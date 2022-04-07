# spike_cardano-api

Just playing around with cardano-api and cardano-cli

trying to solve

`So I just need a way to verify a transaction has been made, once done, it will send Ada back to the user`

https://developers.cardano.org/docs/integrate-cardano/listening-for-payments-cli

- [spike_cardano-api](#spike_cardano-api)
  - [Required](#required)
  - [startup cardano node and cardano wallet](#startup-cardano-node-and-cardano-wallet)
  - [python](#python)
  - [test nft](#test-nft)
    - [wallet and keys setup](#wallet-and-keys-setup)
    - [nft meta-data](#nft-meta-data)
    - [debug](#debug)
    - [debug](#debug-1)
  - [Ref Doco](#ref-doco)
    - [cardano](#cardano)
    - [node](#node)
    - [cardano-wallet cli](#cardano-wallet-cli)
    - [cardano node helm chart](#cardano-node-helm-chart)
    - [minting](#minting)
    - [python](#python-1)
      - [precommit checks](#precommit-checks)

## Required

1. docker installed and running
1. internet connection
1. python (with pyevn)
1. ipfs <https://docs.ipfs.io/install/command-line/#macos>
1. [insomnia](https://insomnia.rest/) (optional)
1. osx (amd64)
   1. updated for osx (M1)

## startup cardano node and cardano wallet

1. startup the cardano node and wallet via docker compose. Note that this will take some time to synk. Note this is for the test network!
    ```bash
    wget https://raw.githubusercontent.com/input-output-hk/cardano-wallet/master/docker-compose.yml
    NETWORK=testnet docker-compose up
    ```
  1. if you have a M1 Mac, you will have to use the docker-compose file in this repo:
    `CARDANO_NETWORK=testnet docker compose up -d`
1. test your locally running node and wallet
    ```bash
    # with curl
    curl http://localhost:8091/v2/network/information -s | jq .sync_progress
    # or with cardano-wallet cli (via docker run)
    docker run --network host --rm inputoutput/cardano-wallet network information
    # or with cardano-cli
    docker run --rm -v spike-cardano-api_node-ipc:/node-ipc islishude/cardano-cli query tip --testnet-magic 1097911063
    ```
1. curl wallets
    ```bash
    curl -s http://localhost:8091/v2/wallets | jq
    ```

## python

1. build `docker build -t spike_python_cardano-api -f Dockerfile_python .`
1. run `docker run --rm --network host spike_python_cardano-api` to either make new wallets or transfer one tada between testsend and testrecive.
   1. if you get an error "not enough ada" you wil have to add some more tada to testsend (this can only be done once every 24h)
   1. get tada, using either the insomnia file `<repo_root>/insomnia/cardano_Insomnia.yaml` or with `curl` commands to get a unused `addresses` for the testsend wallet `485da76a1f99414b439965c1ce80f517eeb53c0c`. TODO automate this
       * <https://testnets.cardano.org/en/testnets/cardano/tools/faucet/>
       * <https://github.com/input-output-hk/cardano-faucet>

## test nft

The following commands are created based on these pages:
<https://devslug.com/how-to-mint-an-nft-on-cardano-testnet-using-the-command-line>
<https://developers.cardano.org/docs/native-tokens/minting-nfts>
<https://developers.cardano.org/docs/native-tokens/minting/#directory-structure>

The following docker command explained,

  * `-v spike-cardano-api_node-ipc:/node-ipc` use the socket from the running node
  * `-v "$(PWD):/pwd"` mount the current dir into the the container
  * `-w /pwd` make the dir in the container writable
  * `islishude/cardano-cli` cli image name

### wallet and keys setup

1. start cardano-cli and run all the following commands in side the container
    ```bash
      docker run \
      -it \
      --rm \
      --entrypoint=/bin/bash \
      -v spike-cardano-api_node-ipc:/node-ipc \
      -v "$(PWD):/pwd" \
      -e CARDANO_NODE_SOCKET_PATH=/node-ipc/node.socket \
      -w /pwd \
      uniqmuz/cardano-cli:1.30.1
    ```
1. setup a few vars:
    ```bash
      testnet="--testnet-magic 1097911063"
    ```
1. Generate the payment keys:
    ```bash
      cardano-cli address key-gen \
      --verification-key-file payment.vkey \
      --signing-key-file payment.skey
    ```
1. Generate an address of the payment keys
    ```bash
      cardano-cli address build \
      --payment-verification-key-file payment.vkey \
      --out-file payment.addr \
      ${testnet}
    ```
1. create variable for payment_address `payment_address=$(cat payment.addr)`
1. Fund the address (ensure that your node sync process is 100%)
    ```bash
      cardano-cli query utxo \
      --address ${payment_address} \
      ${testnet}
    ```
   * if you get errors, checkout out this [stackoverflow](https://stackoverflow.com/questions/69274218/decoderfailure-in-cardano-cli/71730916#71730916)
1. Export protocol parameters
    ```bash
        cardano-cli query protocol-parameters \
        --testnet-magic 1097911063 \
        --out-file protocol.json
    ```
1. Generate the policy keys
    ```bash
      cardano-cli address key-gen \
          --verification-key-file policy/policy.vkey \
          --signing-key-file policy/policy.skey
    ```
1. Write the Policy Script
    ```bash
      echo "{" >> policy/policy.script
      echo "  \"type\": \"all\"," >> policy/policy.script
      echo "  \"scripts\":" >> policy/policy.script
      echo "  [" >> policy/policy.script
      echo "   {" >> policy/policy.script
      echo "     \"type\": \"sig\"," >> policy/policy.script
      echo "     \"keyHash\": \"$(cardano-cli address key-hash --payment-verification-key-file policy/policy.vkey)\"" >> policy/policy.script
      echo "   }" >> policy/policy.script
      echo "  ]" >> policy/policy.script
      echo "}" >> policy/policy.script
    ```
1. Generate the PolicyID
    ```bash
      cardano-cli transaction policyid \
      --script-file ./policy/policy.script >> policy/policyID
    ```

### nft meta-data

1. upload an image to IPFS ... say with <https://app.pinata.cloud>
   * You will get the ipfs_hash from here
1. Encode the NFT's name in base-16
    ```bash
    realtokenname="ACSUAR001"
    tokenname=$(echo -n $realtokenname | xxd -b -ps -c 80 | tr -d '\n')
    ipfs_hash="QmPbuwsYuyNG25S7UtCLhVFSTYqBTsru4Pj8CsFqj2fZeo"
    ```
1. Create the metadata, you can see this doco for the structure of the file: <https://github.com/cardano-foundation/CIPs/tree/master/CIP-0025>. It needs to be saved as a `metadata.json` file.
1. Metadata on the fly
      ```bash
      echo "{" >> metadata.json
      echo "  \"721\": {" >> metadata.json
      echo "    \"$(cat policy/policyID)\": {" >> metadata.json
      echo "      \"$(echo ${realtokenname})\": {" >> metadata.json
      echo "        \"name\": \"Test NFT with name ACSUAR001\"," >> metadata.json
      echo "        \"id\": \"1\"," >> metadata.json
      echo "        \"Made With\": \"VQGAN-CLIP\"," >> metadata.json
      echo "        \"Text Prompts\": \"A clown shitting under a rainbow\"," >> metadata.json
      echo "        \"Optimising\": \"Adam\"," >> metadata.json
      echo "        \"Seed\": \"N/A\"," >> metadata.json
      echo "        \"image\": \"ipfs://$(echo ${ipfs_hash})\"," >> metadata.json
      echo "        \"mediaType\": \"image/png\"" >> metadata.json
      echo "      }" >> metadata.json
      echo "    }" >> metadata.json
      echo "  }" >> metadata.json
      echo "}" >> metadata.json
      ```
1. you can validate the metadata <https://pool.pm/test/metadata>
   * [test metadata](https://pool.pm/test/metadata?metadata=%257B%2522721%2522%253A%257B%2522415319c73546ee4cd7aff445c01a06c8a82ff11dbf97a727f1ee8740%2522%253A%257B%2522ACSUAR001%2522%253A%257B%2522description%2522%253A%2522A%2520clown%2520shitting%2520under%2520a%2520rainbow%2522%252C%2522id%2522%253A%25221%2522%252C%2522image%2522%253A%2522ipfs%253A%252F%252FQmPbuwsYuyNG25S7UtCLhVFSTYqBTsru4Pj8CsFqj2fZeo%2522%252C%2522name%2522%253A%2522ACSUAR001%2520Test%2520NFT%2522%257D%257D%257D%257D)
1. Gather information needed to build the transaction
    ```bash
      cardano-cli query utxo \
      --address ${payment_address} \
      ${testnet}
    ```
1. Create vars, (note that some of these files are created in the above steps)
    ```bash
        fee="1586172"
        first_nft_owner_address="addr_test1qzlujn8r7sjfj955gqulgar2p047v2f9pv3wpdr5ymd6ehv44ky4je5w8gqu4t0qnxahphnaw59v2ntl6r9zerwglugqes0yas"
        policyid=$(cat policy/policyID)
        script="policy/policy.script"
        tokenamount=1
        tokenname="414353554152303031"
        txhash="98e26cdd157b65864f18c4cde6d555dae26a0203473a569337c9664d8f68aead"
        txix="0"
        output="0"
    ```
1. make sure all the values that are required for the txt are set
    ```bash
      echo [fee] This is estimated to cost \"${fee}\" lovelace
      echo [first_nft_owner_address] NFT will be sent to address \"${first_nft_owner_address}\"
      echo [output] Output is set to \"${output}\"
      echo [payment_address] NFT will be generated by payment address \"${payment_address}\"
      echo [policyid] The PolicyID is \"${policyid}\"
      echo [script] The policy script is \"${script}\"
      echo [tokenamount] We are going to mint \"${tokenamount}\" tokens
      echo [tokenname] The token name in hexadecimal is \"${tokenname}\"
      echo [txhash][txix] This transaction will be funded by TxHash \"${txhash}\" using TxIx \"${txix}\"
    ```
1. Build the transaction (if you see errors with this command, have a look at the `Build the transaction` section of this page: <https://devslug.com/how-to-mint-an-nft-on-cardano-testnet-using-the-command-line>)
    ```bash
      cardano-cli transaction build \
      ${testnet} \
      --alonzo-era \
      --tx-in ${txhash}#${txix} \
      --tx-out ${first_nft_owner_address}+${fee}+"${tokenamount} ${policyid}.${tokenname}" \
      --change-address ${payment_address} \
      --mint="${tokenamount} ${policyid}.${tokenname}" \
      --minting-script-file ${script} \
      --metadata-json-file metadata.json \
      --witness-override 2 \
      --out-file matx.raw
    ```
1. Sign the transaction
    ```bash
        cardano-cli transaction sign \
        --signing-key-file payment.skey \
        --signing-key-file policy/policy.skey \
        ${testnet} \
        --tx-body-file matx.raw \
        --out-file matx.signed
    ```
1. Submit the transaction to the blockchain
    ```bash
      cardano-cli transaction submit \
      --tx-file matx.signed \
      --testnet-magic 1097911063
    ```


### debug

1. setup your an env var for your project home
    ```bash
    export cardano_api="/Users/onzyone/projects/cardano/spike_cardano-api"
    ```

1. start and attached container that has the cardano cli installed on it. You will alos mount your git repo under `/app/spike_cardano-api` within the container
    ```bash
    docker run --network host --rm -it --entrypoint=/bin/sh \
    -v ${cardano_api}:/app/spike_cardano-api \
    spike_python_cardano-api
    ```

### debug

## Ref Doco

### cardano

[testnet expore](https://explorer.cardano-testnet.iohkdev.io/en.html)
<https://bump.sh/doc/cardano-wallet-diff>
[cardano-wallet rest ref](https://input-output-hk.github.io/cardano-wallet/api/edge/)
[pool.pm testnet?](https://github.com/SmaugPool/pool.pm/issues/5)

### node

<https://www.npmjs.com/package/cardano-api>
<https://github.com/funador/cardano-api>

### cardano-wallet cli

<https://input-output-hk.github.io/cardano-wallet/user-guide/cli>

### cardano node helm chart

<https://github.com/regel/cardano-charts>

### minting

[minting-native-tokens-on-cardano.sh](https://gist.github.com/HT-Moh/c4feaf753ac4680cef8556bfc9c387d1)
[the-ultimate-guide-to-minting-nfts-on-the-cardano-blockchain]https://ruttkowa.medium.com/the-ultimate-guide-to-minting-nfts-on-the-cardano-blockchain-a8f914d3b2a1

### python

<https://snyk.io/advisor/python/cardano>
<https://github.com/emesik/cardano-python>
<https://cardano-python.readthedocs.io/en/latest/>

#### precommit checks

1. `pip install pre-commit-hooks`
1. `pre-commit install`
1. `pre-commit run --all-files`
