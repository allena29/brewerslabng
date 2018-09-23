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

# add grafana user
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
  apt-get update && apt-get -y install grafana && \
  mkdir /var/lib/grafana/dashboards

COPY grafana.ini /etc/grafana/grafana.ini
COPY dashboards/* /tmp
COPY start.sh /

# Start grafana and add the image
RUN \
  chown grafana:grafana /etc/grafana/grafana.ini && \
  chown -R grafana:grafana /var/lib/grafana/dashboards && \
  /etc/init.d/grafana-server start || echo 'Overlook failure to start'  && \
  curl -u admin:beerng -X POST -H "Content-Type: application/json" --data '{"name":"beerng", "login":"beerng", "password":"beerng"}'  http://localhost:3000/api/admin/users && \
  curl 'http://admin:beerng@127.0.0.1:3000/api/datasources' -X POST -H 'Content-Type: application/json;charset=UTF-8' --data-binary '{"name":"beerstats","type":"influxdb","url":"http://localhost:8086","access":"proxy","isDefault":true,"database":"beerstats","user":"root","password":"beerng"}' && \
  curl 'http://127.0.0.1:3000/api/dashboards/import'  -H 'Content-Type: application/json;charset=UTF-8' --user admin:beerng -X POST --data-binary @/tmp/fermentation.json 


COPY influx.sql /tmp/influx.sql

RUN \
  /etc/init.d/influxdb start && \
  echo "CREATE DATABASE beerstats;" | influx && \
  influx -database beerstats < /tmp/influx.sql && \
  influx < /tmp/influx.sql

RUN \
  chmod 775 /start.sh && \
  apt-get clean autoclean && \
  apt-get autoremove --yes && \
  rm -rf /var/lib/{apt,dpkg,cache,log}/

ENV EDITOR vim
EXPOSE 3000 8086
STOPSIGNAL SIGTERM
CMD [ "/start.sh" ]
