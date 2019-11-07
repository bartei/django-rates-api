FROM python:3.7-stretch

RUN mkdir /app
COPY . /app/

RUN pip install -r /app/requirements.txt

EXPOSE 8000
WORKDIR /app/restful_test

CMD gunicorn -b 0.0.0.0:8000 restful_test.wsgi
