from django.contrib import admin

from student_applications import models


class AnswerAdmin(admin.ModelAdmin):
    list_filter = (
        'q13e_slug',
    )
    search_fields = (
        'user__email',
        'user__hebrew_display_name',
        'user__english_display_name',
    )


admin.site.register(models.Answer, AnswerAdmin)
# admin.site.register(models.Cohort)
# admin.site.register(models.Tag)
