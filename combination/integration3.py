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
from pathlib import Path

##THIS SCRIPT AIMS TO INTEGRATE OPTIMISATION CODE WITH SMART CONTRACT

#list description of all agents
agents = []

#keep track of how many runs of the optimisation code result in suboptimal results
suboptimal = 0

#set the season being considered
season = 'Summer'

#list of loads[i][j] where i = agent number and j = time_period
#loads = [[0.100335206], [0.289092163], [0.074726916], [0.088529768]]
#loads = [[3.46, 0.83] , [0.289092163, 0.232237399], [0.074726916, 0.006], [0.088529768,  0.048454915]]
loads = []
data_path = Path('JulyProfiles1.csv')
data_file = pd.read_csv(data_path)
data_file = pd.DataFrame(data_file)
data_file = data_file.drop(columns = ['Electricity.Timestep', 'Sum', '[kWh]'])
row1 = data_file[data_file.Time == '2016/07/02']
load1 = row1['Proper kWh'].to_list()
loads.append(load1)

data_path = Path('JulyProfiles2.csv')
data_file = pd.read_csv(data_path)
data_file = pd.DataFrame(data_file)
data_file = data_file.drop(columns = ['Electricity.Timestep', 'Sum', '[kWh]'])
row2 = data_file[data_file.Time == '2016/07/02']
load2 = row2['Proper kWh'].to_list()
loads.append(load2)

data_path = Path('JulyProfiles3.csv')
data_file = pd.read_csv(data_path)
data_file = pd.DataFrame(data_file)
data_file = data_file.drop(columns = ['Electricity.Timestep', 'Sum', '[kWh]'])
row3 = data_file[data_file.Time == '2016/07/02']
load3 = row3['Proper kWh'].to_list()
loads.append(load3)

data_path = Path('JulyProfiles4.csv')
data_file = pd.read_csv(data_path)
data_file = pd.DataFrame(data_file)
data_file = data_file.drop(columns = ['Electricity.Timestep', 'Sum', '[kWh]'])
row4 = data_file[data_file.Time == '2016/07/02']
load4 = row4['Proper kWh'].to_list()
loads.append(load4)

data_path = Path('JulyProfiles5.csv')
data_file = pd.read_csv(data_path)
data_file = pd.DataFrame(data_file)
data_file = data_file.drop(columns = ['Electricity.Timestep', 'Sum', '[kWh]'])
row5 = data_file[data_file.Time == '2016/07/02']
load5 = row5['Proper kWh'].to_list()
loads.append(load5)


#list of each agents solar panel number
#solar_panels = [7, 7, 5, 1, 4]
solar_panels = [7, 7, 1, 5, 4]


# grid tariff structure
grid_price = {'Summer': {'Peak': 172.68, 'Standard': 136.60, 'Off-peak': 107.46}, 'Winter': {'Peak': 397.27, 'Standard': 162.74, 'Off-peak': 114.83}}
time_classification = {0: 'Off-peak', 1: 'Off-peak', 2: 'Off-peak', 3: 'Off-peak', 4: 'Off-peak', 5: 'Off-peak', 6: 'Off-peak', 7: 'Peak', 8: 'Peak', 9: 'Peak', 10: 'Peak', 
                    11: 'Standard', 12: 'Standard', 13: 'Standard', 14: 'Standard', 15: 'Standard', 16: 'Standard', 17: 'Standard', 18: 'Peak', 19: 'Peak', 20: 'Peak', 21:'Standard', 22:'Standard'
                    , 23:'Standard'}

#list containing list of solar radiation (W/m^2) per time period 
#solar = [733.18, 438.14]
data_path = Path('Solar_Radiation_Ordered.csv')
data_file = pd.read_csv(data_path)
data_file = pd.DataFrame(data_file)

row = data_file[data_file.Date == 20160202]
solar = row['G'].to_list()
#print('Solar for 01/02/2016:', solar)

#k_tim is the grid c/kwh price for a time period- looking at Standard time period in Summer here.  This is updated in the for loop
k_tim = 136.60
#area of one of the seven solar panels being used in m^2
A = 2*0.994
#one module is 17.64% efficient
n_pv = 0.1764
#efficiency loss parameter. According to [49] eff = 0.08 (inverter losses) + 0.02 (some modules not behaving as well as others) + 0.002 (resistive loss) + assume no temp and suntracking losses + 0.05 (damage + soiling losses )
eff = 0.152
#setting this for testing purposes
hours = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18 , 19, 20, 21, 22, 23]

