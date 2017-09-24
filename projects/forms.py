from django.utils.translation import ugettext_lazy as _
from django import forms

from . import models


class ProjectForm(forms.ModelForm):
    class Meta:
        model = models.Project
        fields = (
            'title',
            'slug',
            'is_published',
            'summary_markdown',
            'link',
            'picture',
        )


class ProjectVoteForm(forms.ModelForm):
    class Meta:
        model = models.ProjectVote
        fields = (
            'score',
        )
        widgets = {
            'score': forms.RadioSelect(),
        }


class ProjectCommentForm(forms.ModelForm):
    class Meta:
        model = models.ProjectComment
        fields = (
            # 'in_reply_to',
            'scope',
            'content',
        )
        # widgets = {
        #     'in_reply_to': forms.HiddenInput(),
        # }


class ProjectCommentEditForm(forms.ModelForm):
    class Meta:
        model = models.ProjectComment
        fields = (
            # 'in_reply_to',
            'is_published',
            'scope',
            'content',
        )
