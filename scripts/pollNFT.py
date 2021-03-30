import json
import requests
import mysql.connector
from mysql.connector import connect, Error, errorcode

config = {
        'user': 'badgeruser',
        'password': '',
        'host': 'localhost',
        'database': 'badger',
        'auth_plugin': 'mysql_native_password',
        'raise_on_warnings': True
}

def insert_redeems(user, redeemed, txid):
    unknown, common, rare, legendary = 0,0,0,0
    if redeemed == 15:
        common = 1
        sql = f'REPLACE INTO minted (address, txid, common) VALUES (\'{user}\', \'{txid}\', {common});'

    elif redeemed == 50:
        rare = 1
        sql = f'REPLACE INTO minted (address, txid, rare) VALUES (\'{user}\', \'{txid}\', {rare});'

    elif redeemed == 100:
        legendary = 1
        sql = f'REPLACE INTO minted (address, txid, legendary) VALUES (\'{user}\', \'{txid}\', {legendary});'

    else:
        unknown = 1
        sql = f'REPLACE INTO minted (address, txid, unknown) VALUES (\'{user}\', \'{txid}\', {unknown});'

    try:
        with connect(**config) as connection:
            #sql = f'REPLACE INTO minted (address, txid, common, rare, legendary, unknown) VALUES (\'{user}\', \'{txid}\', {common}, {rare}, {legendary}, {unknown});'
            #logging.debug('executing SQL command: ' + sql)
            with connection.cursor() as cursor:
                cursor.execute(sql)
            connection.commit()
            #logging.debug(f'minted table inserted data: {user} {type}')
    except Error as e:
        connection.rollback()
        #logging.warning('error while writing to minted table: ',e)
    connection.close()

#ID for the NFT themselves:
#card 205 common, 206 rare, 208 legend
#topic1 seems to be the user
def proc_redeem(item):
    print('Process REDEEM event')
    #print(item)
    #print(len(item['data']))
    pineapple_redeemed = round(int(item['data'],16)*pow(10,-18),0)
    user = item['topics'][1]
    user = ('0x' + user[26:len(user)])
    print(user)
    #user = hex(int(item['topics'][1],16))
    #print(user, pineapple_redeemed)
    insert_redeems(user, pineapple_redeemed, item['transactionHash'])

def proc_stake(item):
    #print('Process STAKE event')
    #print(item)
    user = hex(int(item['topics'][1],16))
    data = int(item['data'],16)*pow(10,-18)
    #print(user, data)

def proc_withdraw(item):
    #print('Process WITHDRAW event')
    #print(item)
    user = hex(int(item['topics'][1],16))
    data = int(item['data'],16)*-1*pow(10,-18)
    #print(user, data)

def thing():
    #let's pull all the events for the NFT bdigg contract
    #after I log known events, i should start tracking "latest" block too
    with open('./etherscan_api_key.json', mode='r') as key_file:
        key = json.loads(key_file.read())['key']
    address = '0x7c444720664c7876004bcdfd786ff8c905add5f1'
    apicall = f'https://api.etherscan.io/api?module=logs&action=getLogs&address={address}&startblock=0&endblock=99999999&sort=desc&apikey={key}'
    resp = requests.get(apicall)
    if resp.status_code != 200:
        # This means something went wrong.
        raise ApiError('GET /txlist/ {}'.format(resp.status_code))
    #print(resp.json()['result'])
    #print('---\n---\n---')
    total, stakes, pulls, redemptions = 0, 0, 0, 0
    #item['result'] is basically a dict with address, topics, data, blocknum, ts, hash, etc
    for item in resp.json()['result']:
        if item['topics'][0] == '0x1449c6dd7851abc30abf37f57715f492010519147cc2652fbc38202c18a6ee90':
            #topic1 = user, topic2 = poolid, topic3 = amount
            proc_stake(item)
            stakes += 1
        elif item['topics'][0] == '0x92ccf450a286a957af52509bc1c9939d1a6a481783e142e41e2499f0bb66ebc6':
            #topic1 = user, topic2 = poolid, topic3 = amount
            proc_withdraw(item)
            pulls += 1
        elif item['topics'][0] == '0xf3a670cd3af7d64b488926880889d08a8585a138ff455227af6737339a1ec262':
            #topic1 = user, topic2 = poolid, topic3 = amount
            proc_redeem(item)
            redemptions += 1
        else:
            print('some other event, do something later maybe')
        total += 1
    print('processed ' , total , ' events')
    print('Stakes: ', stakes)
    print('Withdraws: ', pulls)
    print('Redemptions: ', redemptions)


def main():
    #build an async loop to listen for events
    thing()

if __name__ == '__main__':
    main()
