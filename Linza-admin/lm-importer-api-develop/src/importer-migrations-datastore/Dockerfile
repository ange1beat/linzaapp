FROM python:3.9-alpine
WORKDIR /app/
LABEL maintainer="stasyanzayac@gmail.com"
RUN apk -U upgrade && \
    apk --no-cache add python3 ca-certificates
RUN pip install --trusted-host pypi.org --trusted-host files.pythonhosted.org pip setuptools
RUN apk add --virtual build-deps gcc libc-dev libxml2-dev libxslt-dev postgresql-dev python3-dev musl-dev
RUN pip install --upgrade pip

ADD ./src/importer-migrations-datastore/application.py /app/
ADD ./src/importer-migrations-datastore/requirements.txt /app/
ADD ./src/importer-migrations-datastore/models.py /app/
ADD ./src/config.py /app/
ADD ./src/producer.py /app/
ADD ./src/shared.py /app/
RUN pip3 install colorama==0.4.1
RUN pip3 install peewee==3.9.3
RUN pip3 install -r requirements.txt
ENTRYPOINT ["python", "-u", "application.py"]
