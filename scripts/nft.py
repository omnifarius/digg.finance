import logging
import json
import requests
from web3 import Web3
import time
import statistics
import datetime
from datetime import datetime,timedelta
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

def pirate(amt):
    #function that returns pineapples accrued to date
    z = 1.3
    ppd = z * pow(amt*1000, 0.25)
    pps = ppd / 86400

    #now = datetime.datetime.now()
    #seconds = (now - ts).seconds

    return ppd

def getknown():
    knowntx = []
    try:
        with connect(**config) as connection:
            sql = f'SELECT txid FROM nft'
            logging.debug('executing SQL command: ' + sql)
            with connection.cursor() as cursor:
                cursor.execute(sql)
                result = cursor.fetchall()
                for row in result:
                    knowntx.append(row[0])
    except Error as e:
        connection.rollback()
        logging.warning('error while polling nft table: ',e)
    connection.close()
    return knowntx

def gettx():
    #get the known tx first, by txid
    knowntx = getknown()
    logging.debug(f'known transactions found, ' + str(len((knowntx))))
    with open('./etherscan_api_key.json', mode='r') as key_file:
        key = json.loads(key_file.read())['key']
    nftaddr = '0x7c444720664c7876004bcdfd786ff8c905add5f1'
    apicall = f'https://api.etherscan.io/api?module=account&action=tokentx&address={nftaddr}&sort=desc&apikey={key}'
    resp = requests.get(apicall)
    logging.debug('Pulling entire nft meme erc20 tx list')
    if resp.status_code != 200:
        # This means something went wrong.
        raise ApiError('GET /tokentx/ {}'.format(resp.status_code))
    logging.debug('%%%%%%%%%%%%%%%%%% FULL TX LIST %%%%%%%%%%%%%%')
    #print(resp.json()['result']) #full tx list
    #ratio = []
    for item in resp.json()['result']:
        logging.debug('%%% ITEM %%% \n' + str(item))
        transaction = item['hash']
        timestamp = str(datetime.utcfromtimestamp(int(item['timeStamp'])))
        amount = int(item['value'])*pow(10,-18)
        address = item['from']
        logging.debug(f' xxxx FM ADDR xxxx: ' + address)
        if item['from'] == nftaddr:
            address = item['to']
            logging.debug(f' xxxx TO ADDR xxxx: ' + address)
            logging.debug('removed some bdigg tx found')
            amount = -1*amount
        if transaction not in knowntx:
            logging.debug('Inserting unknown tx')
            logging.debug(item)
            insert_table(transaction, timestamp, address, amount)
        #else:
            #logging.debug('Skipping known tx')

def insert_table(txid, ts, addr, amt):
    #push current ratio for bbadger to badger into a running history
    if amt > 0:
        ppd = pirate(amt)
    else:
        ppd = 0
    try:
        with connect(**config) as connection:
            sql = f'INSERT INTO nft (txid, timestamp, address, amount, pirate) VALUES (\'{txid}\', \'{ts}\', \'{addr}\', \'{amt}\', \'{ppd}\');'
            logging.debug('executing SQL command: ' + sql)
            with connection.cursor() as cursor:
                cursor.execute(sql)
            connection.commit()
            logging.debug(f'nft table inserted data: {txid} {ts} {addr} {amt}')
    except Error as e:
        connection.rollback()
        logging.warning('error while writing to nft table: ',e)
    connection.close()


def main():
    logging.basicConfig(
        level=logging.DEBUG,
        format="%(asctime)s %(relativeCreated)6d %(threadName)s %(levelname)s %(message)s",
        handlers=[
            logging.FileHandler("nft.log"),
            logging.StreamHandler()
        ]
    )

    gettx()


if __name__ == '__main__':
    main()


