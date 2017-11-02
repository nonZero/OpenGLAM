import datetime
from pathlib import Path

from fabric import operations
from fabric.api import *


def make_backup():
    now = datetime.datetime.now()
    filename = now.strftime(
        "{}-{}-%Y-%m-%d-%H-%M.sql.gz".format(env.project, env.instance))
    run('mkdir -p {}'.format(env.backup_dir))
    fullpath = env.backup_dir + '/' + filename
    run('sudo -u postgres pg_dump {} | gzip > {}'.format(env.webuser,
                                                         fullpath))
    return fullpath


@task
def remote_backup_db():
    path = make_backup()
    operations.get(path)
    run('ls -alh {}'.format(path))


@task
def backup_db():
    files = operations.get(make_backup())
    if len(files) != 1:
        print("no file downloaded!")
        return

    latest = "latest.sql.gz"
    target = Path(files[0])
    local(f"cd {target.parent} && ln -fs {target} {latest}")
    print(f"link created to: {target.parent / latest}")
