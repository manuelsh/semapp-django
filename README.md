# Sem app
Based on https://testdriven.io/blog/dockerizing-django-with-postgres-gunicorn-and-nginx/

## Requirements to run in production
* docker
* docker-compose
* aws cli
* lambda function `builder` created
* access to update lambda functions
* zip

## To run in dev mode
`docker-compose up -d --build`

## To run in prod mode
`docker-compose -f docker-compose.prod.yml up -d --build`

## Lambda function
The code requires a lambda function with python3.8 environment to be created in amazon aws called `builders`.

Find the code in the directory `semapp/lambda_function`. To upload the code to the funcion, once access is granted, run the `send_code.sh` script.

To build the layer you can run the script inside the `semapp/lambda_function/layers` directory.

## Stack

* Backend: django
* Web server: nginx
* WSGI HTTP Server: gunicorn
* AWS lambda functions
* SSL Certificate: certbot, it updates automatically
* Database: AWS Postgresql
