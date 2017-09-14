from __future__ import unicode_literals

import copy
from authtools.admin import UserAdmin as UA
from django.contrib import admin

from users import models


class PersonalInfoInline(admin.StackedInline):
    model = models.PersonalInfo


class UserAdmin(UA):
    list_display = (
        'email',
        'hebrew_display_name',
        'english_display_name',
        'is_active',
        'community_member',
        'team_member',
        'is_staff',
        'is_superuser',
        'last_login',
    )

    fieldsets = copy.deepcopy(UA.fieldsets)
    fieldsets[0][1]['fields'] = fieldsets[0][1]['fields'] + (
        'hebrew_display_name',
        'english_display_name',
        'team_member',
        'community_member',
        'community_name',
        'community_email',
        'community_contact_phone',
    )

    inlines = (
        PersonalInfoInline,
    )

    date_hierarchy = "last_login"

    list_filter = (
        'is_superuser',
        'is_staff',
        'team_member',
        'community_member',
        'is_active',
    )


class UserNoteAdmin(admin.ModelAdmin):
    search_fields = (
        'user__email',
        'user__hebrew_display_name',
        'user__english_display_name',
    )


admin.site.register(models.User, UserAdmin)
admin.site.register(models.UserNote, UserNoteAdmin)
admin.site.register(models.Tag)
