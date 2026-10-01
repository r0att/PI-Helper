import uuid

from django.contrib.auth.models import AbstractUser
from django.db.models.signals import post_save
from django.db import models
from django.dispatch import receiver


class User(AbstractUser):
    email = models.EmailField(unique=True)


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)

    description = models.TextField(
        max_length=999,
        blank=True,
    )

    total_games = models.PositiveIntegerField(default=0)
    total_won_games = models.PositiveIntegerField(default=0)
    total_lost_games = models.PositiveIntegerField(default=0)
    total_digits = models.PositiveIntegerField(default=0)

    challenge_total_games = models.PositiveIntegerField(default=0)
    challenge_won_games = models.PositiveIntegerField(default=0)
    challenge_lost_games = models.PositiveIntegerField(default=0)
    challenge_personal_best = models.PositiveIntegerField(default=0)
    challenge_total_digits = models.PositiveIntegerField(default=0)

    hard_mode_total_games = models.PositiveIntegerField(default=0)
    hard_mode_won_games = models.PositiveIntegerField(default=0)
    hard_mode_lost_games = models.PositiveIntegerField(default=0)
    hard_mode_personal_best = models.PositiveIntegerField(default=0)
    hard_mode_total_digits = models.PositiveIntegerField(default=0)

    day_playing_streak = models.PositiveIntegerField(default=0)
    longest_playing_streak = models.PositiveIntegerField(default=0)
    last_playing_date = models.DateField(null=True, blank=True)
    games_today = models.PositiveIntegerField(default=0)

    def __str__(self) -> str:
        return self.user.username


class EmailVerificationToken(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    token = models.UUIDField(default=uuid.uuid4, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return self.user.username


class PasswordChangeToken(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    token = models.UUIDField(default=uuid.uuid4, unique=True)
    new_password_hash = models.CharField(max_length=128)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return self.user.username


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user = instance)