mkdir duncan
cd duncan
git clone https://github.com/LupienLab/ims_docker.git
mkdir media static db_backups
chmod -R 777 db_backups/ media/ static ~/duncan/ims_docker/ims/metadata/migrations
cd ims_docker/ims
mkdir media static
cd ~/duncan/ims_docker/ims/metadata
#vi model.py edit cloneMixin
#vi keycloak_client.py
# cd ~/duncan/ims_docker/Docker
# docker-compose -f prod_docker-compose.yml up
# Now cancel and come out
# mv models1.py models.py
