# -*- coding: utf-8 -*-
# Generated by Django 1.11.5 on 2017-09-14 22:03
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('events', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='eventinvitation',
            name='created_by',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='event_invitations_created', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='eventinvitation',
            name='event',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='invitations', to='events.Event'),
        ),
        migrations.AddField(
            model_name='eventinvitation',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='invitations', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='event',
            name='created_by',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='events_created', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterUniqueTogether(
            name='eventinvitation',
            unique_together=set([('event', 'user')]),
        ),
    ]
