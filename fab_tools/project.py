from random import choice
from contextlib import contextmanager

from fabric.api import *
from fabric.contrib.files import upload_template


def get_secret_key():
    return ''.join(
        [choice('abcdefghijklmnopqrstuvwxyz0123456789!@#$%^&*(-_=+)') for i in
         range(50)])


@contextmanager
def virtualenv(path):
    with cd(path):
        with prefix(env.venv_command):
            yield


@task
def upgrade_pip():
    with virtualenv(env.code_dir):
        run("pip install --upgrade pip pipenv", pty=False)


@task
def git_log():
    with virtualenv(env.code_dir):
        run("git log -n 1")


@task
def freeze():
    with virtualenv(env.code_dir):
        run("pip freeze")


@task
def reload_app():
    run("sudo kill -HUP `cat %s`" % env.pidfile)


@task
def deploy(restart=True, quick=False):
    with virtualenv(env.code_dir):
        run("git pull", pty=False)
        if not quick:
            run("pip install -r requirements.txt", pty=False)
            run("python manage.py migrate --noinput")
            run("python manage.py update_permissions")
        run("python manage.py collectstatic --noinput")
        run("git log -n 1 --format=\"%ai %h\" > collected-static/version.txt")
        run("git log -n 1 > collected-static/version-full.txt")
    if restart:
        reload_app()


@task
def quickdeploy():
    deploy(True, True)


@task
def clone_project():
    run("git clone %s %s" % (env.clone_url, env.code_dir))


@task
def create_venv():
    run("virtualenv -p python3.6 {} --prompt='({}) '".format(env.venv_dir, env.user))
    upgrade_pip()


@task
def create_local_settings():
    with cd(env.code_dir):
        upload_template(
            'conf/prod_settings_template.py',
            '{}{}/local_settings.py'.format(env.code_dir, env.project),
            {
                'webuser': env.webuser,
                'host': env.vhost,
                'secret_key': get_secret_key()
            },
            use_jinja=True
        )


@task
def rebuild_index():
    """Rebuilds haystack search indexes for project"""
    with virtualenv(env.code_dir):
        run("python manage.py rebuild_index --noinput")
        run("sudo chown -v {} search_db search_db/*".format(env.webuser))


@task
def createsuperuser():
    with virtualenv(env.code_dir):
        run("python manage.py createsuperuser")


@task
def del_pyc():
    with cd(env.code_dir):
        run("find . -name '*.pyc' -delete")


@task
def m(params):
    with virtualenv(env.code_dir):
        run("python manage.py {}".format(params))
