FROM python:3.9.16
LABEL maintainer="Javier Sánchez <javiersanp@gmail.com>"
RUN apt-get update
WORKDIR /app
COPY requirements.txt /app
RUN pip install \
    --no-cache-dir \
    --disable-pip-version-check \
    -r requirements.txt
COPY . /app
HEALTHCHECK CMD curl --fail http://localhost/status || exit 1
