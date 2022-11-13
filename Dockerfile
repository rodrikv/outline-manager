FROM python:3.9-slim

# init
ADD . /code
WORKDIR /code

# setup
RUN apt-get update

RUN pip3 install --upgrade pip
RUN pip3 install -r requirements.txt

