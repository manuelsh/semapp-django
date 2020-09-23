# Sem app
Based on https://testdriven.io/blog/dockerizing-django-with-postgres-gunicorn-and-nginx/

## Requirements to run
* docker
* docker-compose

## To run in dev mode
`docker-compose up -d --build`

## To run in prod mode
`docker-compose -f docker-compose.prod.yml up -d --build`