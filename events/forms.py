from django import forms

from events import models


class EventInvitationForm(forms.ModelForm):
    class Meta:
        model = models.EventInvitation
        fields = (
            'status',
            'note',
            'attendance',
        )
