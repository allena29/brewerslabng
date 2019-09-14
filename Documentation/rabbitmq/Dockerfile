FROM raspbian/stretch

RUN \
      apt-get update && apt-get install -y \
      # general tools
      git \
      vim \
      curl \
      gnupg \
      apt-transport-https \
      python3 \
      python3-pip


RUN \
      apt-get update && apt-get install -y \
      cmake \
      build-essential \
      supervisor \
      libpcre3-dev \
      pkg-config \
      libavl-dev \
      libev-dev \
      libprotobuf-c-dev \
      protobuf-c-compiler \
      libssl-dev \
#      swig \
      python-dev \
      python3-dev \
      libcurl4-openssl-dev \
      libxslt-dev \
      libxml2-dev \
      libtool \
      libtool-bin \
      python-setuptools \
      libreadline-dev \
      python-libxml2 \
      libprotobuf-dev && \
      apt-get install -y libtool libtool-bin libxml2-dev libxslt1-dev libcurl4-openssl-dev xsltproc
python-setuptools cmake zlib1g-dev libssl-dev pkg-config libreadline-dev && \
      apt-get install -y bison libboost-thread-dev libboost-thread1.62-dev autoconf automake screen
&& \
      apt-get install -y libffi-dev || echo 'livffi-dev does not exist'


RUN \
    pip3 install ipython ncclient && \
    mkdir -p /root/.ipython/profile_default   && \
    echo "c.Completer.use_jedi = False" >/root/.ipython/profile_default/ipython_config.py && \
    echo "c.TerminalInteractiveShell.confirm_exit = False" >>/root/.ipython/profile_default/ipython_
config.py

# add netconf user
RUN \
    adduser --system netconf && \
    echo "netconf:netconf" | chpasswd

# generate ssh keys for netconf user
RUN \
    mkdir -p /home/netconf/.ssh && \
    ssh-keygen -A && \
    ssh-keygen -t dsa -P '' -f /home/netconf/.ssh/id_dsa && \
    cat /home/netconf/.ssh/id_dsa.pub > /home/netconf/.ssh/authorized_keys

# use /opt/dev as working directory
RUN mkdir /opt/dev
WORKDIR /opt/dev


RUN git clone https://github.com/swig/swig.git && \
    cd swig && \
    ./autogen.sh && \
    ./configure && \
    make && \
    sudo make install

RUN git clone https://github.com/CESNET/libyang.git  && \
    git clone https://github.com/sysrepo/sysrepo.git

RUN \
    cd /opt/dev/libyang && \
    git checkout master && \
    mkdir build && \
    cd build && \
    cmake .. && \
    make && \
    sudo make install && \
    sudo ldconfig

RUN \
    curl -s https://packagecloud.io/install/repositories/rabbitmq/rabbitmq-server/script.deb.sh | ba
sh && \
     apt-get install -y rabbitmq-server && \
     rabbitmq-plugins enable rabbitmq_management

ADD start.sh /start.sh

CMD [ "/start.sh" ]

EXPOSE 5672:5672 15672:15672 25672:25672
