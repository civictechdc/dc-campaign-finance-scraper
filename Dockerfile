FROM python:3

ADD . /code/
WORKDIR /code
RUN pip install -r requirements-testing.txt -e .

ENV LC_ALL C.UTF-8
ENV LANG C.UTF-8
