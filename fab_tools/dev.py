import os.path

from fabric.api import *
from fabric.contrib.console import confirm


@task
def load_db_from_file(filename):
    if not os.path.isfile(filename):
        abort("Unknown file {}".format(filename))

    if not confirm(
            "DELETE local db and load from backup file {}?".format(filename)):
        abort("Aborted.")

    drop_command = "drop schema public cascade; create schema public;"
    cmd = '''python -c "print('{}')" | python manage.py dbshell'''.format(
        drop_command, filename)
    local(cmd)

    cmd = "gunzip -c" if filename.endswith('.gz') else "cat"
    cmd = '{} {} | python manage.py dbshell'.format(cmd, filename)
    local(cmd)

@task
def load_latest_db_from_file():
    load_db_from_file(f"{env.host}/latest.sql.gz")


@task
def create_db_user():
    local("createuser -s {}".format(env.db))


@task
def create_db():
    local("createdb -O {0} {0}".format(env.db))
