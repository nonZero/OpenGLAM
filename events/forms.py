from django import forms

from . import models


class EventForm(forms.ModelForm):
    class Meta:
        model = models.Event
        fields = (
            'title',
            'slug',
            'is_active',
            'is_open',
            'starts_at',
            'ends_at',
            'registration_ends_at',
            'location',
            'description',
        )


class EventInvitationForm(forms.ModelForm):
    class Meta:
        model = models.EventInvitation
        fields = (
            'status',
            'note',
            'attendance',
        )
