from io import StringIO

from fabric.api import *
from fabric.contrib.files import upload_template, uncomment, append, comment

APT_PACKAGES = [
    'unattended-upgrades',
    'ntp',
    'fail2ban',

    'postfix',
    'opendkim',
    'opendkim-tools',

    'supervisor',

    'nginx',

    'git',
    'python',
    'virtualenvwrapper',

    'postgresql',

    'build-essential',
    'python-dev',
    'libpq-dev',
    'libjpeg-dev',
    'libjpeg8',
    'zlib1g-dev',
    'libfreetype6',
    'libfreetype6-dev',
    'libgmp3-dev',

    'htop',

    'rabbitmq-server',  # for offline tasks via celery
]

AUTO_RENEW_SCRIPT = '/home/certbot/auto-renew.sh'


@task
def apt_upgrade():
    run("sudo apt-get update")
    run("sudo apt-get upgrade -y")


@task
def apt_install():
    run("sudo apt-get install -y -q %s" % " ".join(APT_PACKAGES))


@task
def install_new_python():
    sudo("sudo add-apt-repository ppa:jonathonf/python-3.6")
    sudo("apt-get -qq update -y", pty=False)
    sudo("apt-get install -y python3.6 python3.6-dev", pty=False)
    run("which python3.6")
    run("python3.6 --version")


@task
def create_keys():
    run('ssh-keygen')


@task
def show_pubkey():
    run('cat .ssh/id_rsa.pub')


@task
def server_setup():
    apt_upgrade()
    apt_install()
    install_new_python()
    create_keys()
    show_pubkey()
    print("Do not forget to add a github deploy key!")



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

    run('sudo nginx -t')
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
                        }, mode=0o777, use_jinja=True)


@task
def supervisor_setup():
    with cd(env.code_dir):
        upload_template('conf/supervisor.conf.template',
                        env.code_dir + 'conf/supervisor.conf',
                        {
                            'dir': env.code_dir,
                            'webuser': env.webuser,
                            'logdir': env.log_dir,
                        }, mode=0o777, use_jinja=True)

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


@task
def le_create_user():
    run("sudo adduser le --gecos '' --disabled-password")
    print("Now add the following using visudo:")
    print("le ALL=(ALL) NOPASSWD: ALL")


@task
def le_create_scripts():
    put(StringIO(
        '''
#!/bin/bash
cd ~/letsencrypt/
sudo service nginx stop
./letsencrypt-auto certonly --standalone -d oglam.10x.org.il
sudo service nginx start

'''.strip()), "/home/le/renew.sh", use_sudo=True)

    put(StringIO(
        '''
#!/bin/bash
cd ~/letsencrypt/
./letsencrypt-auto certonly -a webroot --agree-tos --renew-by-default --webroot-path=/home/le/webroot -d oglam.10x.org.il
sudo service nginx reload

'''.strip()), "/home/le/auto-renew.sh", use_sudo=True)

    sudo("chown le:le /home/le/renew.sh /home/le/auto-renew.sh")
    sudo("chmod +x /home/le/renew.sh /home/le/auto-renew.sh")


@task
def le_initial_setup():
    run("sudo -iu le git clone https://github.com/letsencrypt/letsencrypt")
    run("sudo -iu le -- bash -c 'cd letsencrypt && ./letsencrypt-auto --help'")


# @task
# def le_renew():
#     run("sudo -iu le -- bash -c './renew.sh'")
#
#
# @task
# def le_auto_renew():
#     run("sudo -iu le -- mkdir -p /home/le/webroot")
#     run("sudo -iu le -- bash -c './auto-renew.sh'")
#
#

