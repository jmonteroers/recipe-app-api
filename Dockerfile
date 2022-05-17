FROM python:3.9-alpine3.13
# maintainer line is optional
LABEL maintainer="Juan Antonio Montero de Espinosa"

# tells Python to run in unbuffered mode
# Python prints outputs directly, allowing us to see logs immediately
ENV PYTHONUNBUFFERED 1

# Install our dependencies from a requirements.txt file
COPY ./requirements.txt /tmp/requirements.txt
COPY ./requirements.dev.txt /tmp/requirements.dev.txt

RUN mkdir /app
# default location to run our docker image
COPY ./app /app
WORKDIR /app

EXPOSE 8000

ARG DEV=false
RUN python -m venv /py && \
  /py/bin/pip install --upgrade pip && \
  /py/bin/pip install -r /tmp/requirements.txt && \
  if [ $DEV = "true" ] ; \
    then /py/bin/pip install -r /tmp/requirements.dev.txt ; \
  fi && \
  rm -rf /tmp && \
  adduser \
    --disabled-password \
    --no-create-home \
    django-user

ENV PATH="/py/bin:$PATH"

USER django-user