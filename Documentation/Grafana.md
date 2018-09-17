# Startup Daemon's


Docker images need to be started mapping `-p 3000:3000 -p 8086:8086` ports


```bash
/etc/init.d/grafana restart
/etc/init.d/influxdb restart
```

At this point we can navigate to [http://127.0.0.1:3000/](http://127.0.0.1:3000/) and login to the grafana management interface. Username: admin  Password: beerng



# Influx DB

We can connect to the database with `influx -database temperatures`



# Grafana

#### Datasource.

We currently provision the datasource by making an API call with grafana running.

#### Dashboard.

- Create a datashboard, and select the drop down box on the Panel Title
  - select datasource `
SELECT value from ferm
