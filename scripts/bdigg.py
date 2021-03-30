import logging
import json
import requests
from web3 import Web3
import time
import statistics
import datetime
import mysql.connector
from mysql.connector import connect, Error, errorcode

config = {
        'user': 'diggsqluser',
        'password': 'foo',
        'host': 'localhost',
        'database': 'digg',
        'auth_plugin': 'mysql_native_password',
        'raise_on_warnings': True
}

def getratio():
    with open('./etherscan_api_key.json', mode='r') as key_file:
        key = json.loads(key_file.read())['key']
    bdigg = '0x7e7e112a68d8d2e221e11047a72ffc1065c38e1a'
    digg = '0x798d1be841a82a273720ce31c822c61a67a601c3'
    apicall = f'https://api.etherscan.io/api?module=account&action=tokentx&address={bdigg}&sort=desc&page=1&offset=5&apikey={key}'
    resp = requests.get(apicall)
    logging.debug('Pulling entire bdigg erc20 tx list')
    if resp.status_code != 200:
        # This means something went wrong.
        raise ApiError('GET /tokentx/ {}'.format(resp.status_code))
    logging.debug('%%%%%%%%%%%%%%%%%% FULL TX LIST %%%%%%%%%%%%%%')
    #print(resp.json()['result']) #full tx list
    ratio = []
    for item in resp.json()['result']:
        bval, bbval = 0,0
        bflag, bbflag = 0,0
        logging.debug('%%% ITEM %%% ' + str(item))
        block = item['blockNumber']
        topic0 = '0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef'
        hexb = '0x000000000000000000000000' + digg.split('x')[-1]
        hexbb = '0x000000000000000000000000' + bdigg.split('x')[-1]

        #check for badger -> bbadger tx, data value will be bbadger)
        getlogs=f'https://api.etherscan.io/api?module=logs&action=getlogs&address={bdigg}&fromBlock={block}&toBlock={block}&topic0={topic0}&apikey={key}'
        time.sleep(0.25)
        logging.debug('waiting 0.25 sec to avoid api limits')
        logresp = requests.get(getlogs)
        if logresp.status_code != 200:
            # This means something went wrong.
            raise ApiError('GET /getlogs/ {}'.format(logresp.status_code))
        logging.debug('++++ BDIGG LOGS ++++' + str(logresp.json()))
        if logresp.json()['status'] == '1': #just making sure it was a successful tx
            bbflag = 1
            logging.debug('found a successful bdigg deposit')
            results = logresp.json()['result']
            #print(results)
            for i in results:
                #print(i)
                for j,k in i.items():
                    #print(j,k)
                    if j == 'data':
                        bbval = int(k,16)*pow(10,-18)
                        #print(bbval)
        #now get the other half of that tx 
        getlogs=f'https://api.etherscan.io/api?module=logs&action=getlogs&address={digg}&fromBlock={block}&toBlock={block}&topic0={topic0}&apikey={key}'
        time.sleep(0.25)
        logging.debug('waiting 0.25 sec to avoid api limits')
        logresp = requests.get(getlogs)
        if logresp.status_code != 200:
            # This means something went wrong.
            raise ApiError('GET /getlogs/ {}'.format(logresp.status_code))
        logging.debug('^^^^ DIGG LOGS ^^^^' + str(logresp.json()))
        if logresp.json()['status'] == '1': #just making sure it was a successful tx
            bflag = 1
            logging.debug('found a successful badger deposit')
            results = logresp.json()['result']
            #print(results)
            for i in results:
                #print(i)
                for j,k in i.items():
                    #print(j,k)
                    if j == 'data' and bbval != 0:
                        bval = int(k,16)*pow(10,-9)
                        #print(bval)
                        bbb = bval / bbval
        if bflag == 1 and bbflag ==1:
            ratio.append(bbb)

    logging.debug(f'Final ratios: {ratio}')
    mode = statistics.mode(ratio)
    logging.debug(f'Mode ratio: {mode}')
    return mode

def insert_kpi(ratio):
    #push current ratio for bbadger to badger into a running history
    timestamp = datetime.datetime.now()
    ratio = str(round(ratio,5))
    try:
        with connect(**config) as connection:
            sql = f'INSERT INTO bdigg_history (timestamp, ratio) VALUES (\'{timestamp}\', \'{ratio}\');'
            logging.debug('executing SQL command: ' + sql)
            with connection.cursor() as cursor:
                cursor.execute(sql)
            connection.commit()
            logging.debug(f'bdigg_history table inserted data: {timestamp} {ratio}')
    except Error as e:
        connection.rollback()
        logging.warning('error while writing to bdigg_history table: ',e)
    connection.close()


def main():
    logging.basicConfig(
        level=logging.DEBUG,
        format="%(asctime)s %(relativeCreated)6d %(threadName)s %(levelname)s %(message)s",
        handlers=[
            logging.FileHandler("bdigg.log"),
            logging.StreamHandler()
        ]
    )

    ratio = getratio()
    insert_kpi(ratio)


if __name__ == '__main__':
    main()


