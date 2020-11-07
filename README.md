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

Find the code in the directory `semapp/lambda_function`. To upload the code to the lambda function in AWS, once access to the AWS CLI is configured, run the `send_code.sh` script.

To build the layer you can run the script inside the `semapp/lambda_function/layers` directory. Short instructions are contained in that file.

## Stack

* Backend: django
* Web server: nginx
* WSGI HTTP Server: gunicorn
* AWS lambda functions
* SSL Certificate: certbot, it updates automatically
* Database: AWS Postgresql

## Dev environment
There is a dev environment where nginx, gunicorn and the certbot is disconnected.

To run the dev environment use:

`sudo docker-compose -f docker-compose.dev.yml up -d --build`

Access to it directly to the IP of the machine, port 8000.
