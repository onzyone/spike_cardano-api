### build

FROM python:3.10.4-slim-buster as builder

ENV DEBIAN_FRONTEND=noninteractive

# Install dependencies
RUN apt-get update \
  && apt-get install -y \
    autoconf automake build-essential g++ git jq \
    libffi-dev libgmp-dev libncursesw5 libnuma-dev libssl-dev libsystemd-dev libtinfo-dev libtool llvm \
    make pkg-config tmux wget zlib1g-dev

# Install Libsodium
WORKDIR /src
RUN git clone https://github.com/input-output-hk/libsodium
WORKDIR libsodium
RUN git checkout 66f017f1
RUN ./autogen.sh \
  && ./configure \
  && make install

ENV LD_LIBRARY_PATH="/usr/local/lib"
ENV PKG_CONFIG_PATH="/usr/local/lib/pkgconfig"

## git@github.com:tdiesler/nessus-cardano.git
## https://hub.docker.com/r/nessusio/cardano-node
# nessusio/cardano-node:1.34.1
# DIGEST:sha256:e9beb663ae9a90e46437bcc8eedc82c68e707f9782f88673f9f451ce0a2c445d

FROM nessusio/cardano-node:1.34.1 as prebuilt

### run
FROM builder

# https://dist.ipfs.io/go-ipfs/v0.12.0
ENV IPFS_VERSION=0.12.0
ENV IPFS_ARCH=arm64
RUN wget https://dist.ipfs.io/go-ipfs/v0.12.0/go-ipfs_v${IPFS_VERSION}_linux-${IPFS_ARCH}.tar.gz && \
    tar -xvzf go-ipfs_v${IPFS_VERSION}_linux-${IPFS_ARCH}.tar.gz && \
    cd go-ipfs && \
    bash install.sh \
    rm go-ipfs_v${IPFS_VERSION}_linux-${IPFS_ARCH}.tar.gz \
    ipfs init --profile server

COPY --from=prebuilt /usr/local/bin/cardano-node /usr/local/bin/
COPY --from=prebuilt /usr/local/bin/cardano-cli /usr/local/bin/
ENV CARDANO_NODE_SOCKET_PATH=/node-ipc/node.socket
ENTRYPOINT ["cardano-cli"]
CMD [ "--help" ]
