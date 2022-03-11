FROM python:3.7-alpine
# maintainer line is optional
MAINTAINER Juan Antonio Montero de Espinosa

# tells Python to run in unbuffered mode
# Python prints outputs directly
ENV PYTHONUNBUFFERED 1

# Install our dependencies from a requirements.txt file
COPY ./requirements.txt /requirements.txt
RUN pip install -r /requirements.txt


RUN mkdir /app
# default location to run our docker image
WORKDIR /app
COPY ./app /app

# do this for security purposes, to avoid that an attacker may have
# root access
# create a user that is going to run our application using Docker
# D is only to run our processes, not have a home directory
RUN adduser -D user
USER user
