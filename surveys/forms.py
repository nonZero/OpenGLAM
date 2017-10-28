from django import forms

from . import models


class SurveyForm(forms.ModelForm):
    class Meta:
        model = models.Survey
        fields = (
            'email_subject',
            'email_content',
            'q13e',
        )
