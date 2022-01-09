# spike_cardano-api

Just playing around with cardano-api

trying to solve

`So I just need a way to verify a transaction has been made, once done, it will send Ada back to the user`

https://developers.cardano.org/docs/integrate-cardano/listening-for-payments-cli

<!-- TOC -->

- [spike_cardano-api](#spike_cardano-api)
  - [Requried](#requried)
  - [startup cardano node and cardano wallet](#startup-cardano-node-and-cardano-wallet)
  - [python](#python)
    - [debug](#debug)
  - [node](#node)
    - [debug](#debug-1)
  - [Ref Doco](#ref-doco)
    - [cardano](#cardano)
    - [node](#node-1)
    - [python](#python-1)
      - [precommit checks](#precommit-checks)

<!-- /TOC -->

## Requried

1. docker installed and running
1. internet connection
1. python (with pyevn)
1. [insomnia](https://insomnia.rest/) (optional)
1. osx (amd64)

## startup cardano node and cardano wallet

1. startup the cardano node and wallet via docker compose. Note that this will take some time to synk. Note this is for the test network!

    ```bash
    wget https://raw.githubusercontent.com/input-output-hk/cardano-wallet/master/docker-compose.yml
    NETWORK=testnet docker-compose up
    ```

1. test your locally runing node and wallet

    ```bash
    # with curl
    curl http://localhost:8090/v2/network/information
    # or with cli (via docker run)
    docker run --network host --rm inputoutput/cardano-wallet network information
    ```

1. curl wallets

    ```bash
    curl -s http://localhost:8090/v2/wallets | jq
    ```

## python

1. build `docker build -t spike_python_cardano-api -f Dockerfile_python .`
1. run `docker run --rm --network host spike_python_cardano-api` to either make new wallets or transfer one tada between testsend and testrecive.
   1. if you get an error "not enough ada" you wil have to add some more tada to testsend (this can only be done once every 24h)
   1. get tada, using either the insomnia file `<repo_root>/insomnia/cardano_Insomnia.yaml` or with `curl` commands to get a unused `addresses` for the testsend wallet `485da76a1f99414b439965c1ce80f517eeb53c0c`. TODO automate this
       * <https://testnets.cardano.org/en/testnets/cardano/tools/faucet/>
       * <https://github.com/input-output-hk/cardano-faucet>

### debug

1. setup your an env var for your project home

    ```bash
    export cardano_api="/Users/onzyone/projects/cardano/spike_cardano-api"
    ```

1. start and attached conntanter that has the cardano cli installed on it. You will alos mount your git repo under `/app/spike_cardano-api` wihtin the container

    ```bash
    docker run --network host --rm -it --entrypoint=/bin/sh \
    -v ${cardano_api}:/app/spike_cardano-api \
    spike_python_cardano-api
    ```

## node

1. build `docker build -t spike_node_cardano-api -f Dockerfile_node .`
1. run `docker run --rm --network host --entrypoint=/bin/bash spike_node_cardano-api`

### debug

## Ref Doco

### cardano

<https://bump.sh/doc/cardano-wallet-diff>
<https://input-output-hk.github.io/cardano-wallet/api/edge/>

### node

<https://www.npmjs.com/package/cardano-api>
<https://github.com/funador/cardano-api>

### python

<https://snyk.io/advisor/python/cardano>
<https://github.com/emesik/cardano-python>
<https://cardano-python.readthedocs.io/en/latest/>

#### precommit checks

1. `pip install pre-commit-hooks`
1. `pre-commit install`
1. `pre-commit run --all-files`