#universal battery paramaters
SOC_max = 0.85*3.7
SOC_min = 0.25*3.7

num_agents = len(solar_panels)

#starting SOC_bat for all agents
#SOC_bat = 0.7*3.7*np.ones([num_agents, 1])

# #get battery SOC data from the previous day 
data_path = Path('SOC_Tests.csv')
data_file = pd.read_csv(data_path)
data_file = pd.DataFrame(data_file)
SOC = data_file[data_file.Time_Period == 0]
SOC = SOC['SOC (%)'].to_list()
num_agents = 5
SOC_bat = np.zeros([num_agents, 1])


for i in range(num_agents):
   SOC_bat[i] = SOC[i]/100 * 3.7

#create dataframes to store info you'd like to save to .csv files
TradesDF = pd.DataFrame(columns=['Agent#','Time Period', 'TradeID', 'Quantity (kWh)', 'Price (c/kWh)', 'Avg. Price for Time Period (c/kwh)', 'Amount paid/received for Trade Transaction (c)'])
PowerPointsDF = pd.DataFrame(columns = ['Agent#', 'Time Period', 'Battery Charge (kWh)', 'Grid Export (kWh)', 'Grid Household Load (kWh)', 'Battery Discharge (kWh)', 'Solar Output (kWh)', 'Grid Import (kWh)', 'Social Welfare (R)'])
TotalSocialWelfareDF = pd.DataFrame(columns = ['Time Period', 'Total Social Welfare (R/kwh)'])
SolarDF = pd.DataFrame(columns=['Agent#','Time Period', 'Solar Irradiation (W/m^2)', 'Num_solar panels', 'Solar Output energy (kWh)'])
SOC_DF = pd.DataFrame(columns=['Agent#', 'Time Period', 'SOC (%)'])
Metrics_DF = pd.DataFrame(columns = ['Time Period', 'Num Iterations', 'Time (s)'])
Price_DF = pd.DataFrame(columns = ['Time Period', 'Avg Price (c/kwh)'])
Residuals_DF = pd.DataFrame(columns = ['Iteration', 'Global Prim', 'Global Dual'])
Times_DF = pd.DataFrame(columns = ['Iteration', 'Total Simulation Time'])

#set up smart contract connections
ganache_url = "http://127.0.0.1:8545"

web3 =Web3(Web3.HTTPProvider(ganache_url))

#Check if node is connected
print(web3.isConnected())

#smart contract address
address = web3.toChecksumAddress('0x6b3e3a86f7022A3d043fBF2A99bC04deCe476149')

#how to import abi and bytecode using truffle 
PATH_TRUFFLE_WK = 'C:/Users/Inessa/Desktop/4th_Year/FYP/Methodology_Eth/energy'
truffleFile = json.load(open(PATH_TRUFFLE_WK + '/build/contracts/Energy.json'))
abi = truffleFile['abi']
bytecode = truffleFile['bytecode']

#fetch the smart contract
contract = web3.eth.contract(address=address, abi =abi)

#if this is the first time running this integration code for this smart contract- admin needs to add the peers participating in trading
# web3.eth.defaultAccount = web3.eth.accounts[0]
# for i in range(num_agents):
#     tx_hash = contract.functions.addPeer(str(web3.eth.accounts[i+1]), True, 1).transact()
#     web3.eth.waitForTransactionReceipt(tx_hash)
#     print("Successfully added peer", i+1)
# print('Peers added')

#if you have run this before- deregister peers first
for i in range(num_agents):
   web3.eth.defaultAccount = web3.eth.accounts[i+1]
   tx_hash = contract.functions.deregisterPeer().transact()
   web3.eth.waitForTransactionReceipt(tx_hash)
print('Peers deregistered')

#admin needs to start the trading period
web3.eth.defaultAccount = web3.eth.accounts[0]
cat = pytz.timezone('Africa/Johannesburg')
today = datetime.time(datetime.now(tz = cat))
time = today.hour
today = datetime.date(datetime.now(tz = cat))
date = str(today)
tx_hash = contract.functions.startTradingPer(date, time).transact()
web3.eth.waitForTransactionReceipt(tx_hash)
print("Trading period started")

#register peers to be involved in blockchain trading
# if you try to register peer twice - will get an error
for i in range(1, num_agents+1):
    web3.eth.defaultAccount = web3.eth.accounts[i]
    print(web3.eth.defaultAccount)
    tx_hash = contract.functions.registerPeer().transact()
    print("Registering peer", i, "to trade in time period")
    web3.eth.waitForTransactionReceipt(tx_hash)
    print("Peer", i, "successfully registered.  Take a look!")
    address = str(web3.eth.accounts[i])
    peer1 = contract.functions.peers(address).call()
    print(peer1)

