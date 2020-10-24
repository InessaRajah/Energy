import json
from web3 import Web3
import pytz
from datetime import datetime
import gurobipy as gb
import time as TIME
from Prosumer import Prosumer
import numpy as np
import pandas as pd
import functions as func

#need to change primal and dual residual and then redeploy contract
#note that in smart contract and saved files= agents are saved starting from 1 but because of indexing in python, agent numbers start at 0
#connect to blockchain network
ganache_url = "http://127.0.0.1:7545"
#ganache_url = "http://127.0.0.1:5354"

web3 =Web3(Web3.HTTPProvider(ganache_url))

#Check if node is connected
print(web3.isConnected())

address = web3.toChecksumAddress('0xFCb00692FAA29a7877CACf928A05C08c9b44Da35')

#how to import abi and bytecode using truffle 
PATH_TRUFFLE_WK = 'C:/Users/Inessa/Desktop/4th_Year/FYP/Methodology_Eth/energy'
truffleFile = json.load(open(PATH_TRUFFLE_WK + '/build/contracts/Energy.json'))
abi = truffleFile['abi']
bytecode = truffleFile['bytecode']

#fetch the smart contract
contract = web3.eth.contract(address=address, abi =abi)

#define signing account for transactions- admin for these tests
web3.eth.defaultAccount = web3.eth.accounts[0]

#add peer 1 
#tx_hash = contract.functions.addPeer('0x9EcFfD05649930d417185E79ad2203F8E8735784', True, 1).transact()
#web3.eth.waitForTransactionReceipt(tx_hash)
#print("Successfully added peer 1")
#print("Take a look!")
#print(contract.functions.peers('0x9EcFfD05649930d417185E79ad2203F8E8735784').call())
#add peer 2
#tx_hash = contract.functions.addPeer('0x60f798cd72C31df6f47fB9F00C0491e702fB3851', True, 1).transact()
#web3.eth.waitForTransactionReceipt(tx_hash)
#print("Successfully added peer 2")
#print("Take a look!")
#print(contract.functions.peers('0x60f798cd72C31df6f47fB9F00C0491e702fB3851').call())

# if you try to re-add a peer that already is part of the network- you'll get errors

#add an additional two peers- makes four peers in total
#tx_hash = contract.functions.addPeer('0xf670B43Fb72b16cD834D43A6BF0f429163B383F2', True, 1).transact()
#web3.eth.waitForTransactionReceipt(tx_hash)
#print("Successfully added peer 3")
#print("Take a look!")
#print(contract.functions.peers('0xf670B43Fb72b16cD834D43A6BF0f429163B383F2').call())
#add peer 4
#tx_hash = contract.functions.addPeer('0x93EC6Ea2d6399E6801D294cb562102C4c03A30A8', True, 1).transact()
#web3.eth.waitForTransactionReceipt(tx_hash)
#print("Successfully added peer 4")
#print("Take a look!")
#print(contract.functions.peers('0x93EC6Ea2d6399E6801D294cb562102C4c03A30A8').call())

#list description of all agents
agents = []

#keep track of how many runs of the optimisation code result in suboptimal results
suboptimal = 0

#set the season being considered
season = 'Summer'

#list of loads[i][j] where i = agent number and j = time_period
#loads = [[0.100335206], [0.289092163], [0.074726916], [0.088529768]]
loads = [[0.100335206, 0.145744248] , [0.289092163, 0.232237399], [0.074726916, 0.006], [0.088529768,  0.048454915]]

#list of each agents solar panel number
solar_panels = [7, 7, 5, 1]

