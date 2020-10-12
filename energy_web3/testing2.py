import json
from web3 import Web3
import pytz
from datetime import datetime


#Testing advanced contract

#setup 
ganache_url = "http://127.0.0.1:7545"

web3 =Web3(Web3.HTTPProvider(ganache_url))

#Check if node is connected
print(web3.isConnected())

address = web3.toChecksumAddress('0x4e7Bd3292F1eA03E7b290b6Aba16eD31231917F9')

#how to import abi and bytecode using truffle 
PATH_TRUFFLE_WK = 'C:/Users/Inessa/Desktop/4th_Year/FYP/Methodology_Eth/energy'
truffleFile = json.load(open(PATH_TRUFFLE_WK + '/build/contracts/Energy.json'))
abi = truffleFile['abi']
bytecode = truffleFile['bytecode']

#fetch the smart contract
contract = web3.eth.contract(address=address, abi =abi)

#Test 1: Testing addPeer function (writing) and peers[acc] (reading)

#define signing account for transactions- admin for these tests
web3.eth.defaultAccount = web3.eth.accounts[0]

#add peer 1 
tx_hash = contract.functions.addPeer('0xAedA4d57bf6be1e2d68D08f0E6D471E0fB27f4A7', True, 1).transact()
web3.eth.waitForTransactionReceipt(tx_hash)
print("Successfully added peer 1")
print("Take a look!")
print(contract.functions.peers('0xAedA4d57bf6be1e2d68D08f0E6D471E0fB27f4A7').call())
# add peer 2
tx_hash = contract.functions.addPeer('0xd69eDf8528349C92B4Ec767402A66190Db49f937', True, 1).transact()
web3.eth.waitForTransactionReceipt(tx_hash)
print("Successfully added peer 2")
print("Take a look!")
print(contract.functions.peers('0xd69eDf8528349C92B4Ec767402A66190Db49f937').call())
print("Test1 passed")
# if you try to re-add a peer that already is part of the network- you'll get errors

##Test 2: Testing startTradingPer() - done by admin
cat = pytz.timezone('Africa/Johannesburg')
today = datetime.time(datetime.now(tz = cat))
time = today.hour
today = datetime.date(datetime.now(tz = cat))
date = str(today)

tx_hash = contract.functions.startTradingPer(date, time).transact()
web3.eth.waitForTransactionReceipt(tx_hash)
if ((contract.functions.init().call()) and (contract.functions.iteration_complete().call()==contract.functions.is_optimal().call()==0) and (contract.functions.iteration().call()==contract.functions.localresCounter().call()==0) and (contract.functions.tradeCountIter().call() == 0)):
    print("Trading period started")
    print("Test2 passed")
else:
    ("Test2 failed")


##Test 3: peers that want to be involved in this time period register (writing)
#set signing peer to be peer 1 who has been added to network by admin
# if you try to register peer twice - will get an error
#testing registerPeer()
web3.eth.defaultAccount = web3.eth.accounts[1]
tx_hash = contract.functions.registerPeer().transact()
print("Registering peer 1 to trade in time period")
web3.eth.waitForTransactionReceipt(tx_hash)
peer1 = contract.functions.peers('0xAedA4d57bf6be1e2d68D08f0E6D471E0fB27f4A7').call()

web3.eth.defaultAccount = web3.eth.accounts[2]
tx_hash = contract.functions.registerPeer().transact()
print("Registering peer 2 to trade in time period")
web3.eth.waitForTransactionReceipt(tx_hash)
peer2 = contract.functions.peers('0xd69eDf8528349C92B4Ec767402A66190Db49f937').call()


if ((contract.functions.peersTrading().call()==2) and (peer1[4]==1) and (peer2[4] ==1)):
    print("Test3 passed")
else:
    print("Test3 failed")


#Test 4: Testing addTradeBid()
#peer 1 will submit trade to peer 2
web3.eth.defaultAccount = web3.eth.accounts[1]
sender = str(web3.eth.accounts[1])
buyer = str(web3.eth.accounts[2])
tx_hash = contract.functions.addTradeBid(date, time, sender, buyer, 50, 87).transact()
web3.eth.waitForTransactionReceipt(tx_hash)

trade_bids = contract.functions.trade_bids(0).call()
if ((contract.functions.iteration().call()==1) and (contract.functions.tradeCountIter().call()==1)):
    print("Trade bid 12 submitted.  Take a look!")
    print(trade_bids)
    print("Total number of trade bids:")
    print(contract.functions.tradeCountIter().call())
    print("Test 4 passed")
else:
    print("Test 4 failed")


#Test 5: Testing addTradeBid() again
# peer 2 submits trade to peer 1
web3.eth.defaultAccount = web3.eth.accounts[2]
sender = str(web3.eth.accounts[2])
buyer = str(web3.eth.accounts[1])
tx_hash = contract.functions.addTradeBid(date, time, sender, buyer, 50, 87).transact()
web3.eth.waitForTransactionReceipt(tx_hash)
trade_bids = contract.functions.trade_bids(1).call()
if ((contract.functions.iteration().call()==1) and (contract.functions.tradeCountIter().call()==2)):
    print("Trade bid 21 submitted. Take a look!")
    print(trade_bids)
    print("Total number of trade bids:")
    print(contract.functions.tradeCountIter().call())
    print("Test 5 passed")
else:
    print("Test 5 failed")

#Test 6: Testing addLocalRes() (writing)
web3.eth.defaultAccount = web3.eth.accounts[1]
sender = str(web3.eth.accounts[1])
#tx_hash = contract.functions.addLocalRes(1, 2).transact()
#web3.eth.waitForTransactionReceipt(tx_hash)
if ((contract.functions.localresCounter().call()==1) and (contract.functions.global_pres().call() == 1) and (contract.functions.global_dres().call()==2)): 
    print("Added a local residual.  Take a look!")
    print(contract.functions.localres(sender).call())
    print("Test 6 passed")
else:
    print("Test 6 failed")

#PICK UP TESTING FROM HERE
#Test 7: Testing addLocalRes() again (writing)
#test if checkOptimal is called and is_optimal is set to false
## change values of global_pres, global_dres, pri_tol and dual_tol appropriately for this test
web3.eth.defaultAccount = web3.eth.accounts[2]
sender = str(web3.eth.accounts[2])
tx_hash = contract.functions.addLocalRes(1, 2).transact()
web3.eth.waitForTransactionReceipt(tx_hash)
if ((contract.functions.localresCounter().call()==2) and (contract.functions.global_pres().call() == 2) and (contract.functions.global_dres().call()==4)): 
    print("Added a local residual.  Take a look!")
    print(contract.functions.localres(sender).call())
    print("Test 6 passed")
else:
    print("Test 6 failed")

# in the following tests will start a new trading iteration where trade bids and local residuals are re-submitted

#Test 8.1: Testing if calling addTradeBid() now executes newIteration()

#Test 8.2: Testing if calling addTradeBid() now behaves as expected i.e. normally and does not execute newIteration()

#Test 8.3: Add two new local residuals

#Test 9: Testing if checkOptimal is called and is_optimal is set to true
## change values of global_pres, global_dres, pri_tol and dual_tol for this test

#Test 10: testing createTrade() function
#create trade from peer 1 to peer 2

#Test 11: testing approveTrade() function
#have peer 2 approve trade created by trade 1

#Test 12: testing createTrade() function
#create trade from peer 2 to peer 1

#Test 13: testing approveTrade() function
#have peer 1 approve trade created by trade 2
#print out approved trades




