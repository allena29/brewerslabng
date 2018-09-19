# Docker Note




If using a Mac we need to use VM's - rather than use the Docker GUI we will use virtualbox to provide VM's. This is super easy and lends itself to creating a swam.

### Create a Gaffer and initialise it

```bash
docker-machine create --driver virtualbox docker-gaffer

# Lookup IP address
docker-machine ls
NAME            ACTIVE   DRIVER       STATE     URL                         SWARM   DOCKER        ERRORS
docker-gaffer   -        virtualbox   Running   tcp://192.168.99.106:2376           v18.06.1-ce
```

### Allow local registry to be insecure (not HTTPS)
```bash
# Prepare for local registry
docker-machine ssh docker-gaffer 'sudo touch /etc/docker/daemon.json'
docker-machine ssh docker-gaffer 'sudo chown docker /etc/docker/daemon.json'
docker-machine ssh docker-gaffer "echo '{ \"insecure-registries\":[\"192.168.99.106:5000\"] }' >/etc/docker/daemon.json"
docker-machine ssh docker-gaffer 'sudo /etc/init.d/docker restart'
```



### Initialise Docker Swarm

```bash
docker-machine ssh docker-gaffer "docker swarm init --advertise-addr 192.168.99.106"
Swarm initialized: current node (vzvahmfijayhpfq95mwe1nx8c) is now a manager.

To add a worker to this swarm, run the following command:

    docker swarm join --token SWMTKN-1-26u9ly12v24oc3p2v8tf4i0unu1iznr9ft5n2ojogndlzd2nf0-50hjdk7jsvuk87hcxue2zgzkq 192.168.99.106:2377
    
To add a manager to this swarm, run 'docker swarm join-token manager' and follow the instructions.
```





## Build a registry

```bash
docker-machine ssh docker-gaffer

# Then run this
docker run -d -p 5000:5000 --restart=always --name registry registry:2

# Check running
docker ps
CONTAINER ID        IMAGE               COMMAND                  CREATED             STATUS              PORTS                    NAMES
02cf00fd99e1        registry:2          "/entrypoint.sh /etc…"   3 minutes ago       Up 3 minutes        0.0.0.0:5000->5000/tcp   registry

```


## Create a Constructor (MAC OSX only)

This let's us use somewhere to build images, it is given a bit more grunt. In this case we let docker-machine mount the home directory, in the case of the Mac this is `/Users` that gets mounted.

```bash
docker-machine create --driver virtualbox --virtualbox-cpu-count 6 --virtualbox-disk-size 20000 --virtualbox-memory 4096 docker-constructor
```



### Allow local registry to be insecure (not HTTPS)

```bash
# Prepare for local registry
docker-machine ssh docker-constructor 'sudo touch /etc/docker/daemon.json'
docker-machine ssh docker-constructor 'sudo chown docker /etc/docker/daemon.json'
docker-machine ssh docker-constructor "echo '{ \"insecure-registries\":[\"192.168.99.106:5000\"] }' >/etc/docker/daemon.json"
docker-machine ssh docker-constructor 'sudo /etc/init.d/docker restart'
```


### Build an Image and Push to our local repository



```bash
docker-machine ssh docker-constructor
cd /Users/adam/brewerslabng/Documentation/grafana
docker build -t blng-grafana .
docker tag blng-grafana 192.168.99.106:5000/blng-grafana
docker push 192.168.99.106:5000/blng-grafana
```



### Create a Navvy 

we add the docker worker with the token we used from before

```bash
docker-machine create --driver virtualbox --virtualbox-cpu-count 1 --virtualbox-disk-size 20000 --virtualbox-memory 1024 --virtualbox-no-share docker-navvy-a

# Prepare for local registry
docker-machine ssh docker-navvy-a 'sudo touch /etc/docker/daemon.json'
docker-machine ssh docker-navvy-a 'sudo chown docker /etc/docker/daemon.json'
docker-machine ssh docker-navvy-a "echo '{ \"insecure-registries\":[\"192.168.99.106:5000\"] }' >/etc/docker/daemon.json"
```


##### Add Bridged Networks

```
VBoxManage controlvm docker-navvy-a acpipowerbutton
```

Wait for the VM to stop

```
VBoxManage modifyvm docker-navvy-a --nic3 bridged --bridgeadapter3 en0
VBoxManage modifyvm docker-navvy-a --nic4 bridged --bridgeadapter4 en7
VBoxManage startvm docker-navvy-a --type headless
```

##### Join the swarm

```
docker-machine ssh docker-navvy-a "docker swarm join --token SWMTKN-1-26u9ly12v24oc3p2v8tf4i0unu1iznr9ft5n2ojogndlzd2nf0-50hjdk7jsvuk87hcxue2zgzkq 192.168.99.106:2377"
```


### Create a Navvy 

we add the docker worker with the token we used from before

```bash
docker-machine create --driver virtualbox --virtualbox-cpu-count 1 --virtualbox-disk-size 20000 --virtualbox-memory 1024 --virtualbox-no-share docker-navvy-b

# Prepare for local registry
docker-machine ssh docker-navvy-b 'sudo touch /etc/docker/daemon.json'
docker-machine ssh docker-navvy-b 'sudo chown docker /etc/docker/daemon.json'
docker-machine ssh docker-navvy-b "echo '{ \"insecure-registries\":[\"192.168.99.106:5000\"] }' >/etc/docker/daemon.json"
```


