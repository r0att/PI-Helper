from django.shortcuts import render
from django.http import JsonResponse

from .forms import ChallengeStartForm
from .pi import get_pi_range
from .stats import (
    update_challenge_stats,
    update_playing_streak,
    update_hard_mode_stats,
    update_best_time,
)
from .models import BestTime


def home(request):
    return render(request, "challenge/home.html")

def challenge(request):
    if request.method == "POST":
        form = ChallengeStartForm(request.POST)

        if form.is_valid():
            start_digit = form.cleaned_data["start_digit"]
            end_digit = form.cleaned_data["end_digit"]
            hard_mode = form.cleaned_data["hard_mode"]

            pi_digits = get_pi_range(start_digit, end_digit)

            best_time = None

            if request.user.is_authenticated:
                best_time = BestTime.objects.filter(
                    user=request.user,
                    start_digit=start_digit,
                    end_digit=end_digit,
                    hard_mode=hard_mode,
                ).first()

            if hard_mode:
                template = "challenge/hard_mode.html"
            else:
                template = "challenge/game.html"

            return render(
                request,
                template,
                {
                    "start_digit": start_digit,
                    "end_digit": end_digit,
                    "pi_digits": pi_digits,
                    "hard_mode": hard_mode,
                    "best_time": best_time,
                },
            )

        return render(
            request,
            "challenge/challenge.html",
            {"form": form},
        )

    form = ChallengeStartForm()

    return render(
        request,
        "challenge/challenge.html",
        {"form": form},
    )

def finish_challenge(request):
    if not request.user.is_authenticated:
        return JsonResponse({"error": "Authentication required."}, status=403)

    digits_entered = int(request.POST["digits_entered"])
    start_digit = int(request.POST["start_digit"])
    end_digit = request.POST.get("end_digit")
    won = request.POST["won"] == "true"
    time_ms = int(request.POST["time_ms"])

    if end_digit != "None":
        end_digit = int(end_digit)
    else:
        end_digit = None

    update_challenge_stats(
        request.user,
        start_digit,
        digits_entered,
        won,
    )

    update_playing_streak(request.user)

    if won:
        update_best_time(
            request.user,
            start_digit,
            end_digit,
            False,
            time_ms
        )

    return JsonResponse({"success": True})

def finish_hard_mode(request):
    if not request.user.is_authenticated:
        return JsonResponse({"error": "Authentication required."}, status=403)

    digits_entered = int(request.POST["digits_entered"])
    start_digit = int(request.POST["start_digit"])
    end_digit = request.POST.get("end_digit")
    won = request.POST["won"] == "true"
    time_ms = int(request.POST["time_ms"])

    if end_digit != "None":
        end_digit = int(end_digit)
    else:
        end_digit = None

    update_hard_mode_stats(
        request.user,
        start_digit,
        digits_entered,
        won,
    )

    update_playing_streak(request.user)

    if won:
        update_best_time(
            request.user,
            start_digit,
            end_digit,
            True,
            time_ms
        )

    return JsonResponse({"success": True})