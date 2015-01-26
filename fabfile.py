"""Manage a remotely-installed WSGI app on a Unix-like system, with
environment variables controlling a lot of the WSGI app's
functionality (12 Factor style).

All remote access to the app is done via an `invoke` script, which
contains the environment variables, which is created during setup.
Sensitive ones should be passed through fab's env rather than being
put directly into this script. (So this should remain valid for the
lifetime of an open source project. Hostnames, db credentials and the
like do not belong in here. We do have a default username and home
directory, for convenience.)

We create a virtual environment for every release. You probably want
to delete them after a while (but you probably want to delete the
releases as well). This is "better" than sharing a virtualenv, because
of the way pip upgrades packages (otherwise you will get periods where
the app will not work if it needs non-code files or just
previously-unused packages). It is, however, slower.

(Heroku's slug compilation is a better approach. It'd be nice to
detect differences and re-use virtualenvs using symlinking or
copy-and-upgrade in future. However we're not really here to build a
cheap PaaS.)

Getting started:

* with a remote user & host you have access to
$ fab -H HOST setup
$ fab -H host setup:restart=false

* subsequently, to put the latest master live
$ fab -H HOST deploy

* if something goes wrong, roll back to a specific version
$ fab -H switch_to:version=<VERS> restart_appserver

deploy will apply migrations; switch_to will not. Also, migrations are
applied while the site is still running, so should be backwards
compatible.

(deploy also runs compilestatic and compilemessages)

Remote server layout (setup makes these):

archives            tgz archives of code versions
releases            unpacked, versioned by datetime of fabric invocation
releases/current    symlink to current version
releases/previous   symlink to previous version
releases/next       symlink to version being upgraded to
releases/<>/ENV     virtualenv per release
userv/rc            userv script for starting app server
invoke              environment-setting invocation script (acts both
                    as an init.d script and a way of invoking app tasks
                    such as migration, compilestatic
"""

from fabric.api import *
from fabric.contrib.files import exists
import os
import tempfile
import time

import fabhelpers


env.remote = 'git@github.com:jaylett/kallisto.git'
env.branch = 'master'
env.project = 'kallisto'

env.user = 'kallisto'
env.path = '/home/%s' % env.user


def deploy(restart='true'):
    """
    Deploy the latest version of the site to the servers.
    """
    
    restart = (restart in ('true', 'True'))

    # installs any required third party modules, compiles static files
    # and messages, migrates the database and then restarts the
    # appserver
    
    env.release = time.strftime('%Y-%m-%dT%H.%M.%S')

    fabhelpers.export_and_upload_tar_from_git_local() # github doesn't support upload-archive
    prep_release(env.release)
    switch_to(env.release)
    if restart:
        restart_appserver()
    else:
        invoke(command="start")

    
def switch_to(version):
    """Switch the current (ie live) version."""
    
    require('hosts')

    previous_path = os.path.join(env.path, 'releases', 'previous')
    current_path = os.path.join(env.path, 'releases', 'current')
    if exists(previous_path):
        run('rm %s' % previous_path)
    if exists(current_path):
        run('mv %s %s' % (current_path, previous_path))
    # ln -s doesn't actually take a path relative to cwd as its first
    # argument; it's actually relative to its second argument
    run('ln -s %s %s' % (version, current_path))
    # tidy up the next marker if there was one
    run('rm -f %s' % os.path.join(env.path, 'releases', 'next'))
    
    env.release = version # in case anything else wants to use it after us

    
def prep_release(version):
    """Compile static, make messages and migrate."""

    require('hosts')
    
    next_path = os.path.join(env.path, 'releases', 'next')
    if exists(next_path):
        run('rm %s' % next_path)
    run('ln -s %s %s' % (version, next_path))

    run(
        "cd %(path)s/releases/next; "
        "virtualenv ENV; "
        "ENV/bin/pip install -r requirements/live.txt" % {
            'path': env.path,
            'release': env.release
        }
    )

    run('invoke prep')
    # leave the next marker (symlink) in place in case something
    # goes wrong before the end of switch_to, since it will provide
    # useful state on the remote machine


def app_shell():
    """Get an app shell on the current release."""

    require('hosts')

    run("invoke shell")


def restart_appserver():
    """Restart the (gunicorn) app server."""

    require('hosts')
    
    run("invoke restart")


def invoke(command):
    """Run an init command (or shell or prep) via the invoker."""
    
    require('hosts')
    
    run("invoke %s" % command)

    
def setup():
    """Set up the initial structure for the given user."""
    
    require('hosts', 'path')
    require(
        'database_url',
        'django_secret_key',
        'allowed_hosts',
        'listen_port',
        used_for="configuring the application.",
    )

    # make our directory structure
    run("mkdir -m 711 %s/releases" % env.path)
    run("mkdir -m 700 %s/archives" % env.path)
    # make the userv rc script
    run("mkdir -m 700 %s/.userv" % env.path)
    put("userv.rc.in", "%s/.userv/rc" % env.path, mode=0600)
    # and the script it points to
    # @TOPDIR@ -> env.path
    # @WSGI@ -> $(env.project).wsgi (python path to WSGI app)
    # @DATABASE_URL@ -> syntax postgresql://USER:PASSWORD@localhost:5432/DBNAME
    # (or postgis://...)
    # @DJANGO_SECRET_KEY@ -> what it says (make it long and gnarly)
    # @ALLOWED_HOSTS@ -> semicolon separated (eg loose-end.in;www.loose-end.in)
    # @PORT@ -> that gunicorn should listen on
    #
    # The last four should be passed into the env in a fab-ish manner.
    # (Hence the require statements above.)

    substitutions = (
        ('TOPDIR', env.path),
        ('WSGI', '%s.wsgi' % env.project),
        ('DATABASE_URL', env.database_url),
        ('DJANGO_SECRET_KEY', env.django_secret_key),
        ('ALLOWED_HOSTS', env.allowed_hosts),
        ('PORT', env.listen_port),
    )

    tmpfile = tempfile.NamedTemporaryFile(delete=False)
    commands = '; '.join(
        "s/@%(var)s@/%(subst)s/g; " % {
            'var': k,
            'subst': v.replace("'", r"\'").replace("/", r"\/"),
        } for k, v in substitutions
    )
    try:
        local(
            "sed < invoke.in > %(tmp_fname)s '%(commands)s'" % {
                'tmp_fname': tmpfile.name,
                'commands': commands,
            }
        )
        put(tmpfile.name, "%s/invoke" % env.path, mode=0700)
    finally:
        os.remove(tmpfile.name)
