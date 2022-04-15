import os

from blockfrost import ApiError
from blockfrost import ApiUrls
from blockfrost import BlockFrostApi

api = BlockFrostApi(
    project_id=os.getenv('API_KEY'),  # or export environment variable BLOCKFROST_PROJECT_ID
    # optional: pass base_url or export BLOCKFROST_API_URL to use testnet, defaults to ApiUrls.mainnet.value
    base_url=ApiUrls.mainnet.value,
)
try:
    health = api.health()
    print(health)   # prints object:    HealthResponse(is_healthy=True)
    health = api.health(return_type='json')  # Can be useful if python wrapper is behind api version
    print(health)   # prints json:      {"is_healthy":True}
    health = api.health(return_type='pandas')
    print(health)   # prints Dataframe:         is_healthy
    #                       0         True

    account_rewards = api.account_rewards(
        stake_address='stake1ux3g2c9dx2nhhehyrezyxpkstartcqmu9hk63qgfkccw5rqttygt7',
        count=20,
    )
    print(account_rewards[0].epoch)  # prints 221
    print(len(account_rewards))  # prints 20

    account_rewards = api.account_rewards(
        stake_address='stake1ux3g2c9dx2nhhehyrezyxpkstartcqmu9hk63qgfkccw5rqttygt7',
        count=20,
        gather_pages=True,  # will collect all pages
    )
    print(account_rewards[0].epoch)  # prints 221
    print(len(account_rewards))  # prints 57

    address = api.address(
        address='addr1qxqs59lphg8g6qndelq8xwqn60ag3aeyfcp33c2kdp46a09re5df3pzwwmyq946axfcejy5n4x0y99wqpgtp2gd0k09qsgy6pz',
    )
    print(address.type)  # prints 'shelley'
    for amount in address.amount:
        print(amount.unit)  # prints 'lovelace'

except ApiError as e:
    print(e)