# grid tariff structure
grid_price = {'Summer': {'Peak': 172.68, 'Standard': 136.60, 'Off-peak': 107.46}, 'Winter': {'Peak': 397.27, 'Standard': 162.74, 'Off-peak': 114.83}}
time_classification = {0: 'Off-peak', 1: 'Off-peak', 2: 'Off-peak', 3: 'Off-peak', 4: 'Off-peak', 5: 'Off-peak', 6: 'Off-peak', 7: 'Peak', 8: 'Peak', 9: 'Peak', 10: 'Peak', 
                    11: 'Standard', 12: 'Standard', 13: 'Standard', 14: 'Standard', 15: 'Standard', 16: 'Standard', 17: 'Standard', 18: 'Peak', 19: 'Peak', 20: 'Peak', 21:'Standard', 22:'Standard'
                    , 23:'Standard'}

#list containing list of solar radiation (W/m^2) per time period 
solar = [733.18, 438.14]
#k_tim is the grid c/kwh price for a time period- looking at Standard time period in Summer here.  This is updated in the for loop
k_tim = 136.60
#area of one of the seven solar panels being used in m^2
A = 2*0.994
#one module is 17.64% efficient
n_pv = 0.1764
#efficiency loss parameter. According to [49] eff = 0.08 (inverter losses) + 0.02 (some modules not behaving as well as others) + 0.002 (resistive loss) + assume no temp and suntracking losses + 0.05 (damage + soiling losses )
eff = 0.152
#setting this for testing purposes
hours = [0, 1]

#universal battery paramaters
SOC_max = 0.85*3.7
SOC_min = 0.25*3.7

num_agents = len(solar_panels)

#starting SOC_bat for all agents
SOC_bat = 0.7*3.7*np.ones([num_agents, 1])

#create dataframes to store info you'd like to save to .csv files
TradesDF = pd.DataFrame(columns=['Agent#','Time Period', 'TradeID', 'Quantity (kWh)', 'Price (c/kWh)', 'Avg. Price for Time Period (c/kwh)', 'Amount paid/received for Trade Transaction (c)'])
SolarDF = pd.DataFrame(columns=['Agent#','Time Period', 'Solar Irradiation (W/m^2)', 'Num_solar panels', 'Solar Output energy (kWh)'])
SOC_DF = pd.DataFrame(columns=['Agent#', 'Time Period', 'SOC (%)'])
Metrics_DF = pd.DataFrame(columns = ['Time Period', 'Num Iterations', 'Time (s)'])

#admin to start trading period
cat = pytz.timezone('Africa/Johannesburg')
today = datetime.time(datetime.now(tz = cat))
time = today.hour
today = datetime.date(datetime.now(tz = cat))
date = str(today)

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

#register peers to be involved in blockchain trading
#set signing peer to be peer 1 who has been added to network by admin
# if you try to register peer twice - will get an error
for i in range(1, num_agents+1):
    web3.eth.defaultAccount = web3.eth.accounts[i]
    print(web3.eth.defaultAccount)
    tx_hash = contract.functions.registerPeer().transact()
    print("Registering peer", i, "to trade in time period")
    web3.eth.waitForTransactionReceipt(tx_hash)
    print("Peer", i, "successfully registered.  Take a look!")
    #address = str(web3.eth.accounts[i])
    #peer1 = contract.functions.peers(address).call()
    #print(peer1)

#look at one time period for this test:
time_period = 0
#first create all agents

for i in range(num_agents):
        agent, agents = func.createAgent(loads[i][time_period], SOC_bat[i][0], solar_panels[i], agents, solar, time_period, k_tim)
        SolarDF = func.createSolarFile(agent, time_period, solar, SOC_bat[i][0], solar_panels[i], SolarDF)
print('Making agents complete')

print("TIME PERIOD:", 0)
max_Iter = 1500
    #the higher the commission fees- the less the trading quantities that occur (makes sense if you think of cost function).  
    #the higher the trade commission fees- the lower the trading price, but because of lower trade quantities (zero if possible) - less economic benefit for prosumers
Commission_Fees = 0 #- for decentralized models (for economic comparison)
    #Commission_Fees = 0.5 #- for centralized models 50c/kwh or might use 1c/kwh as done in [12] - using 1c/kwh gets almost the same price as having 0 commission fees and trades are at a slightly lower quantity
    #using 50c/kwh commission fee results in vastly lower prices but basically 0 traded quantities
