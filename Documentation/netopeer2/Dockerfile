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

RUN \
      apt-get install -y \
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
      doxygen-dbg  && \
      apt-get install -y libtool libtool-bin libxml2-dev libxslt1-dev libcurl4-openssl-dev xsltproc python-setuptools cmake zlib1g-dev libssl-dev pkg-config libreadline-dev && \ 
      apt-get install -y bison libboost-thread-dev libboost-thread1.62-dev autoconf automake


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
      git checkout afa4021ded6e58da4ee4d01dbf4e503d3711d002 && \
#      git checkout 983d1189d08436ba818b591d7a0185927758349c && \
      mkdir build && cd build && \
      cmake .. && \
      make -j6 && \
      make install && \
      ldconfig

# libyang
RUN \
      cd /opt/dev && \
      git clone https://github.com/CESNET/libyang.git && \
      cd libyang && \
      git checkout 85d09f3bdf5ea01ea2e01deb384b2b0dde057e3f && \
      mkdir build && cd build && \
      cmake .. && \
      make -j6  && \
      make install && \
      ldconfig

# protobuf
#RUN \
#      cd /opt/dev && \
#      git clone https://github.com/protocolbuffers/protobuf.git && \
#      cd protobuf && \
#      #git checkout ff3891dab1b1f462d90a68666d14f57eb5fea34f && \
#      git submodule update --init --recursive && \
#      sh autogen.sh && \
#      ./configure && \
#      make -j6 && \
#      make install && \
#      ldconfig

# protobuf-c
#RUN \
#      cd /opt/dev && \
#      git clone https://github.com/protobuf-c/protobuf-c.git && \
#      cd protobuf-c && \
#      git checkout dac1a65feac4ad72f612aab99f487056fbcf5c1a && \
#      sh autogen.sh && \
#      ./configure --disable-protoc && \
#      # Think in the end we did 
#      #./configure && \
#      make -j6 && \
#      make install && \
#      ldconfig
    

# sysrepo
RUN \
      cd /opt/dev && \
      git clone https://github.com/sysrepo/sysrepo.git && \
      cd sysrepo && \
      git checkout 724a62fa830df7fcb2736b1ec41b320abe5064d2 && \
      mkdir build_python3 && \
      cd build_python3 && \
      cmake -DREPOSITORY_LOC=/sysrepo -DGEN_PYTHON_VERSION=3 .. && \
      make -j6 && \
      make install && \
      ldconfig 

# libnetconf2
RUN \
      git clone https://github.com/CESNET/libnetconf2.git && \
      cd libnetconf2 && mkdir build && cd build && \
      git checkout 54ba1c7a1dbd85f3e700c1629ced8e4b52bac4ec && \
      cmake .. && \
      make -j6 && \
      make install && \
      ldconfig

# keystore
RUN \
      cd /opt/dev && \
      git clone https://github.com/CESNET/Netopeer2.git && \
      cd Netopeer2 && \
      git checkout d3ae5423847cbfc67c844ad19288744701bd47a4 && \
      cd keystored && mkdir build && cd build && \
      git checkout devel-server && \
      cmake .. && \
      make -j6  && \
      make install && \
      ldconfig

# netopeer2
RUN \
      cd /opt/dev && \
      cd Netopeer2/server && mkdir build && cd build && \
      git checkout d3ae5423847cbfc67c844ad19288744701bd47a4 && \
      cmake .. && \
      make -j6 && \
      make install && \
      cd ../../cli && mkdir build && cd build && \
      cmake -DCMAKE_BUILD_TYPE:String="Debug" .. && \
      make  && \
      make install

RUN \
    apt-get clean && \
    apt-get autoclean && \
    rm -fr /opt/dev

ENV EDITOR vim
EXPOSE 830
