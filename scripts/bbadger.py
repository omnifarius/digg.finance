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
        'user': 'badgeruser',
        'password': 'foo',
        'host': 'localhost',
        'database': 'badger',
        'auth_plugin': 'mysql_native_password',
        'raise_on_warnings': True
}

def getratio():
    with open('./etherscan_api_key.json', mode='r') as key_file:
        key = json.loads(key_file.read())['key']
    bbadger = '0x19d97d8fa813ee2f51ad4b4e04ea08baf4dffc28'
    badger = '0x3472a5a71965499acd81997a54bba8d852c6e53d'
    apicall = f'https://api.etherscan.io/api?module=account&action=tokentx&address={bbadger}&sort=desc&page=1&offset=5&apikey={key}'
    resp = requests.get(apicall)
    logging.debug('Pulling entire bbadger erc20 tx list')
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
        #really need to pull this against the actual hash not hard coded!
        hexb = '0x000000000000000000000000' + badger.split('x')[-1]
        hexbb = '0x000000000000000000000000' + bbadger.split('x')[-1]

        #check for badger -> bbadger tx, data value will be bbadger)
        getlogs=f'https://api.etherscan.io/api?module=logs&action=getlogs&address={bbadger}&fromBlock={block}&toBlock={block}&topic0={topic0}&apikey={key}'
        time.sleep(0.25)
        logging.debug('waiting 0.25 sec to avoid api limits')
        logresp = requests.get(getlogs)
        if logresp.status_code != 200:
            # This means something went wrong.
            raise ApiError('GET /getlogs/ {}'.format(logresp.status_code))
        logging.debug('++++ BBADGER LOGS ++++' + str(logresp.json()))
        if logresp.json()['status'] == '1': #just making sure it was a successful tx
            bbflag = 1
            logging.debug('found a successful bbadger deposit')
            results = logresp.json()['result']
            #print(results)
            for i in results:
                #print(i)
                for j,k in i.items():
                    #print(j,k)
                    if j == 'data':
                        bbval = k
                        #print(bbval)
        #now get the other half of that tx 
        getlogs=f'https://api.etherscan.io/api?module=logs&action=getlogs&address={badger}&fromBlock={block}&toBlock={block}&topic0={topic0}&apikey={key}'
        time.sleep(0.25)
        logging.debug('waiting 0.25 sec to avoid api limits')
        logresp = requests.get(getlogs)
        if logresp.status_code != 200:
            # This means something went wrong.
            raise ApiError('GET /getlogs/ {}'.format(logresp.status_code))
        logging.debug('^^^^ BADGER LOGS ^^^^' + str(logresp.json()))
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
                        bval = k
                        #print(bval)
                        bbb = int(bval,16) / int(bbval,16)
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
            sql = f'INSERT INTO bbadger_history (timestamp, ratio) VALUES (\'{timestamp}\', \'{ratio}\');'
            logging.debug('executing SQL command: ' + sql)
            with connection.cursor() as cursor:
                cursor.execute(sql)
            connection.commit()
            logging.debug(f'bbadger_history table inserted data: {timestamp} {ratio}')
    except Error as e:
        connection.rollback()
        logging.warning('error while writing to bbadger_history table: ',e)
    connection.close()


def main():
    logging.basicConfig(
        level=logging.DEBUG,
        format="%(asctime)s %(relativeCreated)6d %(threadName)s %(levelname)s %(message)s",
        handlers=[
            logging.FileHandler("bbadger.log"),
            logging.StreamHandler()
        ]
    )

    ratio = getratio()
    insert_kpi(ratio)


if __name__ == '__main__':
    main()


