# REQUIREMENTS
# ------------
#
#   pip install fabric fabric-virtualenv
#
# DJANGO SETTINGS
# ---------------
#
# get_django_settings() is called at the begginig to get all the
# settings for the django instance and be able to use the following
# information (I put these settings in my local_settings.py):

# import os, datetime
# FABRIC_COLORIZE_ERRORS = True
# FABRIC_SHELL = '/usr/local/bin/bash -l -c'
# FABRIC_USER = 'example'
# FABRIC_HOSTS = ['example.com']
# FABRIC_SQL_DUMP_FILENAME = '%s_%s.sql.gz' % (
#     FABRIC_USER, datetime.date.today().strftime('%Y%m%d'))
# FABRIC_PROJECT = '/home/%(user)s/%(user)s-commute-challenge' % {'user': FABRIC_USER}
# FABRIC_VENV = os.path.join(FABRIC_PROJECT, 'env')
# FABRIC_DB_USER = DATABASES['default']['USER']
# FABRIC_DB_NAME = DATABASES['default']['NAME']
# FABRIC_DB_PASSWORD = DATABASES['default']['PASSWORD']
# FABRIC_DB_PORT = 9999
# FABRIC_DB_HOST = '/tmp'


import os
import json
import datetime
import commands
import logging

from fabric.api import *
from fabvenv import virtualenv


PATH = os.path.realpath(os.path.join(os.path.dirname(__file__)))


def get_django_settings():
    for root, dirs, files in os.walk('.'):
        if 'settings.py' in files:
            settings_path = root[2:].replace('/', '.') + '.settings'
            print 'Using "%s"' % settings_path
            os.environ.setdefault("DJANGO_SETTINGS_MODULE", settings_path)
            break
    settings = commands.getoutput("./manage.py print_settings --format=json")
    # print settings
    env.settings = json.loads(settings)

USE_DJANGO_SETTINGS = True
if USE_DJANGO_SETTINGS:
    get_django_settings()

    for k, v in env.settings.iteritems():
        if k.startswith('FABRIC_'):
            name = k[len('FABRIC_'):].lower()
            setattr(env, name, v)


def deploy():
    # db_dump()
    git_pull()
    run_migrations()
    # run_collectstatic()
    # run_loadflatpages()
    # run_loaddbtemplates()
    restart_uwsgi()


def git_pull():
    with cd(env.project):
        run("git pull")


def restart_uwsgi():
    with cd(env.project):
        run("rm reload.wsgi")
        run("touch reload.wsgi")


def run_django_cmd(cmd):
    with cd(env.project):
        with virtualenv(env.venv):
            run("./manage.py %s" % cmd)


def run_migrations():
    with cd(env.project):
        with virtualenv(env.venv):
            run("./manage.py migrate")


def run_collectstatic():
    with cd(env.project):
        with virtualenv(env.venv):
            run("./manage.py collectstatic --noinput")


def run_loadflatpages():
    with cd(env.project):
        with virtualenv(env.venv):
            run("./manage.py loaddata flatpages")


def run_loaddbtemplates():
    with cd(env.project):
        with virtualenv(env.venv):
            run("./manage.py loaddata dbtemplates")


def db_dump():
    # uses ~/.pgpass to get the password
    # hostname:port:database:username:password
    # you can use wildcards also
    run('pg_dump -h %s -p %s -U %s --no-password %s | gzip > %s' %
        (env.db_host, env.db_port, env.db_user, env.db_name, os.path.join('/tmp', env.sql_dump_filename)))
    get(os.path.join('/tmp', env.sql_dump_filename), env.sql_dump_filename)


def production_settings():
    # I sent a pull request to allow user to specify some variables:
    # https://github.com/django-extensions/django-extensions/pull/488
    with cd(env.project):
        with virtualenv(env.venv):
            run("./manage.py print_settings --format=pprint")


def shell_plus():
    env.output_prefix = False
    with cd(env.project):
        with virtualenv(env.venv):
            run("./manage.py shell_plus")


def createdb():
    local("createdb -U postgres %s" % env.db_name)


def dropdb():
    local("dropdb -U postgres %s" % env.db_name)


# def load_db_data():
#     filename = '%s_%s.sql.gz' % (env.sql_dump_filename, today.strftime('%Y%m%d'))
#     local("psql -U postgres -f %s %s" % (filename, env.db_name))


def create_pgpass():
    # http://docs.fabfile.org/en/latest/api/contrib/files.html
    with open('/tmp/.pgpass', 'w') as fh:
        database = env.settings.DATABASES['default']['NAME']
        username = env.settings.DATABASES['default']['USER']
        password = env.settings.DATABASES['default']['PASSWORD']
        content = "*:*:%s:%s:%s" % (database, username, password)
        fh.write(content)
    put('/tmp/.pgpass', '~/.pgpass')
    run("chmod 600 ~/.pgpass")
