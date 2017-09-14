import django.core.mail.message
import email.charset


def fix_django_mail_encoding():
    django.core.mail.message.utf8_charset.body_encoding = email.charset.BASE64


def send_html_mail(subject, html_message, email):
    alts = [(html_message, 'text/html')]

    m = django.core.mail.message.EmailMultiAlternatives(subject, to=[email],
                                                        alternatives=alts)
    return m.send()
