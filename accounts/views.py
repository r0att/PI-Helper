import uuid

from datetime import timedelta

from django.contrib.auth.decorators import login_required
from django.contrib.auth.hashers import make_password
from django.contrib.auth import authenticate, login, logout
from django.core.mail import send_mail
from django.shortcuts import render, redirect
from django.urls import reverse
from django.http import JsonResponse
from django.utils import timezone

from .forms import (
    RegistrationForm,
    ProfileForm,
    UsernameForm,
    ChangePasswordForm,
    ChangeEmailForm,
    ResendVerificationForm,
)
from .models import (
    EmailChangeToken,
    EmailVerificationToken,
    PasswordChangeToken,
    User,
)

def register(request):
    if request.method == "POST":
        form = RegistrationForm(request.POST)

        if form.is_valid():
            print("FORM VALID")

            user = form.save(commit=False)
            user.is_active = False
            user.save()

            verification_token = EmailVerificationToken.objects.create(user=user)

            verification_url = request.build_absolute_uri(
                reverse("verify_email", args=[verification_token.token])
            )

            send_mail(
                "Verify your PI Helper account",
                f"Click the link to verify your email:\n\n{verification_url}",
                None,
                [user.email],
            )

    else:
        form = RegistrationForm()

    return render(request, "accounts/register.html", {"form": form})

def resend_verification(request):
    if request.method == "POST":
        form = ResendVerificationForm(request.POST)

        if form.is_valid():
            user = form.user
            verification_token = EmailVerificationToken.objects.get(
                user=user
            )

            now = timezone.now()

            if now - verification_token.send_window_started_at >= timedelta(
                hours=1
            ):
                verification_token.send_count = 1
                verification_token.send_window_started_at = now
            else:
                if now - verification_token.last_sent_at < timedelta(
                    minutes=2,
                ):
                    form.add_error(
                        "email",
                        "You can request another email in less than 2 minutes.",
                    )

                    return render(
                        request,
                        "accounts/resend_verification.html",
                        {"form": form},
                    )
                
                if verification_token.send_count >= 5:
                    form.add_error(
                        None,
                        "You have reached the email limit. Try again later.",
                    )

                    return render(
                        request,
                        "accounts/resend_verification.html",
                        {"form": form},
                    )

                verification_token.send_count += 1
                
            verification_token.token = uuid.uuid4()
            verification_token.last_sent_at = now
            verification_token.save()

            verification_url = request.build_absolute_uri(
                reverse(
                    "verify_email",
                    args=[verification_token.token],
                )
            )

            send_mail(
                "Verify your email - PI Helper",
                (
                    "Click the link below to verify your email:\n\n"
                    f"{verification_url}"
                ),
                None,
                [user.email],
            )

            return render(
                request,
                "accounts/resend_verification_sent.html",
            )

    else:
        form = ResendVerificationForm()

    return render(
        request,
        "accounts/resend_verification.html",
        {"form": form},
    )

def login_view(request):
    if request.method == "POST":
        username = request.POST["username"]
        password = request.POST["password"]

        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            try:
                user = User.objects.get(email=username)
            except User.DoesNotExist:
                user = None

        if user is not None:
            if not user.is_active:
                return render(
                    request,
                    "accounts/login.html",
                    {
                        "error": "Your account must be activated before logging in."
                    },
                )

            if user.check_password(password):
                login(request, user)
                return redirect("home")

        return render(
            request,
            "accounts/login.html",
            {
                "error": "Invalid username or password."
            },
        )

    return render(request, "accounts/login.html")

def logout_view(request):
    logout(request)

    return redirect("login")

def verify_email(request, token):
    verification_token = EmailVerificationToken.objects.filter(
        token=token
    ).first()

    if verification_token is None:
        return render(request, "accounts/verification_failed.html")

    user = verification_token.user
    user.is_active = True
    user.save()

    verification_token.delete()

    return render(request, "accounts/verification_success.html")

