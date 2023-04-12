FROM python:3.11-alpine

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

RUN mkdir /code
WORKDIR /code

RUN pip install --upgrade pip

RUN apk update \
    && apk add --virtual build-essential gcc python3-dev musl-dev \
    && apk add postgresql-dev \
    && pip install psycopg2

COPY ./requirements.txt /code/
RUN pip install -r requirements.txt

COPY . /code/

RUN python manage.py collectstatic --noinput

RUN adduser -D myuser
USER myuser
