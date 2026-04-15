FROM python:3.9-alpine
WORKDIR /app/
LABEL maintainer="stasyanzayac@gmail.com"
RUN apk -U upgrade && \
    apk --no-cache add python3 ca-certificates
RUN pip install --trusted-host pypi.org --trusted-host files.pythonhosted.org pip setuptools
RUN apk add --virtual build-deps gcc libc-dev libxml2-dev libxslt-dev postgresql-dev python3-dev musl-dev bash
RUN apk add --no-cache curl

RUN pip install --upgrade pip

ADD . /app
RUN chmod +x src/importer_api/bootstrap.sh
RUN pip3 install -r src/importer_api/requirements.txt
#ENTRYPOINT ["sh", "src/importer_api/bootstrap.sh"]

ENTRYPOINT ["python", "-u", "src/importer_api/api.py"]
