#!/usr/bin/env python3

# Distroless's test.sh runs pylint on all python files, but this module will not exist
# pylint: disable=import-error
from cardano.wallet import WalletService
from cardano.wallet import Wallet
from cardano.backends.walletrest import WalletREST
from mnemonic import Mnemonic
from loguru import logger
import snoop
import json
import time

def create_test_wallet(wallet):

# https://cardano-python.readthedocs.io/en/latest/wallet.html#creating-wallets

    # get the values to create a wallets
    wallet_name = wallet.get('name')
    wallet_mnemonic = wallet.get('mnemonic')
    wallet_passphrase = wallet.get('passphrase')

    # connect to the wallet service (in this demo running with docker compose)
    ws = WalletService(WalletREST(port=8090))

    # create wallets
    wal = ws.create_wallet(
        name=f"{wallet_name}",
        mnemonic=f"{wallet_mnemonic}",
        passphrase=f"{wallet_passphrase}",
    )
    # return wallet value
    return wal

def get_wallets():

    ws = WalletService(WalletREST(port=8090))
    wals = ws.wallets()

    return wals

def get_wallet(wallet_id):

    ws = WalletService(WalletREST(port=8090))
    try:
        wal = ws.wallet(wallet_id)
    except ValueError:
        return False
    return wal

def get_wallet_unused_address(wallet_id):

    ws = WalletService(WalletREST(port=8090))
    wal = ws.wallet(wallet_id)
    wal_unused = wal.first_unused_address()
    return wal_unused

def get_wallet_ballance(wallet_id):

    ws = WalletService(WalletREST(port=8090))
    wal = ws.wallet(wallet_id)
    wal_balance = wal.balance()
    return wal_balance

# TODO automate this ... right now it is manually done via this page: https://testnets.cardano.org/en/testnets/cardano/tools/faucet/
def put_wallet_funds(wallet_id, ammount, passphrase):

    wal = Wallet(wallet_id, backend=WalletREST(port=8090), passphrase=passphrase)
    wal.sync_progress()
    logger.info(get_wallet_ballance(wallet_id))
    wal = get_wallet(wallet_id)
    _ammount = float("{:.2f}".format(ammount))
    wal.transfer(ammount, passphrase=passphrase)

def get_transactions():
    ws = WalletService(WalletREST(port=8090))

@snoop
def make_transaction(send_wal_id, ammount, passphrase, to_unused_address):

    wal = Wallet(send_wal_id, backend=WalletREST(port=8090), passphrase=passphrase)
    test_send_funds = get_wallet_ballance(send_wal_id)
    logger.info(f"wal_id {send_wal_id}, has in {test_send_funds} funds and is going to be sending {ammount} to {to_unused_address}")
    wal.transfer(to_unused_address, ammount)

def testsend_to_testrecive(wallets):

    wal_id_test_recive = wallets[1].get("id")
    wal_name_test_recive = wallets[1].get("name")
    logger.info(f"getting unused_address for wallet: {wal_name_test_recive}, with id {wal_id_test_recive}")
    test_recive_unused = get_wallet_unused_address(f"{wal_id_test_recive}")
    logger.info(f"first unused for {wal_name_test_recive} wallet {test_recive_unused}")

    wal_id_test_send = wallets[0].get("id")
    wal_name_test_send = wallets[0].get("name")
    ammount = wallets[0].get("ammount")
    passphrase = wallets[0].get("passphrase")

    logger.info(f"sending tada from wallet: {wal_name_test_send}, with id {wal_id_test_send}")
    make_transaction(wal_id_test_send, ammount, passphrase, test_recive_unused)

def testrecive_to_testsend(wallets):

    wal_id_test_recive = wallets[0].get("id")
    wal_name_test_recive = wallets[0].get("name")
    logger.info(f"getting unused_address for wallet: {wal_name_test_recive}, with id {wal_id_test_recive}")
    test_recive_unused = get_wallet_unused_address(f"{wal_id_test_recive}")
    logger.info(f"first unused for {wal_name_test_recive} wallet {test_recive_unused}")

    wal_id_test_send = wallets[1].get("id")
    wal_name_test_send = wallets[1].get("name")
    ammount = wallets[1].get("ammount")
    passphrase = wallets[1].get("passphrase")

    logger.info(f"sending tada from wallet: {wal_name_test_send}, with id {wal_id_test_send}")
    make_transaction(wal_id_test_send, ammount, passphrase, test_recive_unused)

def create_mnemonic():

    mnemo = Mnemonic("english")
    words = mnemo.generate(strength=256)
    logger.info(f"mnemonic: {words}")

def main():

# if need a new wallet, you can use this to create the mnemonic
#    create_mnemonic()

    # get the wallets from the wallets.json file
    with open('wallets.json') as json_file:
        wallets = json.load(json_file)

    logger.debug(f"wallets loaded from file: {wallets}")

    for each_wallet in wallets:

        # if this is true do now make wallet
        wal_id = each_wallet.get('id')
        wal_name = each_wallet.get('name')
        wal_info = get_wallet(wal_id)
        # cardano.backends.walletrest.exceptions.NotFound exception will be raised.
        logger.info(f"wallet details for {wal_name}, with id {wal_id}: {wal_info}")

        if wal_info is False:
            wal_id = create_test_wallet(each_wallet)
            logger.info(f"wallet was created: {wal_id}")

        wal_balance = get_wallet_ballance(wal_id)
        logger.info(f"wallet {wal_name}, with id {wal_id} has a ballance of: {wal_balance}")

# start of the get, ada and send ada example
    testsend_to_testrecive(wallets)

# send back :)
#    testrecive_to_testsend(wallets)

if __name__ == '__main__':
    main()
