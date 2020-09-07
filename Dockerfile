# pull official base image, alpine images are thingger
FROM python:3.8.3

# set work directory
WORKDIR /usr/src/app

# set environment variables to not add pyc files and to force the stdout and stderr streams to be unbuffered. 
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# install psycopg2 dependencies
# RUN apk update \
#     && apk add postgresql-dev gcc python3-dev musl-dev

# install dependencies
RUN pip install --upgrade pip
COPY ./requirements.txt .
RUN pip install -r requirements.txt

# copy project
COPY . .
