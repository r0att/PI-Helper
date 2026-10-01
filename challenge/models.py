from django.conf import settings
from django.db import models


class BestTime(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
    )

    start_digit = models.PositiveIntegerField()
    end_digit = models.PositiveIntegerField(
        null=True,
        blank=True,
    )

    hard_mode = models.BooleanField(default=False)

    best_time_ms = models.PositiveBigIntegerField()

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=("user", "start_digit", "end_digit", "hard_mode"),
                name="unique_best_time_range",
            ),
        ]

    def __str__(self) -> str:
        mode = "Hard Mode" if self.hard_mode else "Challenge"
        return f"{self.user.username} - {mode} - {self.start_digit}-{self.end_digit}"