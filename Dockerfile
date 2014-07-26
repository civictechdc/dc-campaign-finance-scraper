FROM python:3

ENV LC_ALL C.UTF-8
ENV LANG C.UTF-8

ADD . /code/
WORKDIR /code
RUN pip install -r requirements-testing.txt -e .