penalty_factor = 0.01
residual_primal = 1e-4 
resiudal_dual = 1e-4

num_agents = len(agents)
preferences = Commission_Fees* np.ones(len(agents)-1)

Trades = np.zeros([num_agents, num_agents])
Prices = np.zeros([num_agents, num_agents])

    #array of trade partners- set index to 1 if trade is happening e.g. part[0][1] = 1 if customer 0 is trading with customer 1
part = np.ones([num_agents, num_agents])
for i in range(num_agents):
    for j in range(num_agents):
        if (i == j):
            part[i][j] = 0

    #create players for this optimisation run
players = func.createPlayers(agents, part, preferences, penalty_factor)
prim = float('inf')
dual = float('inf')
iteration = 0
SW = 0
simulation_time = 0

lapsed = 0
start_time = TIME.time()

#get primal and dual tolerances
pri_tol = contract.functions.pri_tol().call()
dual_tol = contract.functions.dual_tol().call()

temp = np.copy(Trades)

#this returns [1,2,3] i.e the indices of trading partners
p = part[0].nonzero()[0]
countTrades = 0
#do the following for each iteration
optimal = False
#while(optimal == 0):
for t in range(0,2):
    if (t==1):
        optimal = True
    print('t', t)
    #each agent performs local optimisation
    if (optimal == 0):
        for i in range(num_agents):
                temp[:,i] = players[i].optimize(Trades[i,:])
                Prices[:,i][part[i,:].nonzero()] = players[i].y
                web3.eth.defaultAccount = web3.eth.accounts[i+1]
                #each agent needs to add local residual based on the previous trades  
                primal_res = players[i].Res_primal * 10000
                primal_res = round(primal_res)
                dual_res = players[i].Res_dual * 10000
                dual_res = round(dual_res)
                if (t==1):
                    print(primal_res)
                    print(dual_res)
                    sender = str(web3.eth.accounts[i+1])
                    print(web3.eth.defaultAccount)
                    print('init', contract.functions.init().call())
                    print('iteration complete?', contract.functions.iteration_complete().call())
                    print('num_trade bids:', contract.functions.tradeCountIter().call())
                    tx_hash = contract.functions.addLocalRes(primal_res, dual_res).transact()
                    web3.eth.waitForTransactionReceipt(tx_hash)
                    print("Added a local residual.  Take a look!")
                    print(contract.functions.localres(sender).call())
                    print('Here is the state of the global pres:', contract.functions.global_pres().call())
                    print('Here is the state of the global dres:', contract.functions.global_dres().call())

    #if trades are not optimal- submit trade bids so that each agent can perform local optimisation again
    if (optimal==0):
        #each agent needs to submit trade bids
        for i in range(num_agents):
            p = part[i].nonzero()[0]
            for j in range(len(p)):
                sender = str(web3.eth.accounts[i+1])
                web3.eth.defaultAccount = web3.eth.accounts[i+1]
                print(sender)
                buyer = p[j] +1
                buyer = str(web3.eth.accounts[buyer])
                print(buyer)
                amount = temp[j, i] * 10000
                amount = amount.tolist()
                amount = round(amount)
                print(type(amount))
                price_c = Prices[:,i][p[j]] * 10000
                price_c = price_c.tolist()
                price_c = round(price_c)
                print(price_c)
                tx_hash = contract.functions.addTradeBid(date, time, sender, buyer, amount, price_c).transact()
                web3.eth.waitForTransactionReceipt(tx_hash)
                tradeID = (i+1)*10 + p[j].tolist() + 1
                trade_bids = contract.functions.trade_bids_mapping(tradeID).call()
                countTrades = countTrades + 1
                print("Trade bid", i+1, "to", p[j]+1 ,"submitted.  Take a look!")
                print(trade_bids)
                print("Total number of trade bids:")
                print(contract.functions.tradeCountIter().call())
        print("All trade bids submitted")
        #now, each agent needs to collect all trade bids and repeat the process
        #Trades = np.zeros([num_agents, num_agents])
        #temp = np.zeros([num_agents, num_agents])
        num_tradebids = contract.functions.tradeCountIter().call()
        for i in range(num_agents):
            address = str(web3.eth.accounts[i+1])
            peer = contract.functions.peers(address).call()
            peer_id = peer[0]
            p = part[i].nonzero()[0]
            for j in range(len(p)):
                peer_from = p[j] + 1
                peer_from = peer_from.tolist()
                trade_id = peer_from*10 + peer_id
                trade_temp = contract.functions.trade_bids_mapping(trade_id).call()
                pos = p[j]
                pos = pos.tolist()
                Trades[i, pos] = trade_temp[4]/10000
        temp = Trades


    #if trades are optimal - create trades for approval          
    else:
        tradeCount = 0
        print(temp)
        #each agent submits optimal trades for approval
        for i in range(num_agents):
            p = part[i].nonzero()[0]
            for j in range(len(p)):
                sender = str(web3.eth.accounts[i+1])
                web3.eth.defaultAccount = web3.eth.accounts[i+1]
                print('Sender', sender)
                to = p[j] +1
                to = str(web3.eth.accounts[to])
                print("To", to)
                amount = temp[p[j], i] * 10000
                amount = amount.tolist()
                amount = round(amount)
                #if you are the one paying to consume power- create the trade
                if (amount<0):
                    price_c = Prices[:,i][p[j]] * 10000
                    price_c = price_c.tolist()
                    price_c = round(price_c)
                    print('price:', price_c)
                    print('amount:', amount)
                    cat = pytz.timezone('Africa/Johannesburg')
                    today = datetime.time(datetime.now(tz = cat))
                    time = today.hour
                    today = datetime.date(datetime.now(tz = cat))
                    date = str(today)
                    s = contract.functions.peers(sender).call()
                    b = contract.functions.peers(to).call()
                    id_set = (s[0] * 10)+ (b[0])
                    bid = contract.functions.trade_bids_mapping(id_set).call()
                    print('Trade bid used to create trade:', bid)
                    tx_hash = contract.functions.createTrade(date, time, sender, to, amount, price_c).transact()
                    web3.eth.waitForTransactionReceipt(tx_hash)
                    trade = contract.functions.trades_pending_mapping(id_set).call()
                    print('Trade created from', s[0], 'to', b[0], 'Here it is:')
                    print(trade)
        print("All trades created")
        #now need to approve trades 
        for i in range(num_agents):
            web3.eth.defaultAccount = web3.eth.accounts[i+1]
            msg_sender = str(web3.eth.accounts[i+1])
            cat = pytz.timezone('Africa/Johannesburg')  
            today = datetime.time(datetime.now(tz = cat))
            time = today.hour
            today = datetime.date(datetime.now(tz = cat))
            date = str(today)
            trades_pen = contract.functions.trade_penCount().call()
            for k in range (0, trades_pen):
                trade = contract.functions.trades_pending(k).call()
                if (trade[3] == msg_sender):
                    print('Approving a trade')
                    #if (trade[9]):
                    approver = contract.functions.peers(trade[3]).call()
                    approvee = contract.functions.peers(trade[2]).call()
                    id_set = approvee[0]*10 + approver[0]
                    tx_hash1 = contract.functions.approveTrade(trade[0], trade[1], trade[2], trade[3], trade[4], trade[5], trade[6], trade[7], trade[8], trade[9], date, time, id_set).transact()
                    web3.eth.waitForTransactionReceipt(tx_hash1)
                    print("Peer", i+1, "approved optimal trade")
                    print("Here is the stored approved, optimal trade:")
                    num_approved = contract.functions.numApprovedTrades().call()
                    approved = contract.functions.approved(num_approved-1).call()
                    print(approved)
        print("Optimal Trades approved")
        print("Iterations:", contract.functions.iteration().call())
        print("Time period", time_period, "is now over")



#update Trades if trade bids are submitted- then do optimisation again