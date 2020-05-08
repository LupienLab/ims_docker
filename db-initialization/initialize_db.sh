#!/bin/bash
FILE=/db_backups/initial.sql.txt
if test -f "$FILE"; then
    cat "$FILE" | psql ims_db
else 
    echo "$FILE does not exist"
fi
