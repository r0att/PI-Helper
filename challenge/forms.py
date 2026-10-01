from django import forms


class ChallengeStartForm(forms.Form):
    start_digit = forms.IntegerField(
        min_value=1,
        initial=1,
    )
    end_digit = forms.CharField(
        initial="Infinite",
        required=False,
        widget=forms.TextInput,
    )
    hard_mode = forms.BooleanField(
        required=False,
        label="Hard Mode",
    )

    def clean(self):
        cleaned_data = super().clean()

        start_digit = cleaned_data.get("start_digit")
        end_digit = cleaned_data.get("end_digit")

        if end_digit == "Infinite" or end_digit == "":
            cleaned_data["end_digit"] = None
            return cleaned_data

        try:
            end_digit = int(end_digit)
        except ValueError:
            raise forms.ValidationError(
                "End digit must be a number or Infinite."
            )

        if end_digit < 1:
            raise forms.ValidationError(
                "End digit muse be at least 1."
            )

        if start_digit and end_digit and start_digit > end_digit:
            raise forms.ValidationError(
                "Start digit cannot be greater than end digit"
            )

        cleaned_data["end_digit"] = end_digit

        return cleaned_data