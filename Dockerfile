FROM nvidia/cuda:12.1.1-devel-ubuntu20.04
WORKDIR /work

ADD ./build.sh /work/build.sh
ADD ./recoil /work/recoil
ADD ./testscripts /work/testscripts

RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

RUN apt-get update \
  && apt-get -y install build-essential \
  && apt-get -y install software-properties-common \
  && apt-get install -y wget \
  && rm -rf /var/lib/apt/lists/* \
  && wget https://github.com/Kitware/CMake/releases/download/v3.24.1/cmake-3.24.1-Linux-x86_64.sh \
      -q -O /tmp/cmake-install.sh \
      && chmod u+x /tmp/cmake-install.sh \
      && mkdir /opt/cmake-3.24.1 \
      && /tmp/cmake-install.sh --skip-license --prefix=/opt/cmake-3.24.1 \
      && rm /tmp/cmake-install.sh \
      && ln -s /opt/cmake-3.24.1/bin/* /usr/local/bin

RUN apt-get update && \
    apt-get upgrade -y && \
    apt-get install -y git
RUN add-apt-repository ppa:ubuntu-toolchain-r/test \
    && apt-get -y update \
    && apt install -y gcc-10 \
	&& apt install -y g++-10 \
    && update-alternatives --install /usr/bin/gcc gcc /usr/bin/gcc-10 30 \
	&& update-alternatives --install /usr/bin/g++ g++ /usr/bin/g++-10 30 \
    && update-alternatives --install /usr/bin/cc cc /usr/bin/gcc 30 \
    && update-alternatives --set cc /usr/bin/gcc \
	&& update-alternatives --install /usr/bin/c++ c++ /usr/bin/g++ 30 \
    && update-alternatives --set c++ /usr/bin/g++

RUN /work/build.sh