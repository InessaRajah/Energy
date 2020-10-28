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
print('Test1: Peer3')

ganache_url = "http://127.0.0.1:8545"

web3 =Web3(Web3.HTTPProvider(ganache_url))

#Check if node is connected
print('Peer3:', web3.isConnected())

num_agent = 3

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

init = contract.functions.init().call()

#check if trading period has started, if so - register for trading
while (init == 0):
   init = init = contract.functions.init().call()

tx_hash = contract.functions.registerPeer().transact()
print("Registering peer", num_agent, "to trade in time period")
web3.eth.waitForTransactionReceipt(tx_hash)
print("Peer", num_agent, "successfully registered.  Take a look!")
address = str(web3.eth.accounts[num_agent])
peer1 = contract.functions.peers(address).call()
print(peer1)

##initiation stuff needed to create agent as a player in the time period
#list description of all agents
agents = []

#keep track of how many runs of the optimisation code result in suboptimal results
suboptimal = 0

#set the season being considered
season = 'Summer'

#list of loads[i][j] where i = agent number and j = time_period
#loads = [[0.100335206], [0.289092163], [0.074726916], [0.088529768]]
#loads = [[0.100335206, 0.145744248] , [0.289092163, 0.232237399], [0.074726916, 0.006], [0.088529768,  0.048454915]]
loads = []
data_path = Path('JulyProfiles3.csv')
data_file = pd.read_csv(data_path)
data_file = pd.DataFrame(data_file)
data_file = data_file.drop(columns = ['Electricity.Timestep', 'Sum', '[kWh]'])
row1 = data_file[data_file.Time == '2016/07/02']
load1 = row1['Proper kWh'].to_list()
loads.append(load1)

#list of each agents solar panel number
#solar_panels = [7, 7, 5, 1]
solar_panels = [7, 7, 5, 1, 4]


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
print('Solar for 02/07/2016:', solar)
#k_tim is the grid c/kwh price for a time period- looking at Standard time period in Summer here.  This is updated in the for loop
k_tim = 107.46 * 0.9
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

#get battery SOC data from the previous day 
data_path = Path('SOC_Tests.csv')
data_file = pd.read_csv(data_path)
data_file = pd.DataFrame(data_file)
SOC = data_file[data_file.Time_Period == 23]
SOC = SOC['SOC (%)'].to_list()
num_agents = 5
SOC_bat = np.zeros([num_agents, 1])


for i in range(num_agents):
   SOC_bat[i] = SOC[i]/100 * 3.7

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

#for testing purposes
time_period = 0


agent, agents = func.createAgent(loads[0][time_period], SOC_bat[num_agent-1][0], solar_panels[num_agent-1], agents, solar, time_period, k_tim)
SolarDF = func.createSolarFile(agent, time_period, solar, SOC_bat[num_agent-1][0], solar_panels[num_agent-1], SolarDF)
print('Made an agent', num_agent)

    #the higher the commission fees- the less the trading quantities that occur (makes sense if you think of cost function).  
    #the higher the trade commission fees- the lower the trading price, but because of lower trade quantities (zero if possible) - less economic benefit for prosumers
Commission_Fees = 0 #- for decentralized models (for economic comparison)
    #Commission_Fees = 0.5 #- for centralized models 50c/kwh or might use 1c/kwh as done in [12] - using 1c/kwh gets almost the same price as having 0 commission fees and trades are at a slightly lower quantity
    #using 50c/kwh commission fee results in vastly lower prices but basically 0 traded quantities
penalty_factor = 0.01

preferences = Commission_Fees* np.ones(num_agents-1)

part = np.ones([num_agents, num_agents])
for i in range(num_agents):
    for j in range(num_agents):
        if (i == j):
            part[i][j] = 0

player = func.createPlayers(agents, part, preferences, penalty_factor, (num_agent -1))
Trades = np.zeros([num_agents])
optimal = False
start_time = TIME.time()

print('Performing Local Optimisation')
temp = player[0].optimize(Trades)
print(temp)
prices = player[0].y

#add local residuals to blockchain
primal_res = player[0].Res_primal * 10000
primal_res = round(primal_res)
dual_res = player[0].Res_dual * 10000
dual_res = round(dual_res)
sender = str(web3.eth.accounts[num_agent-1])
tx_hash = contract.functions.addLocalRes(primal_res, dual_res).transact()
web3.eth.waitForTransactionReceipt(tx_hash)
print('Added local residual')

num_residuals = contract.functions.localresCounter().call()
while(num_residuals != (num_agents)):
   num_residuals = contract.functions.localresCounter().call()

# #once every participant has submitted local residuals, check the contract to see if 
optimal = contract.functions.is_optimal().call()

   # #if not optimal- need to send trade bids to blockchain so they can be received by other agents
if (optimal == 0):
   p = part[num_agent-1].nonzero()[0]
   print(p)
   for j in range(len(p)):
      sender = str(web3.eth.accounts[num_agent])
      buyer = p[j].tolist()
      amount = temp[buyer] * 10000
      amount = amount.tolist()
      amount = round(amount)
      buyer = str(web3.eth.accounts[buyer+1])
      price_c = prices[j] * 10000
      price_c = price_c.tolist()
      price_c = round(price_c)
      tx_hash = contract.functions.addTradeBid(sender, buyer, amount, price_c).transact()
      web3.eth.waitForTransactionReceipt(tx_hash)
      tradeID = (num_agent)*10 + p[j].tolist() + 1
      trade_bids = contract.functions.trade_bids_mapping(tradeID).call()
      print("Trade bid", num_agent, "to", p[j]+1 ,"submitted.  Take a look!")
      print(trade_bids)
      print("Total number of trade bids:")
      print(contract.functions.tradeCountIter().call())
   print("All trade bids from peer", num_agent, "submitted")
