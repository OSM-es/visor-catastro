FROM egofer/catatom2osm:latest
LABEL maintainer="Javier Sánchez <javiersanp@gmail.com>"
USER root
WORKDIR /app
COPY . .
RUN pip install \
    --no-cache-dir \
    --disable-pip-version-check \
    -r requirements.txt
USER catastro
WORKDIR /catastro
