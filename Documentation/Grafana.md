# Startup Daemon's


Docker images need to be started mapping `-p 3000:3000 -p 8086:8086` ports


```bash
/etc/init.d/grafana restart
/etc/init.d/influxdb restart
```

At this point we can navigate to [http://127.0.0.1:3000/](http://127.0.0.1:3000/) and login to the grafana management interface. Username: admin  Password: beerng



# Influx DB

We can connect to the database with `influx -database temperatures`

Once we are populating data (i.e. `publishTemperatureToInflux.py`)  then we can check things in the Influx CLI.

```
root@galaxy:/var/lib/grafana/dashboards# influx
Connected to http://localhost:8086 version 1.6.2
InfluxDB shell version: 1.6.2
> use beerstats;
Using database beerstats

> show series;
key
---
ferm,host=shjips

> show measurements;
name: measurements
name
----
ferm
>
>
> SELECT value FROM ferm LIMIT 5;
name: ferm
time                value
----                -----
1537222239476724224 17
1537222244323504384 17.062
1537222249157805824 17
1537222253996077568 17
1537222258839175168 17
```

#### Backup Data

```
influxd backup -portable -database beerstats /tmp/x
```

# Grafana

#### Datasource.

We currently provision the datasource by making an API call with grafana running.

#### Dashboard.

- Create a datashboard, and select the drop down box on the Panel Title
  - select datasource `temperatures`
  - from default `ferm` 
SELECT value from ferm