@task
def install_certbot():
    # For "Cannot add PPA. Please check that the PPA name or format is correct" error, use:
    # sudo("apt-get install -q --reinstall ca-certificates")
    # Source: https://askubuntu.com/questions/429803/cannot-add-ppa-please-check-that-the-ppa-name-or-format-is-correct

    sudo("add-apt-repository ppa:certbot/certbot")
    sudo("apt-get -qq update", pty=False)
    sudo("apt-get install -q -y certbot", pty=False)

    sudo("adduser certbot --gecos '' --disabled-password")
    upload_template('conf/certbot.ini.template', '/home/certbot/certbot.ini', {
        'host': env.vhost,
    }, use_sudo=True, use_jinja=True, )
    put(StringIO("""#!/bin/bash\ncertbot certonly -c certbot.ini --webroot"""),
        AUTO_RENEW_SCRIPT,
        use_sudo=True, mode=0o775)
    for s in ['webroot', 'conf', 'work', 'logs']:
        sudo('mkdir -p /home/certbot/{}/'.format(s), user='certbot')
    get_cert()
    backup_cert()


@task
def backup_cert():
    get("/home/certbot/conf/", "%(host)s/certbot/%(path)s", use_sudo=True)

    # IMPORTANT NOTES:
    #  - Your account credentials have been saved in your Certbot
    #    configuration directory at /home/certbot/conf. You should make a
    #    secure backup of this folder now. This configuration directory will
    #    also contain certificates and private keys obtained by Certbot so
    #    making regular backups of this folder is ideal.


@task
def get_cert():
    # sudo("service nginx stop")
    # with cd("/home/certbot/"):
    #     sudo("certbot certonly -c certbot.ini --standalone")
    sudo('chown -vR {} {}'.format("certbot", "/home/certbot/"))
    sudo("service nginx reload")
    # sudo("service nginx start")


@task
def renew_cert():
    with cd("/home/certbot/"):
        sudo(AUTO_RENEW_SCRIPT, user='certbot')
    sudo("service nginx reload")


CERTBOT_CRON = """
MAILTO=udioron@gmail.com
0 0 1 FEB,APR,JUN,AUG,OCT,DEC * {}
""".strip()


@task
def setup_certbot_crontab():
    s = CERTBOT_CRON.format(AUTO_RENEW_SCRIPT)
    put(StringIO(s), '/tmp/crontab')
    run('sudo -iu certbot crontab < /tmp/crontab')


def _setup_opendkim(host):
    """Setup opendkim and approve host.
    See https://www.digitalocean.com/community/tutorials/how-to-install-and-configure-dkim-with-postfix-on-debian-wheezy
    """
    with open("conf/opendkim.conf") as f:
        lines = f.read().splitlines()
    append("/etc/opendkim.conf", lines, use_sudo=True)

    append("/etc/default/opendkim", 'SOCKET="inet:12301@localhost"',
           use_sudo=True)

    lines = [
        "milter_protocol = 2",
        "milter_default_action = accept",
        "smtpd_milters = inet:localhost:12301",
        "non_smtpd_milters = inet:localhost:12301",
    ]
    append("/etc/postfix/main.cf", lines, use_sudo=True)

    sudo("mkdir -pv /etc/opendkim/keys")

    lines = [
        "127.0.0.1",
        "localhost",
        host,
    ]
    append("/etc/opendkim/TrustedHosts", lines, use_sudo=True)

    s = "mail._domainkey.{0} {0}:mail:/etc/opendkim/keys/{0}/mail.private".format(
        host)
    append("/etc/opendkim/KeyTable", s, use_sudo=True)

    s = "*@{0} mail._domainkey.{0}".format(host)
    append("/etc/opendkim/SigningTable", s, use_sudo=True)

    d = "/etc/opendkim/keys/{}".format(host)
    sudo('mkdir -pv {}'.format(d))
    with cd(d):
        sudo("opendkim-genkey -s mail -d {}".format(host))
        sudo("chown opendkim:opendkim mail.private")
        s = sudo("cat mail.txt", )

    sudo("service postfix restart")
    sudo("service opendkim restart")

    print(s)


@task
def setup_opendkim():
    _setup_opendkim(env.vhost)


@task
def setup_postfix():
    comment("/etc/postfix/main.cf", "^smtpd_use_tls=yes$", use_sudo=True)
    append("/etc/postfix/main.cf", [
        "smtp_tls_security_level=may",
        "smtpd_tls_security_level=may",
    ], use_sudo=True)
    sudo("service postfix restart")
