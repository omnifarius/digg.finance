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

def insert_sql(address, bdigg, pineapple, pirate):
    try:
        with connect(**config) as connection:
            sql = f'REPLACE INTO nftp (address, bdigg, pineapple, pirate) VALUES (\'{address}\', \'{bdigg}\', \'{pineapple}\', \'{pirate}\')'
            logging.debug('executing SQL command: ' + sql)
            with connection.cursor() as cursor:
                cursor.execute(sql)
            connection.commit()
            logging.debug(f'nftp table inserted data: {address} {bdigg} {pineapple} {pirate}')
    except Error as e:
        connection.rollback()
        logging.warning('error while writing to nftp table: ',e)
    connection.close()

def getcontract():
    endpoint = 'https://mainnet.infura.io/v3/foo'
    web3 = Web3(Web3.HTTPProvider(endpoint))
    abi = '[{"inputs":[{"internalType":"address","name":"_controller","type":"address"},{"internalType":"contract IERC1155","name":"_memeLtdAddress","type":"address"},{"internalType":"contract IERC20","name":"_tokenAddress","type":"address"}],"payable":false,"stateMutability":"nonpayable","type":"constructor"},{"anonymous":false,"inputs":[{"indexed":false,"internalType":"uint256","name":"poolId","type":"uint256"},{"indexed":false,"internalType":"uint256","name":"cardId","type":"uint256"},{"indexed":false,"internalType":"uint256","name":"points","type":"uint256"},{"indexed":false,"internalType":"uint256","name":"mintFee","type":"uint256"},{"indexed":false,"internalType":"uint256","name":"releaseTime","type":"uint256"}],"name":"CardAdded","type":"event"},{"anonymous":false,"inputs":[{"indexed":true,"internalType":"address","name":"previousOwner","type":"address"},{"indexed":true,"internalType":"address","name":"newOwner","type":"address"}],"name":"OwnershipTransferred","type":"event"},{"anonymous":false,"inputs":[{"indexed":false,"internalType":"address","name":"account","type":"address"}],"name":"Paused","type":"event"},{"anonymous":false,"inputs":[{"indexed":true,"internalType":"address","name":"account","type":"address"}],"name":"PauserAdded","type":"event"},{"anonymous":false,"inputs":[{"indexed":true,"internalType":"address","name":"account","type":"address"}],"name":"PauserRemoved","type":"event"},{"anonymous":false,"inputs":[{"indexed":false,"internalType":"uint256","name":"poolId","type":"uint256"},{"indexed":false,"internalType":"address","name":"artist","type":"address"},{"indexed":false,"internalType":"uint256","name":"periodStart","type":"uint256"}],"name":"PoolAdded","type":"event"},{"anonymous":false,"inputs":[{"indexed":true,"internalType":"address","name":"user","type":"address"},{"indexed":false,"internalType":"uint256","name":"poolId","type":"uint256"},{"indexed":false,"internalType":"uint256","name":"amount","type":"uint256"}],"name":"Redeemed","type":"event"},{"anonymous":false,"inputs":[{"indexed":true,"internalType":"address","name":"user","type":"address"},{"indexed":false,"internalType":"uint256","name":"poolId","type":"uint256"},{"indexed":false,"internalType":"uint256","name":"amount","type":"uint256"}],"name":"Staked","type":"event"},{"anonymous":false,"inputs":[{"indexed":true,"internalType":"address","name":"user","type":"address"},{"indexed":false,"internalType":"uint256","name":"fromPoolId","type":"uint256"},{"indexed":false,"internalType":"uint256","name":"toPoolId","type":"uint256"},{"indexed":false,"internalType":"uint256","name":"amount","type":"uint256"}],"name":"Transferred","type":"event"},{"anonymous":false,"inputs":[{"indexed":false,"internalType":"address","name":"account","type":"address"}],"name":"Unpaused","type":"event"},{"anonymous":false,"inputs":[{"indexed":false,"internalType":"uint256","name":"poolId","type":"uint256"},{"indexed":false,"internalType":"address","name":"artist","type":"address"}],"name":"UpdatedArtist","type":"event"},{"anonymous":false,"inputs":[{"indexed":true,"internalType":"address","name":"user","type":"address"},{"indexed":false,"internalType":"uint256","name":"poolId","type":"uint256"},{"indexed":false,"internalType":"uint256","name":"amount","type":"uint256"}],"name":"Withdrawn","type":"event"},{"constant":false,"inputs":[],"name":"BancorFormula","outputs":[],"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":false,"inputs":[{"internalType":"uint256","name":"pool","type":"uint256"},{"internalType":"uint256","name":"id","type":"uint256"},{"internalType":"uint256","name":"points","type":"uint256"},{"internalType":"uint256","name":"mintFee","type":"uint256"},{"internalType":"uint256","name":"releaseTime","type":"uint256"}],"name":"addCard","outputs":[],"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":false,"inputs":[{"internalType":"address","name":"account","type":"address"}],"name":"addPauser","outputs":[],"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":true,"inputs":[{"internalType":"address","name":"account","type":"address"},{"internalType":"uint256","name":"id","type":"uint256"}],"name":"balanceOf","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":true,"inputs":[{"internalType":"uint256","name":"id","type":"uint256"}],"name":"balanceOfPool","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":true,"inputs":[{"internalType":"uint256","name":"pool","type":"uint256"},{"internalType":"uint256","name":"card","type":"uint256"}],"name":"cardMintFee","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":true,"inputs":[{"internalType":"uint256","name":"pool","type":"uint256"},{"internalType":"uint256","name":"card","type":"uint256"}],"name":"cardPoints","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":true,"inputs":[{"internalType":"uint256","name":"pool","type":"uint256"},{"internalType":"uint256","name":"card","type":"uint256"}],"name":"cardReleaseTime","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":true,"inputs":[],"name":"controller","outputs":[{"internalType":"address","name":"","type":"address"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":false,"inputs":[{"internalType":"uint256","name":"pool","type":"uint256"},{"internalType":"uint256","name":"supply","type":"uint256"},{"internalType":"uint256","name":"points","type":"uint256"},{"internalType":"uint256","name":"mintFee","type":"uint256"},{"internalType":"uint256","name":"releaseTime","type":"uint256"}],"name":"createCard","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":false,"inputs":[{"internalType":"uint256","name":"id","type":"uint256"},{"internalType":"uint256","name":"periodStart","type":"uint256"},{"internalType":"uint256","name":"controllerShare","type":"uint256"},{"internalType":"address","name":"artist","type":"address"}],"name":"createPool","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":true,"inputs":[{"internalType":"address","name":"account","type":"address"},{"internalType":"uint256","name":"pool","type":"uint256"}],"name":"earned","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":false,"inputs":[{"internalType":"uint256","name":"pool","type":"uint256"}],"name":"exit","outputs":[],"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":true,"inputs":[],"name":"isOwner","outputs":[{"internalType":"bool","name":"","type":"bool"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":true,"inputs":[{"internalType":"address","name":"account","type":"address"}],"name":"isPauser","outputs":[{"internalType":"bool","name":"","type":"bool"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":true,"inputs":[],"name":"memeLtd","outputs":[{"internalType":"contract IERC1155","name":"","type":"address"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":true,"inputs":[],"name":"owner","outputs":[{"internalType":"address","name":"","type":"address"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":false,"inputs":[],"name":"pause","outputs":[],"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":true,"inputs":[],"name":"paused","outputs":[{"internalType":"bool","name":"","type":"bool"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":true,"inputs":[{"internalType":"address","name":"","type":"address"}],"name":"pendingWithdrawals","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":true,"inputs":[{"internalType":"uint256","name":"","type":"uint256"}],"name":"pools","outputs":[{"internalType":"uint256","name":"periodStart","type":"uint256"},{"internalType":"uint256","name":"feesCollected","type":"uint256"},{"internalType":"uint256","name":"spentPineapples","type":"uint256"},{"internalType":"uint256","name":"controllerShare","type":"uint256"},{"internalType":"address","name":"artist","type":"address"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":true,"inputs":[{"internalType":"uint256","name":"_baseN","type":"uint256"},{"internalType":"uint256","name":"_baseD","type":"uint256"},{"internalType":"uint32","name":"_expN","type":"uint32"},{"internalType":"uint32","name":"_expD","type":"uint32"}],"name":"power","outputs":[{"internalType":"uint256","name":"","type":"uint256"},{"internalType":"uint8","name":"","type":"uint8"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":false,"inputs":[{"internalType":"uint256","name":"pool","type":"uint256"},{"internalType":"uint256","name":"card","type":"uint256"}],"name":"redeem","outputs":[],"payable":true,"stateMutability":"payable","type":"function"},{"constant":false,"inputs":[],"name":"renounceOwnership","outputs":[],"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":false,"inputs":[],"name":"renouncePauser","outputs":[],"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":false,"inputs":[{"internalType":"address","name":"account","type":"address"},{"internalType":"uint256","name":"pool","type":"uint256"}],"name":"rescuePineapples","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":true,"inputs":[],"name":"rescuer","outputs":[{"internalType":"address","name":"","type":"address"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":false,"inputs":[{"internalType":"uint256","name":"pool","type":"uint256"},{"internalType":"address","name":"artist","type":"address"}],"name":"setArtist","outputs":[],"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":false,"inputs":[{"internalType":"address","name":"_controller","type":"address"}],"name":"setController","outputs":[],"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":false,"inputs":[{"internalType":"uint256","name":"pool","type":"uint256"},{"internalType":"uint256","name":"_controllerShare","type":"uint256"}],"name":"setControllerShare","outputs":[],"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":false,"inputs":[{"internalType":"address","name":"_rescuer","type":"address"}],"name":"setRescuer","outputs":[],"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":false,"inputs":[{"internalType":"uint256","name":"pool","type":"uint256"},{"internalType":"uint256","name":"amount","type":"uint256"}],"name":"stake","outputs":[],"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":true,"inputs":[{"internalType":"address","name":"account","type":"address"},{"internalType":"uint256","name":"pool","type":"uint256"}],"name":"timeElapsed","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":true,"inputs":[],"name":"token","outputs":[{"internalType":"contract IERC20","name":"","type":"address"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":true,"inputs":[],"name":"totalSupply","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":false,"inputs":[{"internalType":"uint256","name":"fromPool","type":"uint256"},{"internalType":"uint256","name":"toPool","type":"uint256"},{"internalType":"uint256","name":"amount","type":"uint256"}],"name":"transfer","outputs":[],"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":false,"inputs":[{"internalType":"uint256","name":"fromPool","type":"uint256"},{"internalType":"uint256","name":"toPool","type":"uint256"}],"name":"transferAll","outputs":[],"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":false,"inputs":[{"internalType":"address","name":"newOwner","type":"address"}],"name":"transferOwnership","outputs":[],"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":false,"inputs":[],"name":"unpause","outputs":[],"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":false,"inputs":[{"internalType":"uint256","name":"pool","type":"uint256"},{"internalType":"uint256","name":"amount","type":"uint256"}],"name":"withdraw","outputs":[],"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":false,"inputs":[],"name":"withdrawFee","outputs":[],"payable":false,"stateMutability":"nonpayable","type":"function"}]'
    contract_address = '0x7c444720664c7876004bcdfd786ff8c905add5f1'
    safe_address = Web3.toChecksumAddress(contract_address)
    contract = web3.eth.contract(address=safe_address, abi=abi)
    return contract

