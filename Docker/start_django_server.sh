#!/bin/bash
set -e

#############################################
## This scripts runs in the machine running
## django. The environment variables are
## passed from docker-compose or docker files
##############################################

##############################################
### Varaible Definitions  ####################

# Note that these ports are used by gunicorn or manage.py
# nginx directs them to the ultimate webserver port
# which is 80 or 8080


PRODUCTION_PORT=8080
DEVELOPMENT_PORT=8000

##############################################
## Make sure that certain environment
## variables exist
if [ ! $DB_NAME  ] || [ ! $DB_USER ]|| \
   [ ! $DB_PORT ] || [ ! $DB_PORT ];
then
   echo Error: Could not find the DB_* envrionment variables
   exit 1
fi


##############################################
## Make sure that postgres server is up
## and running

while ! nc -w 1 -z db 5432;
do
   sleep 0.1;
done;

###############################################

python3 manage.py makemigrations
python3 manage.py migrate --fake-initial

if [ $DEVELOPMENT ];
then
   echo Running local development server...
   python3 manage.py runserver 0.0.0.0:${DEVELOPMENT_PORT}
elif [ $PRODUCTION ];
then
   echo Running production...
   python3 manage.py collectstatic --noinput
   gunicorn ims.wsgi -t 120 -b 0.0.0.0:${PRODUCTION_PORT}
else
   echo Unknown run mode!
fi