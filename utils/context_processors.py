from django.conf import settings


def hackita_processor(request):
        return {
        'PRODUCTION': not settings.DEBUG,
        'ANALYTICS_ID': getattr(settings, 'GOOGLE_ANALYTICS_ID', None),
    }