def getstuff(contract, addr):
    miner = Web3.toChecksumAddress(addr)
    earned = contract.functions.earned(miner,0).call()
    earned = earned * pow (10,-18)
    bdigg = contract.functions.balanceOf(miner,0).call()
    bdigg = bdigg * pow (10,-18)

    return earned, bdigg

def getminted(contract, addr):
    list = {}
    
    return list

def known_addr():
    knownaddr = []
    try:
        with connect(**config) as connection:
            sql = f'SELECT address FROM nft'
            logging.debug('executing SQL command: ' + sql)
            with connection.cursor() as cursor:
                cursor.execute(sql)
                result = cursor.fetchall()
                for row in result:
                    if row[0] not in knownaddr:
                        knownaddr.append(row[0])
    except Error as e:
        connection.rollback()
        logging.warning('error while polling nft table: ',e)
    connection.close()
    return knownaddr


def main():
    logging.basicConfig(
        level=logging.DEBUG,
        format="%(asctime)s %(relativeCreated)6d %(threadName)s %(levelname)s %(message)s",
        handlers=[
            logging.FileHandler("analyzenft.log"),
            logging.StreamHandler()
        ]
    )

    addresses = known_addr()
    contract = getcontract()

    for address in addresses:
        pineapple,bdigg = getstuff(contract, address)
        pirate = 1.3*pow(bdigg*1000, 0.25)
        time.sleep(0.2)
        insert_sql(address, bdigg, pineapple, pirate)



if __name__ == '__main__':
    main()


