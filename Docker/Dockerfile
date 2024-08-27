FROM ubuntu:24.04
RUN apt-get update -y
RUN apt-get install -y build-essential
RUN apt-get install -y graphviz
RUN apt-get install -y graphviz-dev
RUN apt-get install netcat-openbsd -y
RUN apt-get install -y python3
RUN apt-get install -y python3-pip
RUN apt-get install -y libpq-dev

ENV PYTHONUNBUFFERED 1
ENV PIP_BREAK_SYSTEM_PACKAGES 1

RUN mkdir /code


ADD ./config/pip-requirements.txt  /code/
RUN pip3 install -r /code/pip-requirements.txt


WORKDIR /ims
ADD start_django_server.sh /code/

