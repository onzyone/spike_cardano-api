FROM debian:buster-slim as builder
ARG CARDANO_CLI_VERSION=1.24.2
ARG CARDANO_NODE_REPO_TAG=400d18092ce604352cf36fe5f105b0d7c78be074
RUN apt-get update && apt-get install -y \
    automake build-essential pkg-config libffi-dev libgmp-dev libssl-dev libtinfo-dev libsystemd-dev zlib1g-dev make g++ tmux git jq wget libncursesw5 libtool autoconf
WORKDIR /app/cabal
ARG CABAL_VERSION=3.2.0.0
RUN wget https://downloads.haskell.org/~cabal/cabal-install-${CABAL_VERSION}/cabal-install-${CABAL_VERSION}-x86_64-unknown-linux.tar.xz && \
    tar -xf cabal-install-${CABAL_VERSION}-x86_64-unknown-linux.tar.xz && \
    rm cabal-install-${CABAL_VERSION}-x86_64-unknown-linux.tar.xz cabal.sig && \
    mv cabal /usr/local/bin/
RUN cabal update
WORKDIR /app/ghc
ARG GHC_VERSION=8.10.2
RUN wget https://downloads.haskell.org/~ghc/${GHC_VERSION}/ghc-${GHC_VERSION}-x86_64-deb10-linux.tar.xz && \
    tar -xf ghc-${GHC_VERSION}-x86_64-deb10-linux.tar.xz && \
    rm ghc-${GHC_VERSION}-x86_64-deb10-linux.tar.xz
WORKDIR /app/ghc/ghc-${GHC_VERSION}
RUN ./configure && make install
WORKDIR /app/libsodium
RUN git clone https://github.com/input-output-hk/libsodium . && \
    git checkout 66f017f1 && \
    ./autogen.sh && \
    ./configure && \
    make && make install
ENV LD_LIBRARY_PATH="/usr/local/lib:$LD_LIBRARY_PATH"
ENV PKG_CONFIG_PATH="/usr/local/lib/pkgconfig:$PKG_CONFIG_PATH"
WORKDIR /app/cardano-node
RUN git clone https://github.com/input-output-hk/cardano-node.git . && \
    git checkout ${CARDANO_NODE_REPO_TAG}
RUN cabal build cardano-cli
RUN mv ./dist-newstyle/build/x86_64-linux/ghc-${GHC_VERSION}/cardano-cli-${CARDANO_CLI_VERSION}/x/cardano-cli/build/cardano-cli/cardano-cli /usr/local/bin/
RUN cardano-cli --version

FROM debian:buster-slim
COPY --from=builder /usr/local/lib/libsodium.so.23 /usr/lib/x86_64-linux-gnu/libgmp.so.10 /usr/lib/x86_64-linux-gnu/liblz4.so.1 /lib/
COPY --from=builder /usr/local/bin/cardano-cli /usr/local/bin/cardano-cli
ENV CARDANO_NODE_SOCKET_PATH=/node-ipc/node.socket
ENTRYPOINT ["cardano-cli"]
CMD [ "--help" ]
