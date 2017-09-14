#!/bin/bash
cd $1 && django-admin makemessages -l he --no-location && xdg-open locale/he/LC_MESSAGES/django.po

