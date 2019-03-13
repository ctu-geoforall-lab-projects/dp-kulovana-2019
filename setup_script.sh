#!/bin/bash

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
cd $PROJ_PATH
python3.6 -m venv virenv
source virenv/bin/activate
pip install django==2.1.7
django-admin --version

#install ldap
pip install django_python3_ldap

# create a sample project
django-admin startproject web_console_project .
python manage.py startapp users

# clone github respository
git clone https://github.com/ctu-geoforall-lab-projects/dp-kulovana-2019.git $PROJ_PATH/dp-kulovana-2019 

# copy files
cp -r $PROJ_PATH/dp-kulovana-2019/src/templates $PROJ_PATH/templates

cp $PROJ_PATH/dp-kulovana-2019/src/users/admin.py $PROJ_PATH/users/admin.py
cp $PROJ_PATH/dp-kulovana-2019/src/users/forms.py $PROJ_PATH/users/forms.py
cp $PROJ_PATH/dp-kulovana-2019/src/users/models.py $PROJ_PATH/users/models.py
cp $PROJ_PATH/dp-kulovana-2019/src/users/urls.py $PROJ_PATH/users/urls.py
cp $PROJ_PATH/dp-kulovana-2019/src/users/views.py $PROJ_PATH/users/views.py

cp $PROJ_PATH/dp-kulovana-2019/src/project/settings.py $PROJ_PATH/web_console_project/settings.py
cp $PROJ_PATH/dp-kulovana-2019/src/project/settings_custom.py $PROJ_PATH/web_console_project/settings_custom.py
cp $PROJ_PATH/dp-kulovana-2019/src/project/urls.py $PROJ_PATH/web_console_project/urls.py

# migrate db
python manage.py makemigrations users
python manage.py migrate
