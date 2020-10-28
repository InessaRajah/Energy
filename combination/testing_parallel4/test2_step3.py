import json
import time as TIME
from Prosumer import Prosumer
import numpy as np
import pandas as pd
import functions as func
import subprocess as subprocess
from web3 import Web3
import pytz
from datetime import datetime
import gurobipy as gb
from pathlib import Path


#this will be agent1
print('Test3: Peer2')

ganache_url = "http://127.0.0.1:8545"

web3 =Web3(Web3.HTTPProvider(ganache_url))

#Check if node is connected
print('Peer2:', web3.isConnected())

num_agent = 2

#set node as signing agent
web3.eth.defaultAccount = web3.eth.accounts[num_agent]

#perform steps to access the smart contract
address = web3.toChecksumAddress('0xa0Dc61164631b017a1Ed74e41e34A624B554A3c7')

#how to import abi and bytecode using truffle 
PATH_TRUFFLE_WK = 'C:/Users/Inessa/Desktop/4th_Year/FYP/Methodology_Eth/energy'
truffleFile = json.load(open(PATH_TRUFFLE_WK + '/build/contracts/Energy.json'))
abi = truffleFile['abi']
bytecode = truffleFile['bytecode']

#fetch the smart contract
contract = web3.eth.contract(address=address, abi =abi)

#list of each agents solar panel number
#solar_panels = [7, 7, 5, 1]
solar_panels = [7, 7, 5, 1, 4]

#list containing list of solar radiation (W/m^2) per time period 
#solar = [733.18, 438.14]

num_agents = len(solar_panels)

#create dataframes to store info you'd like to save to .csv files
Metrics_DF = pd.DataFrame(columns = ['Time Period', 'Num Iterations', 'Time (s)'])

#admin to start trading period
cat = pytz.timezone('Africa/Johannesburg')
today = datetime.time(datetime.now(tz = cat))
time = today.hour
today = datetime.date(datetime.now(tz = cat))
date = str(today)

#for testing purposes
time_period = 1

part = np.ones([num_agents, num_agents])
for i in range(num_agents):
    for j in range(num_agents):
        if (i == j):
            part[i][j] = 0

p = part[num_agent-1].nonzero()[0]
print(p)
data_path = Path(r'Results\Trades2.csv')
data_file = pd.read_csv(data_path)
data_file = pd.DataFrame(data_file)
tradeIDs = data_file['TradeID']
amounts = data_file['Quantity (kWh)']
prices = data_file['Price (c/kWh)']

for j in range(len(amounts)):
     sender = str(web3.eth.accounts[num_agent])
     buyer = p[j].tolist()
     amount = amounts[j] * 10000
     amount = round(amount)
     buyer = str(web3.eth.accounts[buyer+1])
     price_c = prices[j] * 10000
     price_c = round(price_c)
     tx_hash = contract.functions.addTradeBid(sender, buyer, amount, price_c).transact()
     web3.eth.waitForTransactionReceipt(tx_hash)
     tradeID = tradeIDs[j].tolist()
     trade_bids = contract.functions.trade_bids_mapping(tradeID).call()
     print("Trade bid", num_agent, "to", p[j]+1 ,"submitted.  Take a look!")
     print(trade_bids)
     print("Total number of trade bids:")
     print(contract.functions.tradeCountIter().call())
print("All trade bids from peer", num_agent, "submitted")
