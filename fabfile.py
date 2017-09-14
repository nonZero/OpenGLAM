import os.path

from fab_tools.server import *

from fab_tools.project import *
from fab_tools import dev, db

assert dev
assert db

PROJ_DIR = os.path.abspath(os.path.dirname(__file__))
CONF_DIR = os.path.abspath(os.path.join(PROJ_DIR, 'conf'))

env.project = "oglam"
env.user = "h2"
env.db = "oglam"
env.gunicorn_port = 9099
env.clone_url = "git@github.com:nonZero/OpenGLAM.git"
env.webuser = "webh2"
env.code_dir = '/home/%s/Hackita/' % env.user
env.log_dir = '%slogs/' % env.code_dir
env.venv_dir = '/home/%s/.virtualenvs/h2' % env.user
env.venv_command = '.  %s/bin/activate' % env.venv_dir
env.pidfile = '/home/%s/app.pid' % env.webuser
env.backup_dir = '/home/%s/backups' % env.user


@task
def qa():
    env.instance = 'qa'
    env.vhost = 'h02.10x.org.il'
    env.hosts = [env.vhost]
    env.redirect_host = 'www.%s' % env.vhost


@task
def initial_project_setup():
    create_webuser_and_db()
    clone_project()
    create_venv()
    project_setup()


@task
def project_setup():
    project_mkdirs()
    create_local_settings()
    deploy(restart=False)
    gunicorn_setup()
    supervisor_setup()
    nginx_setup()
