#!/bin/bash

set -e

# set project path, delete if already exists and create a new one
PROJ_PATH=/mnt/home/gislab/project_gislab_web
rm -rf $PROJ_PATH
mkdir $PROJ_PATH

# install necessary packages
sudo apt update
sudo apt install python3.6
sudo apt install python3-pip
sudo apt install python3-venv
python3 -V

# create virtual environment and install django
requirements=`pwd`/requirements.txt

cd $PROJ_PATH
python3.6 -m venv virenv
source virenv/bin/activate
pip install -r $requirements
django-admin --version

# create a sample project
django-admin startproject web_console_project .
python manage.py startapp users

# clone github repository
git clone https://github.com/ctu-geoforall-lab-projects/dp-kulovana-2019.git /tmp/dp-kulovana-2019

# copy files
cp -r /tmp/dp-kulovana-2019/src/templates $PROJ_PATH/templates

cp /tmp/dp-kulovana-2019/src/users/admin.py $PROJ_PATH/users/admin.py
cp /tmp/dp-kulovana-2019/src/users/forms.py $PROJ_PATH/users/forms.py
cp /tmp/dp-kulovana-2019/src/users/models.py $PROJ_PATH/users/models.py
cp /tmp/dp-kulovana-2019/src/users/urls.py $PROJ_PATH/users/urls.py
cp /tmp/dp-kulovana-2019/src/users/views.py $PROJ_PATH/users/views.py
cp -r /tmp/dp-kulovana-2019/src/users/templatetags $PROJ_PATH/users/templatetags

cp /tmp/dp-kulovana-2019/src/project/settings.py $PROJ_PATH/web_console_project/settings.py
cp /tmp/dp-kulovana-2019/src/project/settings_custom.py $PROJ_PATH/web_console_project/settings_custom.py
cp /tmp/dp-kulovana-2019/src/project/urls.py $PROJ_PATH/web_console_project/urls.py
cp /tmp/dp-kulovana-2019/src/project/ldap_auth.py $PROJ_PATH/web_console_project/ldap_auth.py
cp /tmp/dp-kulovana-2019/src/project/ldap_sync.py $PROJ_PATH/web_console_project/ldap_sync.py

# delete github repository
rm -rf /tmp/dp-kulovana-2019

# migrate db
python manage.py makemigrations users
python manage.py migrate