#look at one time period for this test:
time_period = 1
tim = time_classification[time_period]
k_tim = grid_price[season][tim] * 0.9
#first create all agents
for i in range(num_agents):
        agent, agents = func.createAgent(loads[i][time_period], SOC_bat[i][0], solar_panels[i], agents, solar, time_period, k_tim)
        SolarDF = func.createSolarFile(agent, time_period, solar, SOC_bat[i][0], solar_panels[i], SolarDF)
print('Making agents complete')

#for this test- iterations should not exceed 400
max_Iter = 500
#the higher the commission fees- the less the trading quantities that occur (makes sense if you think of cost function).  
#the higher the trade commission fees- the lower the trading price, but because of lower trade quantities (zero if possible) - less economic benefit for prosumers
Commission_Fees = 0 #- for decentralized models (for economic comparison)
#Commission_Fees = 0.1 - used and it worked for the first day#- for centralized models 50c/kwh or might use 1c/kwh as done in [12] - using 1c/kwh gets almost the same price as having 0 commission fees and trades are at a slightly lower quantity
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
print(part)
#create players for this optimisation run
players = func.createPlayers(agents, part, preferences, penalty_factor)
prim = float('inf')
dual = float('inf')
iteration = 0
SW = 0
simulation_time = 0
optimal = 0
iteration = 0
prim_list = []
window = 25
#now, going to perform optimisation for time period
while ((optimal == 0) and (iteration<max_Iter)):
    temp = np.copy(Trades)
    start_time = TIME.time()
    iteration = contract.functions.iteration().call()
    print('iter', iteration)
    #each agent must first perform local optimisation- then, add local residuals
    for i in range(num_agents):
        #print('i', i)
        temp[:,i] = players[i].optimize(Trades[i,:])
        #print('Trades', i+1, temp[:,i])
        Prices[:,i][part[i,:].nonzero()] = players[i].y
        #print("At prices:", Prices[:,i])
        web3.eth.defaultAccount = web3.eth.accounts[i+1]
        #print(players[i].Res_primal)
        #print(players[i].Res_dual)
        primal_res = players[i].Res_primal * 10000
        primal_res = round(primal_res)
        dual_res = players[i].Res_dual * 10000
        dual_res = round(dual_res)
        tx_hash = contract.functions.addLocalRes(primal_res, dual_res).transact()
        web3.eth.waitForTransactionReceipt(tx_hash)
        #print('Local residuals added by agent:', i +1)
        #print(contract.functions.localres(str(web3.eth.accounts[i+1])).call())
        #print('Here is the state of the global pres:', contract.functions.global_pres().call())
        #print('Here is the state of the global dres:', contract.functions.global_dres().call())
    test_prim = sum(round(players[i].Res_primal * 10000) for i in range(num_agents))
    test_dual = sum(round(players[i].Res_dual * 10000) for i in range(num_agents))
    # print('From Prosumer class global prim:', test_prim)
    # print('From Prosumer class dual prim', test_dual)
    # print(contract.functions.global_pres().call())
    # print(contract.functions.global_dres().call())
    row = Residuals_DF.shape[0]
    Residuals_DF.loc[row, 'Iteration']  = iteration  
    Residuals_DF.loc[row, 'Global Prim'] = contract.functions.global_pres().call()
    Residuals_DF.loc[row, 'Global Dual'] = contract.functions.global_dres().call()
    Residuals_DF.to_csv(r'C:\Users\Inessa\Desktop\4th_Year\FYP\Methodology_Eth\combination\Results\Residuals.csv')
    prim_list.append(contract.functions.global_pres().call())
    if (len(prim_list) ==  window):
            prim_list, penalty_factor, players = func.checkRho(prim_list, penalty_factor, players)  
    print('Temp:', temp)
    #now, check if trades are optimal
    optimal = contract.functions.is_optimal().call()
    #if not optimal - need to submit trade bids
    if (optimal == 0):
        for i in range(num_agents):
            p = part[i].nonzero()[0]
            for j in range(len(p)):
                sender = str(web3.eth.accounts[i+1])
                web3.eth.defaultAccount = web3.eth.accounts[i+1]
                buyer = p[j] +1
                buyer = str(web3.eth.accounts[buyer])
                amount = temp[p[j].tolist(), i] * 10000
                amount = amount.tolist()
                amount = round(amount)
                price_c = Prices[:,i][p[j]] * 10000
                price_c = price_c.tolist()
                price_c = round(price_c)
                tx_hash = contract.functions.addTradeBid(sender, buyer, amount, price_c).transact()
                web3.eth.waitForTransactionReceipt(tx_hash)
                tradeID = (i+1)*10 + p[j].tolist() + 1
                trade_bids = contract.functions.trade_bids_mapping(tradeID).call()
                #print("Trade bid", i+1, "to", p[j]+1 ,"submitted.  Take a look!")
                #print(trade_bids)
                #print("Total number of trade bids:")
                #print(contract.functions.tradeCountIter().call())
            #print("All trade bids submitted")
            #now, each agent needs to collect all trade bids and repeat the process
        num_tradebids = contract.functions.tradeCountIter().call()
        for i in range(num_agents):
            address = str(web3.eth.accounts[i+1])
            peer = contract.functions.peers(address).call()
            peer_id = peer[0]
            p = part[i].nonzero()[0]
            #print(p)
            for j in range(len(p)):
                peer_from = p[j] + 1
                peer_from = peer_from.tolist()
                trade_id = peer_from*10 + peer_id
                trade_temp = contract.functions.trade_bids_mapping(trade_id).call()
                pos = p[j]
                pos = pos.tolist()
                Trades[i, pos] = trade_temp[2]/10000
                temp = Trades
            print("Trades for", i+1, "are these:")
            print(Trades[i,:])
    end_time = TIME.time()
    row = Times_DF.shape[0]
    Times_DF.loc[row, 'Iteration'] = iteration
    Times_DF.loc[row, 'Total Simulation Time'] = end_time - start_time
    Times_DF.to_csv(r'C:\Users\Inessa\Desktop\4th_Year\FYP\Methodology_Eth\combination\Results\Times.csv')
    print('Simulation Time:', end_time - start_time)
    # #update SOC
