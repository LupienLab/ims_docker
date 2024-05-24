#!/bin/bash
##BACKUP the database
FOLDER="/home/anand/duncan/db_backups/"
now_local=`date +'%Y-%m-%d'`
now_s3=`date +'%Y/%m/%d'`
rm $FOLDER/*.lupien.ims.sql.txt
SQLFILE=$FOLDER/${now_local}.lupien.ims.sql.txt
docker exec -u postgres docker-db-1 pg_dump -F p ims_db > $SQLFILE
