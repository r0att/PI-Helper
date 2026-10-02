from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.password_validation import validate_password

from .models import User, Profile


class RegistrationForm(UserCreationForm):
    email = forms.EmailField()

    class Meta:
        model = User
        fields = ("username", "email", "password1", "password2")


class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ("description",)


class UsernameForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ("username",)


class ChangeEmailForm(forms.Form):
    new_email = forms.EmailField(
        label="New email",
    )

    def __init__(self, user: User, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.user = user

    def clean_new_email(self):
        new_email = self.cleaned_data["new_email"]

        if User.objects.filter(email=new_email).exclude(
            pk=self.user.pk
        ).exists():
            raise forms.ValidationError(
                "This email is already in use."
            )

        return new_email


class ChangePasswordForm(forms.Form):
    current_password = forms.CharField(
        label="Current password",
        widget=forms.PasswordInput,
    )
    new_password = forms.CharField(
        label="New password",
        widget=forms.PasswordInput,
    )
    confirm_password = forms.CharField(
        label="Confirm new password",
        widget=forms.PasswordInput,
    )

    def __init__(self, user: User, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.user = user

    def clean_current_password(self):
        current_password = self.cleaned_data["current_password"]

        if not self.user.check_password(current_password):
            raise forms.ValidationError(
                "Current password is incorrect."
            )

        return current_password

    def clean_new_password(self):
        new_password = self.cleaned_data["new_password"]
        validate_password(new_password, self.user)

        return new_password

    def clean(self):
        cleaned_data = super().clean()

        new_password = cleaned_data.get("new_password")
        confirm_password = cleaned_data.get("confirm_password")

        if (
            new_password
            and confirm_password
            and new_password != confirm_password
        ):
            raise forms.ValidationError(
                "New passwords do not match."
            )

        return cleaned_data


class PasswordResetRequestForm(forms.Form):
    email = forms.EmailField()


class PasswordResetForm(forms.Form):
    new_password = forms.CharField(
        label="New password",
        widget=forms.PasswordInput,
    )
    confirm_password = forms.CharField(
        label="Confirm new password",
        widget=forms.PasswordInput,
    )

    def __init__(self, user: User, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.user = user

    def clean_new_password(self):
        new_password = self.cleaned_data["new_password"]
        validate_password(new_password, self.user)
        return new_password

    def clean(self):
        cleaned_data = super().clean()
        new_password = cleaned_data.get("new_password")
        confirm_password = cleaned_data.get("confirm_password")

        if (
            new_password
            and confirm_password
            and new_password != confirm_password
        ):
            self.add_error(
                "confirm_password",
                "New passwords do not match.",
            )

        return cleaned_data


class ResendVerificationForm(forms.Form):
    username = forms.CharField()
    email = forms.EmailField()
    password = forms.CharField(
        widget=forms.PasswordInput,
    )

    def clean(self):
        cleaned_data = super().clean()

        username = cleaned_data.get("username")
        email = cleaned_data.get("email")
        password = cleaned_data.get("password")

        if not username or not email or not password:
            return cleaned_data

        try:
            user = User.objects.get(
                username=username,
                email=email,
            )
        except User.DoesNotExist:
            raise forms.ValidationError(
                "Invalid account details."
            )

        if user.is_active:
            raise forms.ValidationError(
                "This account is already verified."
            )

        if not user.check_password(password):
            raise forms.ValidationError(
                "Invalid account details."
            )

        self.user = user

        return cleaned_data


class DeleteAccountForm(forms.Form):
    confirmation = forms.CharField(
        label='Type "DELETE"',
    )
    password = forms.CharField(
        label="Password",
        widget=forms.PasswordInput,
    )
    confirm_password = forms.CharField(
        label="Confirm password",
        widget=forms.PasswordInput,
    )

    def __init__(self, user: User, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.user = user

    def clean_confirmation(self):
        confirmation = self.cleaned_data["confirmation"]

        if confirmation != "DELETE":
            raise forms.ValidationError(
                'You must type "DELETE".'
            )

        return confirmation

    def clean_password(self):
        password = self.cleaned_data["password"]

        if not self.user.check_password(password):
            raise forms.ValidationError(
                "Invalid password."
            )

        return password

    def clean(self):
        cleaned_data = super().clean()

        password = cleaned_data.get("password")
        confirm_password = cleaned_data.get("confirm_password")

        if (
            password
            and confirm_password
            and password != confirm_password
        ):
            self.add_error(
                "confirm_password",
                "Passwords do not match."
            )

        return cleaned_data