@login_required
def profile(request):
    profile = request.user.profile

    if request.method == "POST":
        profile_form = ProfileForm(
            request.POST,
            instance=profile,
        )
        username_form = UsernameForm(
            request.POST,
            instance=request.user,
        )

        if profile_form.is_valid() and username_form.is_valid():
            profile_form.save()
            username_form.save()

            return redirect("profile")
    else:
        profile_form = ProfileForm(instance=profile)
        username_form = UsernameForm(instance=request.user)

    return render(
        request,
        "accounts/profile.html",
        {
            "profile": profile,
            "profile_form": profile_form,
            "username_form": username_form,
        },
    )

@login_required
def check_username(request):
    username = request.GET.get("username", "").strip()

    if not username:
        return JsonResponse({"available": False})

    username_exists = User.objects.filter(
        username=username
    ).exclude(
        pk=request.user.pk
    ).exists()

    return JsonResponse(
        {"available": not username_exists}
    )

def check_registration_username(request):
    username = request.GET.get("username", "").strip()

    if not username:
        return JsonResponse({"available": False})

    username_exists = User.objects.filter(
        username=username
    ).exists()

    return JsonResponse(
        {"available": not username_exists}
    )

@login_required
def change_email(request):
    if request.method == "POST":
        form = ChangeEmailForm(request.user, request.POST)

        if form.is_valid():
            EmailChangeToken.objects.filter(
                user=request.user
            ).delete()

            email_token = EmailChangeToken.objects.create(
                user=request.user,
                new_email=form.cleaned_data["new_email"],
            )

            verification_url = request.build_absolute_uri(
                reverse(
                    "confirm_email_change",
                    args=[email_token.token],
                )
            )

            send_mail(
                "Confirm email change - PI Helper",
                (
                    "Click the link below to confirm your email change:\n\n"
                    f"{verification_url}"
                ),
                None,
                [email_token.new_email],
            )

            return render(
                request,
                "accounts/email_change_sent.html",
            )

    else:
        form = ChangeEmailForm(request.user)

    return render(
        request,
        "accounts/change_email.html",
        {"form": form},
    )

def confirm_email_change(request, token):
    try:
        email_token = EmailChangeToken.objects.get(
            token=token
        )
    except EmailChangeToken.DoesNotExist:
        return render(
            request,
            "accounts/email_change_invalid.html",
        )

    user = email_token.user
    user.email = email_token.new_email
    user.save(update_fields=["email"])

    email_token.delete()

    return render(
        request,
        "accounts/email_change_success.html"
    )

@login_required
def change_password(request):
    if request.method == "POST":
        form = ChangePasswordForm(request.user, request.POST)

        if form.is_valid():
            PasswordChangeToken.objects.filter(
                user=request.user
            ).delete()

            password_token = PasswordChangeToken.objects.create(
                user=request.user,
                new_password_hash=make_password(
                    form.cleaned_data["new_password"]
                ),
            )

            verification_url = request.build_absolute_uri(
                reverse(
                    "confirm_password_change",
                    args=[password_token.token],
                )
            )

            send_mail(
                "Confirm password change - PI Helper",
                (
                    "Click the link below to confirm your password change:\n\n"
                    f"{verification_url}"
                ),
                None,
                [request.user.email],
            )

            return render(
                request,
                "accounts/password_change_sent.html",
            )

    else:
        form = ChangePasswordForm(request.user)

    return render(
        request,
        "accounts/change_password.html",
        {"form": form},
    )

@login_required
def confirm_password_change(request, token):
    try:
        password_token = PasswordChangeToken.objects.get(token=token)
    except PasswordChangeToken.DoesNotExist:
        return render(
            request,
            "accounts/password_change_invalid.html",
        )

    user = password_token.user
    user.password = password_token.new_password_hash
    user.save(update_fields=["password"])

    password_token.delete()

    return render(
        request,
        "accounts/password_change_success.html",
    )