##### Add Bridged Networks

```
VBoxManage controlvm docker-navvy-b acpipowerbutton
```

Wait for the VM to stop

```
VBoxManage modifyvm docker-navvy-b --nic3 bridged --bridgeadapter3 en0
VBoxManage modifyvm docker-navvy-b --nic4 bridged --bridgeadapter4 en7
VBoxManage startvm docker-navvy-b --type headless
```

##### Join the swarm

```
docker-machine ssh docker-navvy-b "docker swarm join --token SWMTKN-1-26u9ly12v24oc3p2v8tf4i0unu1iznr9ft5n2ojogndlzd2nf0-50hjdk7jsvuk87hcxue2zgzkq 192.168.99.106:2377"
```



# Build a service 

This doesn't use compose but will fetch an image from the local repository.

```
docker service create --replicas 1 -p 3000:3000 --name grafana 192.168.99.10
6:5000/blng-grafana
```

Note: for this to work the `Dockerfile` must have a RUN defined - otherwise it won't run by default.

--------


# Other Notes..

``` not our example - just master and A are running
docker service create --replicas 5 -p 80:80 --name web nginx

uvad97jw8phbx0im7pxa0hp94
overall progress: 0 out of 5 tasks
overall progress: 0 out of 5 tasks
overall progress: 0 out of 5 tasks
overall progress: 5 out of 5 tasks
1/5: running
2/5: running
3/5: running
4/5: running
5/5: running
verify: Service converged

docker service ls
ID                  NAME                MODE                REPLICAS            IMAGE                                     PORTS
nyzprb0qdax6        test_web            replicated          0/2                 192.168.99.106:5000/blng-grafana:latest   *:4000->80/tcp
uvad97jw8phb        web                 replicated          5/5                 nginx:latest                              *:80->80/tcp


docker-machine ssh docker-gaffer docker ps
CONTAINER ID        IMAGE               COMMAND                  CREATED             STATUS              PORTS                    NAMES
d0fc82a33216        nginx:latest        "nginx -g 'daemon of…"   2 minutes ago       Up 2 minutes        80/tcp                   web.4.wkyskcl4p4v24aw8637vhecxe
193b4233a810        nginx:latest        "nginx -g 'daemon of…"   2 minutes ago       Up 2 minutes        80/tcp                   web.2.p77fvlhx2sb2ovv79rwzwra9s
02cf00fd99e1        registry:2          "/entrypoint.sh /etc…"   22 hours ago        Up 22 hours         0.0.0.0:5000->5000/tcp   registry

docker-machine ssh docker-navvy-a docker ps
CONTAINER ID        IMAGE               COMMAND                  CREATED             STATUS              PORTS               NAMES
14860c17d6e5        nginx:latest        "nginx -g 'daemon of…"   2 minutes ago       Up 2 minutes        80/tcp              web.5.t4sb5jbi7o5r9mf2k76cvjdy0
4ca5693313ca        nginx:latest        "nginx -g 'daemon of…"   2 minutes ago       Up 2 minutes        80/tcp              web.1.xkmg9dts96vb04q8pirotagrs
530d4857ac7d        nginx:latest        "nginx -g 'daemon of…"   2 minutes ago       Up 2 minutes        80/tcp              web.3.qr7gcubunzbtcd1zgmg2lieym
[I] git:g

docker-machine ssh docker-gaffer docker service ps web
ID                  NAME                IMAGE               NODE                DESIRED STATE       CURRENT STATE           ERROR               PORTS
xkmg9dts96vb        web.1               nginx:latest        docker-navvy-a      Running             Running 6 minutes ago
p77fvlhx2sb2        web.2               nginx:latest        docker-gaffer       Running             Running 6 minutes ago
qr7gcubunzbt        web.3               nginx:latest        docker-navvy-a      Running             Running 6 minutes ago
wkyskcl4p4v2        web.4               nginx:latest        docker-gaffer       Running             Running 6 minutes ago
t4sb5jbi7o5r        web.5               nginx:latest        docker-navvy-a      Running             Running 6 minutes ago
docker@docker-gaffer:~$


# Then we shutdown the navvy-a

docker@docker-gaffer:~$ docker service ps web
ID                  NAME                IMAGE               NODE                DESIRED STATE       CURRENT STATE              ERROR               PORTS
t70ljwrji82o        web.1               nginx:latest        docker-navvy-b      Running             Preparing 10 seconds ago
xkmg9dts96vb         \_ web.1           nginx:latest        docker-navvy-a      Shutdown            Running 23 seconds ago
p77fvlhx2sb2        web.2               nginx:latest        docker-gaffer       Running             Running 8 minutes ago
07qjaaa7c6p2        web.3               nginx:latest        docker-navvy-b      Running             Preparing 10 seconds ago
qr7gcubunzbt         \_ web.3           nginx:latest        docker-navvy-a      Shutdown            Running 23 seconds ago
wkyskcl4p4v2        web.4               nginx:latest        docker-gaffer       Running             Running 8 minutes ago
jtdir509hkfe        web.5               nginx:latest        docker-navvy-b      Running             Preparing 10 seconds ago
t4sb5jbi7o5r         \_ web.5           nginx:latest        docker-navvy-a      Shutdown            Running 23 seconds ago
docker@docke

# remove the service
docker service ps
```
