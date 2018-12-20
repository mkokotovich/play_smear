FROM python:3.7-alpine3.8

RUN apk update \
  && apk add \
    bash \
    build-base \
    postgresql \
    postgresql-dev \
    libpq

RUN mkdir /usr/src/app
WORKDIR /usr/src/app
COPY ./backend/requirements.txt .
RUN pip install -r requirements.txt

COPY backend .
