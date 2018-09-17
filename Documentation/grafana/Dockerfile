FROM debian:stretch

RUN \
      apt-get update && apt-get install -y \
      # general tools
      git \
      vim \
      curl \
      gnupg \
      apt-transport-https \
      python3

# add netconf user
RUN \
    adduser --system graphana && \
    echo "graphana:graphana" | chpasswd

# Install Influx
RUN \
  curl -sL "https://repos.influxdata.com/influxdb.key" | apt-key add - && \
  echo "deb https://repos.influxdata.com/debian jessie stable" >/etc/apt/sources.list.d/influxdb.list  && \
  apt-get update && apt-get -y  install influxdb

# Install Grafana
RUN \
  curl -sL "https://bintray.com/user/downloadSubjectPublicKey?username=bintray" | apt-key add - && \
  curl -sL "https://packagecloud.io/gpg.key" | apt-key add - && \
  echo 'deb https://packagecloud.io/grafana/stable/debian/ stretch main' >/etc/apt/sources.list.d/grafana.list && \
  echo "deb https://dl.bintray.com/fg2it/deb-rpi-1b stretch main" >>/etc/apt/sources.list.d/grafana.list && \
  apt-get update && apt-get -y install grafana

COPY grafana.ini /etc/grafana/grafana.ini

# Start grafana and add the image
RUN \
  chown grafana:grafana /etc/grafana/grafana.ini && \
  /etc/init.d/grafana-server start || echo 'Overlook failure to start'  && \
  curl 'http://admin:beerng@127.0.0.1:3000/api/datasources' -X POST -H 'Content-Type: application/json;charset=UTF-8' --data-binary '{"name":"temperatures","type":"influxdb","url":"http://localhost:8086","access":"proxy","isDefault":true,"database":"temperatures","user":"root","password":"beerng"}'


COPY influx.sql /tmp/influx.sql

RUN \
  /etc/init.d/influxdb start && \
  echo "CREATE DATABASE temperatures;" | influx && \
  influx -database temperatures < /tmp/influx.sql && \
  influx < /tmp/influx.sql

ENV EDITOR vim
EXPOSE 3000 8086
