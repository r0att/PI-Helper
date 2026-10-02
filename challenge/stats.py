from datetime import date, timedelta

from accounts.models import Profile, User
from .models import BestTime


def update_challenge_stats(user: User, start_digit, digits_entered: int, won: bool) -> None:
    profile = Profile.objects.get(user=user)

    profile.total_games += 1
    profile.total_digits += digits_entered

    profile.challenge_total_games += 1
    profile.challenge_total_digits += digits_entered

    if won:
        profile.total_won_games += 1
        profile.challenge_won_games += 1
    else:
        profile.total_lost_games += 1
        profile.challenge_lost_games += 1

    if start_digit == 1 and profile.challenge_personal_best < digits_entered:
        profile.challenge_personal_best = digits_entered

    profile.save()

def update_playing_streak(user: User) -> None:
    profile = Profile.objects.get(user=user)
    today = date.today()

    if profile.last_playing_date == today:
        profile.games_today += 1

    elif profile.last_playing_date == today - timedelta(days=1):
        profile.games_today = 1

    else:
        profile.games_today = 1
        profile.day_playing_streak = 0

    if profile.games_today == 2:
        if profile.last_playing_date == today - timedelta(days=1):
            profile.day_playing_streak += 1
        else:
            profile.day_playing_streak = 1

        if profile.day_playing_streak > profile.longest_playing_streak:
            profile.longest_playing_streak = profile.day_playing_streak

    profile.last_playing_date = today
    profile.save()

def update_hard_mode_stats(user: User, start_digit, digits_entered: int, won: bool) -> None:
    profile = Profile.objects.get(user=user)

    profile.total_games += 1
    profile.total_digits += digits_entered

    profile.hard_mode_total_games += 1
    profile.hard_mode_total_digits += digits_entered

    if won:
        profile.total_won_games += 1
        profile.hard_mode_won_games += 1
    else:
        profile.total_lost_games += 1
        profile.hard_mode_lost_games += 1

    if start_digit == 1 and profile.hard_mode_personal_best < digits_entered:
        profile.hard_mode_personal_best = digits_entered

    profile.save()

def update_best_time(user: User, start_digit: int, end_digit: int | None, hard_mode: bool, time_ms: int,) -> None:
    best_time = BestTime.objects.filter(
        user=user,
        start_digit=start_digit,
        end_digit=end_digit,
        hard_mode=hard_mode,
    ).first()

    if best_time is None:
        BestTime.objects.create(
            user=user,
            start_digit=start_digit,
            end_digit=end_digit,
            hard_mode=hard_mode,
            best_time_ms=time_ms,
        )
        return

    if time_ms < best_time.best_time_ms:
        best_time.best_time_ms = time_ms
        best_time.save(update_fields=["best_time_ms"])
