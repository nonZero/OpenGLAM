import datetime

from fabric import operations
from fabric.api import *


@task
def backup_db():
    now = datetime.datetime.now()
    filename = now.strftime(
        "{}-{}-%Y-%m-%d-%H-%M.sql.gz".format(env.project, env.instance))
    run('mkdir -p {}'.format(env.backup_dir))
    fullpath = env.backup_dir + '/' + filename
    run('sudo -u postgres pg_dump {} | gzip > {}'.format(env.webuser,
                                                         fullpath))
    operations.get(fullpath)
