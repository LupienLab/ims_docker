#!/bin/bash
##BACKUP the database
# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Navigate two levels up from script directory
BACKUP_DIR="$(cd "$SCRIPT_DIR/../.." && pwd)/db_backups"

# Create backup folder if it doesn't exist
mkdir -p "$BACKUP_DIR"

# Default container name (change to your default if any)
DEFAULT_CONTAINER="ims_db"

# Use the first command line argument as container name if provided; otherwise default
CONTAINER_NAME="${1:-$DEFAULT_CONTAINER}"

now_local=$(date +'%Y-%m-%d')
now_s3=$(date +'%Y/%m/%d')

SQLFILE=$BACKUP_DIR/${now_local}.lupien.ims.sql.txt

echo "Starting database backup..."
echo "Using container: $CONTAINER_NAME"
echo "Backup folder: $BACKUP_DIR"
echo "Backup file: $SQLFILE"

docker exec -u postgres "$CONTAINER_NAME" pg_dump -F p ims_db > "$SQLFILE"

if [ $? -eq 0 ]; then
  echo "Backup completed successfully."
else
  echo "Backup failed!" >&2
fi

######crontab -e ######
#####
##30 17 * * 5 bash /home/anand/duncan/ims_docker/Docker/backup2h4h.sh


