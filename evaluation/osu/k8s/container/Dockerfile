FROM opensuse/leap:15.5 as builder

RUN zypper update -y \
 && zypper --non-interactive install --recommends \
    +pattern:devel_basis \
    gcc13 \
    gcc13-fortran \
    gcc13-c++ \
    gdb \
    libstdc++6-pp \
    rust cargo \
    boost-gnu-hpc \
    python311 \
    java-17-openjdk java-17-openjdk-devel \
    wget \
    git-core \
    gzip \
    cmake \
    ninja \
    vim \
    nano \
    hwloc hwloc-devel \
    zsh \
    libcurl-devel \
    libjson-c-devel \
    openssl-3 libopenssl3 \
    rdma-core-devel \
    libnl3-devel \
 && zypper cc --all

RUN update-alternatives --install /usr/bin/gcc gcc /usr/bin/gcc-13 50 \
 && update-alternatives --install /usr/bin/g++ g++ /usr/bin/g++-13 50 \
 && update-alternatives --install /usr/bin/gfortran gfortran /usr/bin/gfortran-13 50

# Libfabric
WORKDIR /opt
RUN set -ex \
 && git clone --branch v2.1.0 --depth 1 https://github.com/ofiwg/libfabric.git \
 && cd libfabric

COPY libfabric-shs-k8s.patch /opt/

# Note: --enable-cxi will not work out-of-the-batch.
#  This assumes that the build-command mounts the necessary CXI headers + libraries(!) into the build-container
#  Rationale: OpenCUBE will mount the CXI-libraries into containers during runtime anyway, so assuming it here is the least bad way of doing things
RUN cd /opt/libfabric \
 && git apply < /opt/libfabric-shs-k8s.patch \
 && sh autogen.sh \
 && ./configure \
    --prefix="/usr/local" \
    --enable-cxi=yes \
    --enable-only \
    --enable-restricted-dl \
    --enable-tcp \
    --enable-udp \
    --enable-rxm \
    --enable-rxd \
    --enable-hook_debug \
    --enable-hook_hmem \
    --enable-dmabuf_peer_mem \
 && make -j \
 && make install

# Open MPI
WORKDIR /opt

RUN set -ex \
 && mkdir -p /opt/openmpi \
 && cd /opt/openmpi \
 && wget -O- https://download.open-mpi.org/release/open-mpi/v5.0/openmpi-5.0.7.tar.gz | tar -zx --strip-component=1 \
 && ./configure \
    --prefix="/usr/local" \
    --enable-mpi-fortran \
    --with-ofi="/usr/local" \
    --with-libevent=internal \
    --with-hwloc=internal \
    --with-pmix=internal
RUN cd /opt/openmpi \
 && make -j \
 && make install


FROM opensuse/leap:15.5
COPY --from=builder /usr/local /usr/local
RUN zypper update -y \
 && zypper --non-interactive install --recommends \
    +pattern:devel_basis \
    gcc13 \
    gcc13-fortran \
    gcc13-c++ \
    gdb \
    libstdc++6-pp \
    rust cargo \
    boost-gnu-hpc \
    python311 \
    java-17-openjdk java-17-openjdk-devel \
    wget \
    git-core \
    gzip \
    cmake \
    ninja \
    vim \
    nano \
    zsh \
    hwloc hwloc-devel \
    libcurl-devel \
    libjson-c-devel \
    openssl-3 libopenssl3 \
    rdma-core-devel \
    libnl3-devel \
    sudo \
 && zypper cc --all

RUN update-alternatives --install /usr/bin/gcc gcc /usr/bin/gcc-13 50 \
 && update-alternatives --install /usr/bin/g++ g++ /usr/bin/g++-13 50 \
 && update-alternatives --install /usr/bin/gfortran gfortran /usr/bin/gfortran-13 50

WORKDIR /root
RUN zypper --non-interactive install \
    libcurl-devel \
    libjson-c-devel \
    openssl-3 libopenssl3 \
    rdma-core-devel \
    libnl3-devel

# make ldconfig cache OpenMPI libaries
RUN ldconfig

# create host keys
RUN ssh-keygen -t rsa -f /etc/ssh/ssh_host_rsa_key -N "" \
 && ssh-keygen -t ecdsa -f /etc/ssh/ssh_host_ecdsa_key  -N "" \
 && ssh-keygen -t ed25519 -f /etc/ssh/ssh_host_ed25519_key  -N "" \
 && echo "        LogLevel ERROR" >> /etc/ssh/ssh_config \
 && echo "        StrictHostKeyChecking no" >> /etc/ssh/ssh_config \
 && echo "        UserKnownHostsFile=/dev/null" >> /etc/ssh/ssh_config

# create mpiuser & ssh keys
RUN groupadd -r mpiuser -g 1000 \
  && useradd --no-log-init -r -m -b /home -g mpiuser -G wheel -u 1000 mpiuser

RUN ulimit -c unlimited

USER mpiuser
RUN  cd /home/mpiuser \
 && ssh-keygen -t rsa -N "" -f ~/.ssh/id_rsa \
 && chmod og+rX . \
 && cd .ssh \
 && cat id_rsa.pub > authorized_keys \
 && chmod 644 authorized_keys \
 && exit

WORKDIR /home/mpiuser
RUN mkdir osu \
 && cd osu \
 && wget -O- https://mvapich.cse.ohio-state.edu/download/mvapich/osu-micro-benchmarks-7.3.tar.gz | tar -zx --strip-component=1 \
 && ./configure CC=mpicc CXX=mpicxx \
 && make -j

COPY launcher_multi.sh /home/mpiuser/

USER root
RUN chown mpiuser:mpiuser /home/mpiuser/launcher_multi.sh