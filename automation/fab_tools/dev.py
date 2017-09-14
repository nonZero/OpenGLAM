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
    print(cmd)
    # local(cmd)

    build_cmd = "gunzip -c" if filename.endswith('.gz') else "cat"
    cmd = '{} automation/{} | python manage.py dbshell'.format(build_cmd,
                                                               filename)
    print(cmd)
    # local(cmd)


@task
def create_db_user():
    local("createuser -s weboglam")


@task
def create_db():
    local("createdb -O weboglam weboglam")
