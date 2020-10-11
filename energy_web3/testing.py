import json
from web3 import Web3
import pytz
from datetime import datetime


#setup 
ganache_url = "http://127.0.0.1:7545"

web3 =Web3(Web3.HTTPProvider(ganache_url))

#Check if node is connected
print(web3.isConnected())

#define signing account for transactions
web3.eth.defaultAccount = web3.eth.accounts[0]
print(web3.eth.accounts[0])
print(web3.eth.accounts[1])

#define smart contract account - different address for each deployment
address = web3.toChecksumAddress('0x3B79cab73D2d22EB642c32c06a10FF8f4A4e09Ef')

#how to import abi and bytecode using truffle 
PATH_TRUFFLE_WK = 'C:/Users/Inessa/Desktop/4th_Year/FYP/Methodology_Eth/energy'
truffleFile = json.load(open(PATH_TRUFFLE_WK + '/build/contracts/Energy.json'))
abi = truffleFile['abi']
bytecode = truffleFile['bytecode']

#fetch the smart contract
contract = web3.eth.contract(address=address, abi =abi)

## Test 1: reading data from smart contract, simple Peer contract

#call() function - read data
#returns struct as a list
peer = contract.functions.peersCount().call()
#print(peer)
print("Test1 Complete")

#Test 2: writing transactions using smart contract, simple Peer contract
#writing to blockchain using smart contract
#need to pass address arguments as strings when calling functions from web3.py

tx_hash = contract.functions.addPeer('0x6C6f8c9b409480EFFA632284b5058ebAd48F1fcc', True, 1, True).transact()

#want to get transaction receipt back to indicate that mining was successful and transaction has been logged on the blockchain
#this next line means wait until transaction receipt is received before continuing with code execution
web3.eth.waitForTransactionReceipt(tx_hash)

print("Test2 Complete")

#print('Added a peer: {}'.format(
#   contract.functions.peersCount().call()
#))

#print('New peer: {}'.format(
#   contract.functions.peers(6).call()
#))

##Test 3: reading data and writing transactions using smart contract, simple Peer + Trade contract
#address s, address b, uint amount, uint price_c
sender = str(web3.eth.accounts[0])
buyer = str(web3.eth.accounts[1])
cat = pytz.timezone('Africa/Johannesburg')
today = datetime.now(tz = cat)
time_per = today.hour
date = datetime.date(datetime.now(tz = cat))
date = str(date)

tx_hash = contract.functions.addTradeBid(date, time_per, sender, buyer, 9, 80).transact()
web3.eth.waitForTransactionReceipt(tx_hash)

#print('Added a trade bid...: {}'.format(
#   contract.functions.tradeCountIter().call()
#))

#print('...for this iteration: {}'.format(
#  contract.functions.iteration().call()
#))

##calling the first trade bid stored in trades array
print("Test3 complete")
print('Added a trade bid. Take a look!: {}'.format(
   contract.functions.trade_bids(0).call()
))

##print the latest block
#latest = web3.eth.getBlock('latest')
#print(latest)

##Test 4: testing reading data and writing transactions, peer+trade+local residuals
#sender = str(web3.eth.accounts[1])
sender = '0x6C6f8c9b409480EFFA632284b5058ebAd48F1fcc'
tx_hash1 = contract.functions.addLocalRes(sender, 1234).transact()
web3.eth.waitForTransactionReceipt(tx_hash1)

print('Added a local residual.  Take a look!: {}'.format(
   contract.functions.localres(sender).call()
))


print("Test4 complete")

##Test 5: testing writing to approved Trades to the smart contract, createTrade
sender = web3.eth.accounts[0]
buyer = web3.eth.accounts[1]
temp = "2020_10_11_0_2_1"

tx_hash2 = contract.functions.createTrade(sender, buyer, 10, 87, temp).transact()

web3.eth.waitForTransactionReceipt(tx_hash2)

print('Added a trade.  Take a look!: {}'.format(
   contract.functions.approved_trades(temp).call()
))

print("Test 5 complete")


