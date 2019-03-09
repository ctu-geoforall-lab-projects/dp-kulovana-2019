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

# copy templates, custom_settings...
