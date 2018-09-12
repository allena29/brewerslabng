FROM debian:9.4

RUN \
      apt-get update && apt-get install -y \
      # general tools
      git \
      cmake \
      build-essential \
      vim \
      supervisor \
      # libyang
      libpcre3-dev \
      pkg-config \
      # sysrepo
      libavl-dev \
      libev-dev \
      libprotobuf-c-dev \
      protobuf-c-compiler \
      # netopeer2 \
      libssl-dev \
      # bindings
      swig \
      python-dev \
      libcurl4-openssl-dev \
      libxslt-dev \
      libxml2-dev \
      libtool \
      libtool-bin \
      python-setuptools \
      libreadline-dev \
      python-libxml2 \
      libprotobuf-dev \
      doxygen-dbg 

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

# pyang
RUN \
      cd /opt/dev && \
      git clone https://github.com/mbj4668/pyang.git && \
      cd pyang && \
      git checkout cca321ef0c6ddf82c77c12aca8301bcfdfd5b7d3 && \
      python setup.py install

# libssh
RUN \
      cd /opt/dev && \
      git clone https://git.libssh.org/projects/libssh.git libssh && \
      cd libssh && \
      git checkout 983d1189d08436ba818b591d7a0185927758349c && \
      mkdir build && cd build && \
      cmake .. && \
      make && \
      make install && \
      ldconfig

# libyang
RUN \
      git clone https://github.com/CESNET/libyang.git && \
      cd libyang && git checkout 85d09f3bdf5ea01ea2e01deb384b2b0dde057e3f && mkdir build && cd build && \
      git checkout devel && \
      cmake -DCMAKE_BUILD_TYPE:String="Debug" -DENABLE_BUILD_TESTS=OFF .. && \
      make -j2 && \
      make install && \
      ldconfig

# sysrepo
RUN \
      git clone https://github.com/sysrepo/sysrepo.git && \
      cd sysrepo && git checkout 724a62fa830df7fcb2736b1ec41b320abe5064d2 && mkdir build && cd build && \
      git checkout devel && \
      cmake -DCMAKE_BUILD_TYPE:String="Debug" -DENABLE_TESTS=OFF -DREPOSITORY_LOC:PATH=/etc/sysrepo .. && \
      make -j2 && \
      make install && \
      ldconfig

# libnetconf2
RUN \
      git clone https://github.com/CESNET/libnetconf2.git && \
      cd libnetconf2 && mkdir build && cd build && \
      git checkout 54ba1c7a1dbd85f3e700c1629ced8e4b52bac4ec && \
      cmake -DCMAKE_BUILD_TYPE:String="Debug" -DENABLE_BUILD_TESTS=OFF .. && \
      make -j2 && \
      make install && \
      ldconfig

# keystore
RUN \
      cd /opt/dev && \
      git clone https://github.com/CESNET/Netopeer2.git && \
      cd Netopeer2 && git checkout d3ae5423847cbfc67c844ad19288744701bd47a4 && \
      cd keystored && mkdir build && cd build && \
      git checkout devel-server && \
      cmake -DCMAKE_BUILD_TYPE:String="Debug" .. && \
      make -j2 && \
      make install && \
      ldconfig

# netopeer2
RUN \
      cd /opt/dev && \
      cd Netopeer2/server && mkdir build && cd build && \
      cmake -DCMAKE_BUILD_TYPE:String="Debug" .. && \
      make -j2 && \
      make install && \
      cd ../../cli && mkdir build && cd build && \
      cmake -DCMAKE_BUILD_TYPE:String="Debug" .. && \
      make -j2 && \
      make install

ENV EDITOR vim
EXPOSE 830
