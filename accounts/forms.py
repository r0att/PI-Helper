from django import forms
from django.contrib.auth import authenticate
from django.contrib.auth.forms import UserCreationForm

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

        from django.contrib.auth.password_validation import validate_password

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