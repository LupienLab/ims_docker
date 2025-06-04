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

## Implementing the approval features

- Add concept of supervisor
- Add concept of approvals
- Add concept of notifications

leave export as is
export two files 10x

look at handle export
export sequencing form

ask them select which form

one line per experiment

we need submit to sequencing core

approval is associated with a project and 1 or more experiments

sequencing core can log in and only see approvals

lab can have one supervisor

project can have more than one lab

lab has users and one superivors
lab has many projects associated with it

person is associated with one lab

lab has name
supervisor
lab url

user belongs to one lab
