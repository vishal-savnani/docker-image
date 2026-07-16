FROM httpd:2.4-trixie

LABEL authors="vishal.savnani"

RUN apt-get update \
    && apt-get upgrade -y \
    && rm -rf /var/lib/apt/lists/*

COPY html/ /usr/local/apache2/htdocs/
