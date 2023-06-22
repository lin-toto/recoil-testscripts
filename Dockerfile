FROM nvidia/cuda:12.1.1-devel-ubuntu20.04
WORKDIR /work

RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

RUN apt-get -y update && apt-get -y install software-properties-common

RUN add-apt-repository ppa:ubuntu-toolchain-r/test \
    && apt-get -y update \
    && apt-get -y install gcc-10 g++-10 \
    && update-alternatives --install /usr/bin/gcc gcc /usr/bin/gcc-10 30 \
	&& update-alternatives --install /usr/bin/g++ g++ /usr/bin/g++-10 30 \
    && update-alternatives --install /usr/bin/cc cc /usr/bin/gcc 30 \
    && update-alternatives --set cc /usr/bin/gcc \
	&& update-alternatives --install /usr/bin/c++ c++ /usr/bin/g++ 30 \
    && update-alternatives --set c++ /usr/bin/g++

RUN apt-get -y install build-essential wget unzip \
  && wget https://github.com/Kitware/CMake/releases/download/v3.24.1/cmake-3.24.1-Linux-x86_64.sh \
      -q -O /tmp/cmake-install.sh \
      && chmod u+x /tmp/cmake-install.sh \
      && mkdir /opt/cmake-3.24.1 \
      && /tmp/cmake-install.sh --skip-license --prefix=/opt/cmake-3.24.1 \
      && rm /tmp/cmake-install.sh \
      && ln -s /opt/cmake-3.24.1/bin/* /usr/local/bin

RUN apt-get -y install python3-pip

ADD ./build.sh /work/build.sh
ADD ./runall.sh /work/runall.sh
ADD ./fetch_dataset.sh /work/fetch_dataset.sh
ADD ./dataset /work/dataset
ADD ./recoil /work/recoil
ADD ./multians /work/multians
ADD ./testscripts /work/testscripts

RUN chmod +x /work/fetch_dataset.sh && /work/fetch_dataset.sh

RUN chmod +x /work/build.sh && /work/build.sh

RUN pip install -r /work/testscripts/requirements.txt

RUN chmod +x /work/runall.sh
ENTRYPOINT /work/runall.sh