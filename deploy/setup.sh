#!/usr/bin/env bash

set -e

# TODO: Set to URL of git repo.
PROJECT_GIT_URL='https://github.com/thanhttle/profiles-resr-api.git'

PROJECT_BASE_PATH='/usr/local/apps'
VIRTUALENV_BASE_PATH='/usr/local/virtualenvs'

# Set Ubuntu Language
locale-gen en_GB.UTF-8

# Install Python, SQLite and pip
echo "Installing dependencies..."
sudo apt-get update
sudo apt-get install -y python3-dev python3-venv sqlite python-pip supervisor nginx git

sudo mkdir -p $PROJECT_BASE_PATH
sudo git clone $PROJECT_GIT_URL $PROJECT_BASE_PATH/profiles-rest-api

sudo mkdir -p $VIRTUALENV_BASE_PATH
sudo python3 -m venv $VIRTUALENV_BASE_PATH/profiles_api

$VIRTUALENV_BASE_PATH/profiles_api/bin/pip install -r $PROJECT_BASE_PATH/profiles-rest-api/requirements.txt

# Run migrations
cd $PROJECT_BASE_PATH/profiles-rest-api/src

# Setup Supervisor to run our uwsgi process.
sudo cp $PROJECT_BASE_PATH/profiles-rest-api/deploy/supervisor_profiles_api.conf /etc/supervisor/conf.d/profiles_api.conf
sudo supervisorctl reread
sudo supervisorctl update
sudo supervisorctl restart profiles_api

# Setup nginx to make our application accessible.
sudo cp $PROJECT_BASE_PATH/profiles-rest-api/deploy/nginx_profiles_api.conf /etc/nginx/sites-available/profiles_api.conf
sudo rm /etc/nginx/sites-enabled/default
sudo ln -s /etc/nginx/sites-available/profiles_api.conf /etc/nginx/sites-enabled/profiles_api.conf
sudo systemctl restart nginx.service

echo "DONE! :)"
