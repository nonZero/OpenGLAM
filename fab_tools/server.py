from fabric.api import *
from fabric import operations
from fabric.contrib.files import upload_template, uncomment

APT_PACKAGES = [
    'postgresql',
    'nginx',
    'supervisor',
    'python',
    'virtualenvwrapper',
    'git',
    'python-dev',
    'libpq-dev',
    'libjpeg-dev',
    'libjpeg8',
    'zlib1g-dev',
    'libfreetype6',
    'libfreetype6-dev',
    'postfix',
    'fail2ban',
    'postgis',
    'postgresql-9.3-postgis-2.1',
    'htop',
]


@task
def server_setup():
    run("sudo apt-get update")
    run("sudo apt-get upgrade -y")
    run("sudo apt-get install -y %s" % " ".join(APT_PACKAGES))


@task
def host_type():
    run('uname -s')


@task
def hard_reload():
    run("sudo supervisorctl restart %s" % env.webuser)


@task
def very_hard_reload():
    run("sudo service supervisor stop")
    run("sudo service supervisor start")


@task
def log(n=50):
    run("tail -n{} {}*".format(n, env.log_dir))


@task
def create_webuser_and_db():
    run("sudo adduser %s --gecos '' --disabled-password" % env.webuser)
    run("sudo -iu postgres createuser %s -S -D -R" % env.webuser)
    run("sudo -iu postgres createdb %s -O %s" % (env.webuser, env.webuser))
    run("sudo -iu postgres psql -c \"alter user %s with password '%s';\"" % (
        env.webuser, env.webuser))
    enable_postgis()


@task
def enable_postgis():
    run(
        "sudo -iu postgres psql %s -c \"CREATE EXTENSION postgis;\"" % env.webuser)
    run(
        "sudo -iu postgres psql %s -c \"CREATE EXTENSION postgis_topology;\"" % env.webuser)


@task
def nginx_setup():
    nginx_conf1 = '/etc/nginx/sites-available/%s.conf' % env.webuser
    nginx_conf2 = '/etc/nginx/sites-enabled/%s.conf' % env.webuser

    with cd(env.code_dir):
        upload_template('conf/nginx.conf.template',
                        env.code_dir + 'conf/nginx.conf',
                        {
                            'host': env.vhost,
                            'redirect_host': env.redirect_host,
                            'dir': env.code_dir,
                            'port': env.gunicorn_port,
                        }, use_jinja=True)

    uncomment('/etc/nginx/nginx.conf',
              'server_names_hash_bucket_size\s+64',
              use_sudo=True)

    run('sudo rm -f /etc/nginx/sites-enabled/default')

    run('sudo ln -fs %sconf/nginx.conf %s' % (env.code_dir, nginx_conf1))
    run('sudo ln -fs %s %s' % (nginx_conf1, nginx_conf2))
    run('sudo service nginx configtest')
    run('sudo service nginx start')
    run('sudo service nginx reload')


@task
def gunicorn_setup():
    with cd(env.code_dir):
        upload_template('conf/server.sh.template',
                        env.code_dir + 'server.sh',
                        {
                            'venv': env.venv_dir,
                            'port': env.gunicorn_port,
                            'pidfile': env.pidfile,
                        }, mode=0777, use_jinja=True)


@task
def supervisor_setup():
    with cd(env.code_dir):
        upload_template('conf/supervisor.conf.template',
                        env.code_dir + 'conf/supervisor.conf',
                        {
                            'dir': env.code_dir,
                            'webuser': env.webuser,
                            'logdir': env.log_dir,
                        }, mode=0777, use_jinja=True)

        run(
            'sudo ln -fs %sconf/supervisor.conf /etc/supervisor/conf.d/%s.conf'
            % (env.code_dir, env.webuser))
        run("sudo supervisorctl reread")
        run("sudo supervisorctl update")
        # run("sudo supervisorctl start %s" % env.webuser)


@task
def project_mkdirs():
    """Creates empty directories for logs, uploads and search indexes"""
    with cd(env.code_dir):
        run('mkdir -pv %s' % env.log_dir)

        dirs = 'uploads'
        run('mkdir -pv {}'.format(dirs))
        run('sudo chown -v {} {}'.format(env.webuser, dirs))


@task
def status():
    run("sudo supervisorctl status")
