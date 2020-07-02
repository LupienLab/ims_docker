FROM ubuntu:20.04
FROM python:3.7.4
RUN apt-get update -y 

ENV PYTHONUNBUFFERED 1
RUN mkdir /code

ADD ./config/pip-requirements.txt  /code/
RUN pip install -r /code/pip-requirements.txt


RUN apt-get install netcat -y
#RUN apt install python-pygraphviz
 
WORKDIR /ims
ADD start_django_server.sh /code/

