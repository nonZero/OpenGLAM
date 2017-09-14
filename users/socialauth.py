from pprint import pprint

from django.core.mail import mail_managers


def create_user(strategy, details, user=None, *args, **kwargs):
    if user:
        return {'is_new': False}

    return {
        'is_new': True,
        'user': strategy.create_user(email=details['email'])
    }


def notify_managers(backend, details, user=None, *args, is_new=False,
                    **kwargs):
    if not is_new:
        return

    title = "New {} User: {}".format(backend.name, user.email)
    mail_managers(title, title)


def debug(response, details, *args, pipeline_index, **kwargs):
    print(str(pipeline_index).center(20, "="))
    pprint(response)
    print('-' * 80)
    pprint(details)
    print('-' * 80)
    pprint(args)
    print('-' * 80)
    pprint(kwargs)
    print('=' * 80)
