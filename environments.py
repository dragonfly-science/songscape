environments = {
    '__all__': {
        'remote_path': '/var/www/django/songscape/',
        'db_host': 'pg',
        'db_name': 'songscape',
        'db_user': 'songscape',
        'db_port': '5432',
        'dba': 'dba',
    },
    'production': {
        'hosts': ['songscape.dragonfly.co.nz'],
        'debconf': 'debconf.dat.production',
        },
    'staging': {
        'hosts': ['songscape-staging.dragonfly.co.nz'],
        'debconf': 'debconf.dat.staging',
        'db_name': 'songscape_dev',
        },
    'lxc': {
        'lxc': 'songscape',
        'lxc_template': 'vanilla',
        'debconf': 'debconf.dat.lxc',
        'db_name': 'songscape_dev',
        'db_host': '10.0.3.1',
        'db_user': 'dba',
        'db_port': '5433',
        },
    'haast': {
        'hosts': ['haast.dragonfly.co.nz'],
        'db_host': '',
        'db_port': '',
        },
    'development': {
        'hosts': ['127.0.0.1'],
        'db_host': '',
        'db_name': 'songscape_dev',
        'db_user': 'dba',
        'db_port': '5434',
    }

}
