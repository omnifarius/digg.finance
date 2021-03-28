import logging
import threading
import json
import requests
import mysql.connector
from mysql.connector import connect, Error, errorcode
from web3 import Web3
import datetime
from datetime import datetime
import time
import csv

config = {
        'user': 'diggsqluser',
        'password': 'foo',
        'host': 'localhost',
        'database': 'digg',
        'auth_plugin': 'mysql_native_password',
        'raise_on_warnings': True
}

def getnextrebase(event):
    #load and loop through known rebase tx
    knowntx = []
    try:
        with connect(**config) as connection:
            sql = "SELECT txid FROM rebase_history"
            with connection.cursor() as cursor:
                cursor.execute(sql)
                result = cursor.fetchall()
                #print(result)
                for row in result:
                    #print(row)
                    knowntx.append(row[0])
    except Error as e:
        logging.debug('Error polling rebase_history: %s',e)
    connection.close()
    print('length of known tx')
    print(len(knowntx))

    #load and loop through known failed tx
    failedtx = []
    try:
        with connect(**config) as connection:
            sql = "SELECT txid FROM failed_rebase_tx"
            with connection.cursor() as cursor:
                cursor.execute(sql)
                result = cursor.fetchall()
                #print(result)
                for row in result:
                    #print(row)
                    knowntx.append(row[0])
    except Error as e:
        logging.debug('Error polling failed_rebase_tx: %s',e)
    connection.close()
    print('length of failed tx')
    print(len(failedtx))

### TO DO add a check here to make sure i pulled known and failed tx list.  trying again as needed !!!

#### Need to add startblock to the equation as lastknownrebaseblock so i'm not pulling the whole list every time!
#### or maybe not if I'm just checking the length of said list
    while not event.isSet():
        #ok now let's pull all the rebase tx we can find from the digg contract
        logging.debug('===starting event loop===')
        with open('./etherscan_api_key.json', mode='r') as key_file:
            key = json.loads(key_file.read())['key']
        address = '0xBd5d9451E004fc495F105cEaB40d6c955E4192bA'
        apicall = f'https://api.etherscan.io/api?module=account&action=txlist&address={address}&startblock=0&endblock=99999999&sort=asc&apikey={key}'
        resp = requests.get(apicall)
        logging.debug('Pulling entire digg tx list')
        event.wait(0.25) #quick wait after api call
        if resp.status_code != 200:
            # This means something went wrong.
            raise ApiError('GET /txlist/ {}'.format(resp.status_code))
        #print(resp.json()['result']) #full tx list
        newsupply=0 #set a default new supply
        for item in resp.json()['result']:
            if item['input'] == '0xaf14052c' and item['hash'] not in knowntx and item['hash'] not in failedtx:
                print('found an unknown (success/failed) rebase!')
                #print(item['timeStamp'])
                #print(datetime.utcfromtimestamp(int(item['timeStamp'])))
                #print(item['txreceipt_status'])
                print(item['hash'])
                #block number to check rebase tx logs
                block = item['blockNumber'] #must be from that resp.json for loop
                #topic 0 seems to be the new supply
                topic_0 = '0x72725a3b1e5bd622d6bcd1339bb31279c351abe8f541ac7fd320f24e1b1641f2'
                #digg address
                diggaddr = '0x798D1bE841a82a273720CE31c822C61a67a601C3'
                #piece together the variables into the api call
                apicall=f'https://api.etherscan.io/api?module=logs&action=getLogs&fromBlock={block}&toBlock={block}&address={diggaddr}&topic0={topic_0}&apikey={key}'
                event.wait(0.25) #quick pause to avoid api limits
                logging.debug('waiting 0.25 sec to avoid api limits')
                diggresp = requests.get(apicall)
                logging.debug('Pulling unknown tx from the list')
                if resp.status_code != 200:
                    # This means something went wrong.
                    raise ApiError('GET /getLogs/ {}'.format(resp.status_code))
                print(diggresp.json())
                if diggresp.json()['status'] != '0': #just making sure it was a successful tx
                    logging.debug('found both unknown AND successful tx so adding to db')
                    results = diggresp.json()['result']
                    #print(results)
                    for i in results:
                        for j,k in i.items():
                            #print(j,k)
                            if j == 'data':
                                hexsupply = k
                                newsupply = round(int(hexsupply,16)*pow(10,-9),3)

                    #add the rebase that wasn't previously found in the txid list
                    data = (item['hash'], str(datetime.utcfromtimestamp(int(item['timeStamp']))), str(newsupply), block)
                    sql = f'INSERT INTO rebase_history (txid, timestamp, supply, block) VALUES {data}'
                    #sql="" #fake do nothing injection while testing...
                    print(sql)
                    try:
                        with connect(**config) as connection:
                            with connection.cursor() as cursor:
                                cursor.execute(sql)
                                connection.commit()
                                logging.debug(f'rebase_history data inserted: {data}')
                                logging.info('event set to break loop')
                                event.set()  #this breaks out of the while loop
                    except Error as e:
                        connection.rollback()
                        logging.debug('Error while inserting rebase_history: %s',e)
                    connection.close()
                else:
                    data = str(item['hash'])
                    sql = f"INSERT INTO failed_rebase_tx VALUES (\'{data}\')"
                    print(sql)
                    try:
                        with connect(**config) as connection:
                            with connection.cursor() as cursor:
                                cursor.execute(sql)
                                connection.commit()
                                logging.debug(f'failed_tx data inserted: {data}')
                    except Error as e:
                        connection.rollback()
                        print(e)
                        logging.debug('Error while interting failed_tx: %s',e)
                    connection.close()
                    logging.debug('logged a failed tx')
        logging.debug('--- waiting 30 seconds to try again ---')
        event.wait(30)

