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


PRODUCTION_PORT=5050
DEVELOPMENT_PORT=8000

##############################################
## Make sure that certain environment
## variables exist
if [ -z "$DB_NAME"  ] || [ -z "$DB_USER" ]|| \
   [ -z "$DB_PORT" ] || [ -z "$DB_HOST" ];
then
   echo Error: Could not find the DB_* envrionment variables
   exit 1
fi


##############################################
## Make sure that postgres server is up
## and running

while ! nc -w 1 -z "$DB_HOST" "$DB_PORT";
do
   sleep 0.1;
done;

###############################################

# Run migrations
echo "Running migrations..."
python3 manage.py makemigrations
python3 manage.py migrate --fake-initial

# Graceful shutdown handling
trap 'exit' INT TERM
trap 'kill 0' EXIT

if [ $DEVELOPMENT ];
then
  echo "Running local development server on port $DEVELOPMENT_PORT..."
  python3 manage.py runserver 0.0.0.0:${DEVELOPMENT_PORT}
elif [ $PRODUCTION ];
then
  echo "Running production server on port $PRODUCTION_PORT..."
  python3 manage.py collectstatic --noinput
  gunicorn ims.wsgi -t 120 -b 0.0.0.0:${PRODUCTION_PORT}
else
  echo Unknown run mode!
  exit 1
fi
