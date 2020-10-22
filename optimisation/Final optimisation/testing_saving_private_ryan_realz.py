import gurobipy as gb
import time
from Prosumer import Prosumer
import numpy as np
import functions as func
import pandas as pd

##THIS SCRIPT BUILDS ON TESTING_SAVING_PRIVATE_RYAN.PY
# Added functionality- save results in .csv files

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
#cycle through and create agents
for t in range(len(hours)):
    agents = []
    time_period = hours[t]
    tim = time_classification[13+t]
    k_tim = grid_price[season][tim]
    print(k_tim)
    print(SOC_bat)
    for i in range(num_agents):
        print(i)
        print('num panels', solar_panels[i])
        agent, agents = func.createAgent(loads[i][time_period], SOC_bat[i][0], solar_panels[i], agents, solar, time_period, k_tim)
        SolarDF = func.createSolarFile(agent, time_period, solar, SOC_bat[i][0], solar_panels[i], SolarDF)

    print("TIME PERIOD:", t)
    max_Iter = 1500
    #Commission_Fees = 1 - for centralized models (for economic comparison)
    Commission_Fees = 0.05
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
    start_time = time.time()

    #local optimisation function
    while ((prim > residual_primal or dual>resiudal_dual) and iteration< max_Iter):
        iteration+=1
        temp = np.copy(Trades)
        for i in range(num_agents):
            temp[:,i] = players[i].optimize(Trades[i,:])
            Prices[:,i][part[i,:].nonzero()] = players[i].y
        Trades = np.copy(temp)
        prim = sum([players[i].Res_primal for i in range(num_agents)])
        dual = sum([players[i].Res_dual for i in range(num_agents)])
        lapsed = time.time()-start_time
            
    simulation_time += lapsed
    Price_avg = Prices[Prices!=0].mean()
    print("Avg Price:", Price_avg)
    SW = sum([players[i].SW for i in range(num_agents)])
    print("Total Social Welfare:", SW)
    print(iteration)
    if iteration == 1000:
        suboptimal = suboptimal + 1
    print(prim)
    print(dual)
    print(players[0].variables.t[0].x)
    print(players[1].variables.t)
    print(players[2].variables.t)
    print(players[3].variables.t)
    print(players[0].y[0])
    print("prosumer0 battery charge", players[0].variables.p[0])
    print("prosumer0 grid export", players[0].variables.p[1])
    print("prosumer0 grid household load", players[0].variables.p[2])
    print("prosumer0 battery discharge", players[0].variables.p[3])
    print("prosumer0 solar", players[0].variables.p[4])
    print("prosumer0 grid import", players[0].variables.p[5])
    #print(players[1].variables.p)
    print("######################################")
    print("prosumer1 battery charge", players[1].variables.p[0])
    print("prosumer1 grid export", players[1].variables.p[1])
    print("prosumer1 grid household load", players[1].variables.p[2])
    print("prosumer1 battery discharge", players[1].variables.p[3].x)
    print("prosumer1 solar", players[1].variables.p[4])
    print("prosumer1 grid import", players[1].variables.p[5])
    print("######################################")
    print("prosumer2 battery charge", players[2].variables.p[0])
    print("prosumer2 grid export", players[2].variables.p[1])
    print("prosumer2 grid household load", players[2].variables.p[2])
    print("prosumer2 battery discharge", players[2].variables.p[3])
    print("prosumer2 solar", players[2].variables.p[4])
    print("prosumer2 grid import", players[2].variables.p[5])
    print("######################################")
    print("prosumer3 battery charge", players[3].variables.p[0])
    print("prosumer3 grid export", players[3].variables.p[1])
    print("prosumer3 grid household load", players[3].variables.p[2])
    print("prosumer3 battery discharge", players[3].variables.p[3])
    print("prosumer3 solar", players[3].variables.p[4])
    print("prosumer3 grid import", players[3].variables.p[5])
    print(simulation_time)
    pbd = []
    pbc = []
    for i in range(num_agents):
        pbd.append([players[i].variables.p[3].x])
        pbc.append([players[i].variables.p[0].x])
    pbd = np.asarray(pbd)
    pbc = np.asarray(pbc)
    #update state of all batteries
    SOC_bat = SOC_bat - pbc*0.99 - pbd*0.99
    TradesDF = func.createTradeFile(players, TradesDF, time_period, Price_avg, part)
    SOC_DF = func.createSOCFile(SOC_bat, SOC_DF, time_period)


TradesDF.to_csv('Trade_Tests.csv')
SolarDF.to_csv('Solar_Tests.csv')
SOC_DF.to_csv('SOC_Tests.csv')
 