SW = sum([players[i].SW for i in range(num_agents)])
ind_row = TotalSocialWelfareDF.shape[0]
TotalSocialWelfareDF.loc[ind_row, 'Time Period'] = time_period
TotalSocialWelfareDF.loc[ind_row, 'Total Social Welfare (R/kwh)'] = SW
Price_avg = Prices[Prices!=0].mean()
PowerPointsDF = func.createPowerPoints(players, time_period, PowerPointsDF)
TradesDF = func.createTradeFile(players, TradesDF, time_period, Price_avg, part)
Metrics_DF = func.createMetricsFile(Metrics_DF, simulation_time, time_period, iteration)
ind_row = Price_DF.shape[0]
Price_DF.loc[ind_row, 'Time Period'] = time_period
Price_DF.loc[ind_row, 'Avg Price (c/kwh)'] = Price_avg*100


TradesDF.to_csv(r"C:\Users\Inessa\Desktop\4th_Year\FYP\Methodology_Eth\combination\Results\Trade_Tests.csv")
SolarDF.to_csv(r'C:\Users\Inessa\Desktop\4th_Year\FYP\Methodology_Eth\combination\Results\Solar_Tests.csv')
Metrics_DF.to_csv(r'C:\Users\Inessa\Desktop\4th_Year\FYP\Methodology_Eth\combination\Results\Overall Optimisation Metrics Test.csv') 
Price_DF.to_csv(r'C:\Users\Inessa\Desktop\4th_Year\FYP\Methodology_Eth\combination\Results\Average Trading Prices.csv')
PowerPointsDF.to_csv(r'C:\Users\Inessa\Desktop\4th_Year\FYP\Methodology_Eth\combination\Results\Power Set Points.csv')
TotalSocialWelfareDF.to_csv(r'C:\Users\Inessa\Desktop\4th_Year\FYP\Methodology_Eth\combination\Results\Social Welfare.csv')
pbd = []
pbc = []
for i in range(num_agents):
    pbd.append([players[i].variables.p[3].x])
    pbc.append([players[i].variables.p[0].x])
pbd = np.asarray(pbd)
pbc = np.asarray(pbc)
    #update state of all batteries
SOC_bat = SOC_bat - pbc*0.99 - pbd*0.99
SOC_DF = func.createSOCFile(SOC_bat, SOC_DF, time_period)
SOC_DF.to_csv(r'C:\Users\Inessa\Desktop\4th_Year\FYP\Methodology_Eth\combination\Results\SOC_Tests.csv')
