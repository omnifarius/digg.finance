import mysql.connector
from mysql.connector import errorcode
import datetime
from web3 import Web3

endpoint = 'https://mainnet.infura.io/v3/foo'

btcusd = '0xF4030086522a5bEEa4988F8cA5B36dbC97BeE88c'
diggbtc = '0x418a6C98CD5B8275955f08F0b8C1c6838c8b1685'

web3 = Web3(Web3.HTTPProvider(endpoint))
abi = '[{"inputs":[],"name":"decimals","outputs":[{"internalType":"uint8","name":"","type":"uint8"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"description","outputs":[{"internalType":"string","name":"","type":"string"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"uint80","name":"_roundId","type":"uint80"}],"name":"getRoundData","outputs":[{"internalType":"uint80","name":"roundId","type":"uint80"},{"internalType":"int256","name":"answer","type":"int256"},{"internalType":"uint256","name":"startedAt","type":"uint256"},{"internalType":"uint256","name":"updatedAt","type":"uint256"},{"internalType":"uint80","name":"answeredInRound","type":"uint80"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"latestRoundData","outputs":[{"internalType":"uint80","name":"roundId","type":"uint80"},{"internalType":"int256","name":"answer","type":"int256"},{"internalType":"uint256","name":"startedAt","type":"uint256"},{"internalType":"uint256","name":"updatedAt","type":"uint256"},{"internalType":"uint80","name":"answeredInRound","type":"uint80"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"version","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"}]'
#first pass for digg price
contract = web3.eth.contract(address=diggbtc, abi=abi)
decimals = contract.functions.decimals().call()
latestData = contract.functions.latestRoundData().call()
#print(latestData)
results = {}
if len(latestData) == 5:
    results = {'roundID':latestData[0], 'answer':latestData[1], 'startedAt':latestData[2], 'updatedAt':latestData[3], 'answeredInRound':latestData[4]}
else:
    print('latest data not 5 distinct results')
diggprice = results['answer'] * pow(10, -1 * decimals)
#second pass for btc price
contract = web3.eth.contract(address=btcusd, abi=abi)
decimals = contract.functions.decimals().call()
latestData = contract.functions.latestRoundData().call()
#print(latestData)
results = {}
if len(latestData) == 5:
    results = {'roundID':latestData[0], 'answer':latestData[1], 'startedAt':latestData[2], 'updatedAt':latestData[3], 'answeredInRound':latestData[4]}
else:
    print('latest data not 5 distinct results')
btcprice = results['answer'] * pow(10, -1 * decimals)
#ok, now i have both, time to push into TWAP table

timenow = datetime.datetime.now()

config = {
    'user': 'diggsqluser',
    'password': 'foo',
    'host': 'localhost',
    'database': 'digg',
    'auth_plugin': 'mysql_native_password',
    'raise_on_warnings': True
}

cnx = mysql.connector.connect(**config)
cursor = cnx.cursor()

sql = (
    "INSERT INTO running_prices (timestamp, BTCUSDprice, DIGGBTCprice, DIGGUSDprice)"
    "VALUES (%s, %s, %s, %s)" )
data = (timenow, btcprice, diggprice, diggprice * btcprice)

try:
   # Executing the SQL command
   cursor.execute(sql, data)
   print(f'Data inserted: {data}')
   # Commit your changes in the database
   cnx.commit()

except:
   # Rolling back in case of error
   cnx.rollback()
   print("Rolling Back due to Error")

# Closing the connection
cnx.close()

