environments = {
    'staging': {
        'hosts': ['songscape-staging.dragonfly.co.nz'],
        'remote_path': '/var/www/django/songscape/',
        'debconf': 'debconf.dat.staging',
        'db_name': 'songscape_dev',
        'db_host': 'pg',
        'db_user': 'songscape',
        'db_port': '5432',
        },
    'production': {
        'hosts': ['songscape.dragonfly.co.nz'],
        'remote_path': '/var/www/django/songscape/',
        'debconf': 'debconf.dat.production',
        'db_name': 'songscape',
        'db_host': 'pg',
        'db_user': 'songscape',
        'db_port': '5432',
        },
    'lxc': {
        'lxc': 'songscape',
        'lxc_template': 'vanilla',
        'remote_path': '/var/www/django/songscape/',
        'debconf': 'debconf.dat.lxc',
        'db_name': 'songscape_dev',
        'db_host': '10.0.3.1',
        'db_user': 'dba',
        'db_port': '5433',
        },

}
