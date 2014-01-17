import os

from fabric.api import *

# Set this before dragonfab imports, because it will then set up logging for you
env.DEBUG=False

env.local_dir = os.path.dirname(__file__)

# This will make all environments available as root fabric commands
from dragonfab.env import *
from dragonfab import deb, database, utils

# TODO: we need to define this for dumping from production
env.databasedump = ''

# Set up your ssh config like this to be able to access production
# ~/.ssh/config
#Host songscape
#  ProxyCommand ssh -q hoiho nc -q0 songscape.local 22
env.use_ssh_config = True

# Package dir specifies where .deb file will go
env.package_dir = os.path.join(env.local_dir, '..')

# This is the name of the deb pacakage that will be built, and where it ends up
env.package_name = 'songscape'

@task
def database_test_setup():
    "Setup database for testing"
    with cd(env.remote_path):
        run("python manage.py test_setup")

@task
def data_refresh():
    "Get the media sorted. In this case we only need to collect static"
    with cd(env.remote_path):
        sudo("python manage.py collectstatic --noinput")


# TESTING
@task
def test():
    with cd(env.remote_path), lcd(env.local_dir):
        put('.coveragerc', '.coveragerc', use_sudo=True)
        sudo('coverage run manage.py test')
        sudo('coverage html --include=www\*')
        sudo('coverage xml --include=www\*')

@task
def fetch_results():
    """ Fetch the test results from the remote server.  """
    with cd(env.remote_path):
        get('nosetests.xml', env.local_dir)
        get('coverage.xml', env.local_dir)
        get('htmlcov', env.local_dir)
