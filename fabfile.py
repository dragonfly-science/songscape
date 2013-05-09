import os, time

from fabric.api import *
# Set this before dragonfab imports, because it will then set up logging for you
env.DEBUG=False

local_dir = os.path.dirname(__file__)

# This will make all environments available as root fabric commands
from dragonfab.env import *
from dragonfab import deb

# TODO: we need to define this for dumping from production
env.databasedump = ''

# Set up your ssh config like this to be able to access production
# ~/.ssh/config
#Host songscape
#  ProxyCommand ssh -q hoiho nc -q0 scs.tridentsystems.local 22
env.use_ssh_config = True

# Package dir specifies where .deb file will go
env.package_dir = os.path.join(local_dir, '..')

# This is the name of the deb pacakage that will be built, and where it ends up
env.package_name = 'songscape'

@task
def database_dump():
    """Copy of current database from the production server to dumps/latest.sql"""
    with lcd(local_dir):
        local('mkdir -p dumps')
        if os.path.exists('dumps/latest.sql'):
            local('mv dumps/latest.sql dumps/latest.sql.last')
        sudo('mkdir -p /var/backups/dumps/')
        local('echo pg_dump -h %(db_host)s -U %(db_user)s -p %(db_port)s' % env)

        sudo('pg_dump -h %(db_host)s -U %(db_user)s -p %(db_port)s > /var/backups/dumps/latest.sql' % env)
        get('/var/backups/dumps/latest.sql', 'dumps/latest.sql')

@task
def database_push():
    "Recreate database from dumps/latest.sql."
    # TODO refactor this to be more generic (but probably best to wait until using dragonfab)
    # (could also use debconf settings instead of having to add into environments.py)
    sudo('mkdir -p /var/backups/dumps/')
    put('dumps/latest.sql', '/var/backups/dumps/latest.sql', use_sudo=True)
    with settings(warn_only=True):
        run('dropdb -h %(db_host)s -U %(db_user)s -p %(db_port)s %(db_name)s' % env)
    run('createdb -h %(db_host)s -U %(db_user)s -p %(db_port)s -O %(db_user)s %(db_name)s' % env)
    run('psql -h %(db_host)s -U %(db_user)s -p %(db_port)s -d %(db_name)s -f /var/backups/dumps/latest.sql' % env)

@task
def database_migrate():
    "Run south migrations to upgrade database"
    with cd(env.remote_path):
        run("./manage.py syncdb")
        run("./manage.py migrate --list") # Run this to get the state of things first
        run("./manage.py migrate")

@task
def database_test_setup():
    "Setup database for testing"
    with cd(env.remote_path):
        run("python manage.py test_setup")

@task
def apache_restart():
    "Restart apache"
    sudo('sleep 2')
    # http://stackoverflow.com/questions/6379484/fabric-appears-to-start-apache2-but-doesnt
    sudo('service apache2 restart', pty=False)

# TESTING
@task
def test():
    with cd(env.remote_path), lcd(local_dir):
        put('.coveragerc', '.coveragerc', use_sudo=True)
        sudo('coverage run www/manage.py test')
        sudo('coverage html --include=www\*')
        sudo('coverage xml --include=www\*')

@task
def fetch_results():
    """ Fetch the test results from the remote server.  """
    with cd(env.remote_path):
        get('nosetests.xml', local_dir)
        get('coverage.xml', local_dir)
        get('htmlcov', local_dir)
