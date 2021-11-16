# ims_docker
1. Make sure docker is up and running
2. From inside docker folder run one of the following command:

###For production
  docker-compose -f prod_docker-compose.yml build
  
###For Development 
  docker-compose -f dev_docker-compose.yml build

3. Inititalize database from dump, if needed.
4. Run now with one of the following command:

###For production
  docker-compose -f prod_docker-compose.yml up -d
  
 
###For Development
  docker-compose -f dev_docker-compose.yml up -d
