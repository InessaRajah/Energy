import json
import subprocess as subprocess
import time as TIME
from Prosumer import Prosumer
import numpy as np
import pandas as pd
import functions as func 
from web3 import Web3
import pytz
from datetime import datetime
import gurobipy as gb

#This will be the Admin node
print('Test0: Admin')

ganache_url = "http://127.0.0.1:7545"
#ganache_url = "http://127.0.0.1:5354"

web3 =Web3(Web3.HTTPProvider(ganache_url))

#Check if node is connected
print('Admin:', web3.isConnected())

address = web3.toChecksumAddress('0x2F6D8F6cE45f9A74E79bf7AD30aC8D9BdFBdEBF5')

#how to import abi and bytecode using truffle 
PATH_TRUFFLE_WK = 'C:/Users/Inessa/Desktop/4th_Year/FYP/Methodology_Eth/energy'
truffleFile = json.load(open(PATH_TRUFFLE_WK + '/build/contracts/Energy.json'))
abi = truffleFile['abi']
bytecode = truffleFile['bytecode']

#fetch the smart contract
contract = web3.eth.contract(address=address, abi =abi)

#define signing account for transactions- admin for these tests
web3.eth.defaultAccount = web3.eth.accounts[0]

num_agents = 4

#admin to start trading period
cat = pytz.timezone('Africa/Johannesburg')
today = datetime.time(datetime.now(tz = cat))
time = today.hour
today = datetime.date(datetime.now(tz = cat))
date = str(today)
print(date)
print(time)


#Admin needs to add peers before trading period starts
# #add peer 1 
# tx_hash = contract.functions.addPeer('0x9EcFfD05649930d417185E79ad2203F8E8735784', True, 1).transact()
# web3.eth.waitForTransactionReceipt(tx_hash)
# print("Successfully added peer 1")
# print("Take a look!")
# print(contract.functions.peers('0x9EcFfD05649930d417185E79ad2203F8E8735784').call())
# #add peer 2
# tx_hash = contract.functions.addPeer('0x60f798cd72C31df6f47fB9F00C0491e702fB3851', True, 1).transact()
# web3.eth.waitForTransactionReceipt(tx_hash)
# print("Successfully added peer 2")
# print("Take a look!")
# print(contract.functions.peers('0x60f798cd72C31df6f47fB9F00C0491e702fB3851').call())

# # if you try to re-add a peer that already is part of the network- you'll get errors

# #add an additional two peers- makes four peers in total
# tx_hash = contract.functions.addPeer('0xf670B43Fb72b16cD834D43A6BF0f429163B383F2', True, 1).transact()
# web3.eth.waitForTransactionReceipt(tx_hash)
# print("Successfully added peer 3")
# print("Take a look!")
# print(contract.functions.peers('0xf670B43Fb72b16cD834D43A6BF0f429163B383F2').call())
# #add peer 4
# tx_hash = contract.functions.addPeer('0x93EC6Ea2d6399E6801D294cb562102C4c03A30A8', True, 1).transact()
# web3.eth.waitForTransactionReceipt(tx_hash)
# print("Successfully added peer 4")
# print("Take a look!")
# print(contract.functions.peers('0x93EC6Ea2d6399E6801D294cb562102C4c03A30A8').call())



for i in range(num_agents):
   web3.eth.defaultAccount = web3.eth.accounts[i+1]
   tx_hash = contract.functions.deregisterPeer().transact()
   web3.eth.waitForTransactionReceipt(tx_hash)
print('Peers deregistered')

web3.eth.defaultAccount = web3.eth.accounts[0]
tx_hash = contract.functions.startTradingPer(date, time).transact()
web3.eth.waitForTransactionReceipt(tx_hash)
#if ((contract.functions.init().call()) and (contract.functions.iteration_complete().call()==contract.functions.is_optimal().call()==0) and (contract.functions.iteration().call()==contract.functions.localresCounter().call()==0) and (contract.functions.tradeCountIter().call() == contract.functions.trade_penCount().call()== contract.functions.numApprovedTrades().call()==0)):
print("Trading period started")

