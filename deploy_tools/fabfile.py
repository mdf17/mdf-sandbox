from fabric.contrib.files import append, exists, sed
from fabric.api import env, local, run
import random

REPO_URL = 'https://github.com/mdf17/mdf-sandbox.git'  

def deploy():
    site_folder = '/home/'+ env.user + '/sites/' + env.host   
    source_folder = site_folder + '/source'
    _create_directory_structure_if_necessary(site_folder)
    _get_latest_source(source_folder)
    _update_settings(source_folder, env.host)  
    _update_virtualenv(source_folder)
    _update_static_files(source_folder)
    _update_database(source_folder)

def _create_directory_structure_if_necessary(site_folder):
    for subfolder in ('database', 'static', 'virtualenv', 'source'):
        command = 'mkdir -p ' + site_folder + '/' + subfolder;
        run(command)

def _get_latest_source(source_folder):
    if exists(source_folder + '/.git'):
        command =  'cd ' + source_folder + ' && git fetch'
        run(command)
    else:
        command = 'git clone ' + REPO_URL + ' ' + source_folder
        run(command)
    current_commit = local("git log -n 1 --format=%H", capture=True)
    command = 'cd ' + source_folder + ' && git reset --hard ' + current_commit
    run(command)

def _update_settings(source_folder, site_name):
    settings_path = source_folder + '/test_project/settings.py'
    sed(settings_path, "DEBUG = True", "DEBUG = False")
    allowed_hosts_site_name = 'ALLOWED_HOSTS = ["' + site_name + '"]'
    sed(settings_path,
        'ALLOWED_HOSTS = .+$',
        allowed_hosts_site_name
    )
    secret_key_file = source_folder + '/test_project/secret_key.py'
    if not exists(secret_key_file):
        chars = 'abcdefghijklmnopqrstuvwxyz0123456789!@#$%^&*(-_=+)'
        key = ''.join(random.SystemRandom().choice(chars) for _ in range(50))
        secret_key_string = 'SECRET_KEY = "' + key + '"'
        append(secret_key_file, secret_key_string)
    append(settings_path, '\nfrom .secret_key import SECRET_KEY')

def _update_virtualenv(source_folder):
    virtualenv_folder = source_folder + '/../virtualenv'
    if not exists(virtualenv_folder + '/bin/pip'):
        command = 'python3.5 -m venv ' + virtualenv_folder
        run(command)
    command = virtualenv_folder + '/bin/pip install -r ' + source_folder + '/requirements.txt'
    run(command)

def _update_static_files(source_folder):
    command = 'cd ' + source_folder + ' && ../virtualenv/bin/python manage.py collectstatic --noinput'
    run(command)

def _update_database(source_folder):
    command = 'cd ' + source_folder + ' && ../virtualenv/bin/python manage.py migrate --noinput'
    run(command)
