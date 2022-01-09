import os

import requests

# expected env vars:
# export API_KEY =
# export WALLET =

def get_assets(asset_endpoint):
    API_KEY = os.getenv('API_KEY')
    base_url = 'https://cardano-mainnet.blockfrost.io'
    base_api = '/api/v0'
    base_headers = {'project_id': f'{API_KEY}'}

    uri = f'{base_url}{base_api}{asset_endpoint}'
    res = requests.get(uri, headers=base_headers)

    return res.json()


def sort_assets(cnft_in_wallet):

    staff = []
    sword = []
    bow = []
    for each in cnft_in_wallet:
        asset_id = each['unit']
        # get only dlc assets
        if '9e9e948d' in asset_id:
            #      print(asset_id)
            asset_endpoint = f'/assets/{asset_id}'
            dlc_data = get_assets(asset_endpoint)
#      print(dlc_data)
            metat_data = dlc_data['onchain_metadata']

            if 'bow' in metat_data['Type'].lower():
                bow.append(dlc_data)

            if 'staff' in metat_data['Type'].lower():
                staff.append(dlc_data)

            if 'sword' in metat_data['Type'].lower():
                sword.append(dlc_data)

    return bow, staff, sword


def get_metat_data(data):

    return data['onchain_metadata']


def print_bow(bow):
    #    print(bow)
    print('===== bow(s) =====')
    for each in bow:
        metat_data = get_metat_data(each)
        print(f"name: {metat_data['name']}")
        print(f"damage: {metat_data['Damage']}")
        print(f"grip: {metat_data['grip']}")
        print(f"bow: {metat_data['bow']}")


def print_staff(staff):
    #    print(staff)
    print('===== staff(s) =====')
    for each in staff:
        metat_data = get_metat_data(each)
        print(f"name: {metat_data['name']}")
        print(f"damage: {metat_data['Damage']}")
        print(f"shaft: {metat_data['shaft']}")
        print(f"head: {metat_data['head']}")


def print_sword(sword):
    #    print(sword)
    print('===== sword(s) =====')
    for each in sword:
        metat_data = get_metat_data(each)
        print(f"name: {metat_data['name']}")
        print(f"damage: {metat_data['Damage']}")
        print(f"hilt: {metat_data['hilt']}")
        print(f"blade: {metat_data['blade']}")


def main():

    # get assets in wallet

    wallet = os.getenv('WALLET')
    asset_endpoint = f'/accounts/{wallet}/addresses/assets'
    cnft_in_wallet = get_assets(asset_endpoint)

    bow, staff, sword = sort_assets(cnft_in_wallet)

    if not bow:
        print('you have no bow(s)')
    else:
        print_bow(bow)

    if not staff:
        print('you have no staff(s)')
    else:
        print_staff(staff)

    if not sword:
        print('you have no sword(s)')
    else:
        print_sword(sword)


if __name__ == '__main__':
    main()
