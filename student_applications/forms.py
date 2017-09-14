from __future__ import unicode_literals

from django import forms

from . import models
from users.models import UserNote


class ApplicationStatusForm(forms.ModelForm):
    class Meta:
        model = models.Application
        fields = (
            'status',
        )


class ApplicationReviewForm(forms.ModelForm):
    class Meta:
        model = models.ApplicationReview
        fields = (
            'programming_exp',
            'webdev_exp',
            'activism_level',
            'availability',
            'humanism_background',
            'comm_skills',
            'overall_impression',
            'comments',
        )


class DashboardNoteForm(forms.ModelForm):
    class Meta:
        model = UserNote
        fields = (
            'content',
        )