def calculator():
    logging.debug('!!! Starting calculations !!!')
    latesttx = '0x0'
    latestts = datetime(2021, 1, 22, 0, 0, 0) #ie before creation!
    latestsup = 4000
    prevtx = '0x1'
    prevts = datetime(2021, 1, 22, 0, 0, 0) #ie before creation!
    prevsup = 0
    delta = 0
    rbpct = 0
    streak = 0

    #load and loop through known rebase tx
    try:
        with connect(**config) as connection:
            sql = "SELECT txid,timestamp,supply FROM rebase_history ORDER BY timestamp ASC"
            with connection.cursor() as cursor:
                cursor.execute(sql)
                result = cursor.fetchall()
                #print(result)
                for row in result:
                    #print(row)
                    if len(row) > 1:
                        if latestts < row[1]:
                            delta = round(row[2] - latestsup,3)
                            rbpct = round(delta / latestsup * 100, 2)
                            latesttx = row[0]
                            latestts = row[1]
                            latestsup = round(row[2],3)
                            data = (str(latesttx), str(latestts), str(latestsup), str(delta), str(rbpct))
                            sql2 = f"REPLACE INTO calc_rebase (txid, timestamp, supply, delta, rbpct) VALUES {data}"
                            cursor.execute(sql2)
            connection.commit()
            logging.debug(f'calc_rebase table inserted data: {data}')
    except Error as e:
        connection.rollback()
        logging.warning('error while writing to calc_rebase table: ',e)
    connection.close()

"""
def outputcsv():
    #ok, now also create the csv from this new data
    try:
        with connect(**config) as connection:
            sql = "SELECT * FROM calc_rebase"
            with connection.cursor() as cursor:
                cursor.execute(sql)
                result = cursor.fetchall()
                for row in result:
                    with open('./diggrebase.csv', mode='a') as rebase_file:
                        rebase_writer = csv.writer(rebase_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
                        rebase_writer.writerow(line.split(",",3))
                logging.debug('finished writing to file')
    except Error as e:
        logging.debug('Error polling calc_rebase: %s',e)
    connection.close()
"""

def main():
    logging.basicConfig(
        level=logging.DEBUG,
        format="%(asctime)s %(relativeCreated)6d %(threadName)s %(levelname)s %(message)s",
        handlers=[
            logging.FileHandler("diggfiupdater.log"),
            logging.StreamHandler()
        ]
    )

    #this should be on a daily cycle
    #crontab restarts daily at 8pm UTC
    event = threading.Event()
    rebase_thread = threading.Thread(name='RebaseThread', target=getnextrebase, args=(event,))
    rebase_thread.start()

    while not event.isSet():
        try:
            logging.debug("Checking in from main thread, then waiting 1 min, keyboard interrupt exception")
            logging.debug("In theory, this will loop here until data is inserted into rebase_history")
            event.wait(60)
        except KeyboardInterrupt:
            event.set()
            break

    #after rebase occurred, so run the calculations
    calculator()
    #outputcsv()


if __name__ == '__main__':
    main()
