import gurobipy as gb
import time
from Prosumer import Prosumer
import numpy as np
import functions as func
import pandas as pd
from pathlib import Path
import csv

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

# data_path = Path('JulyProfiles6.csv')
# data_file = pd.read_csv(data_path)
# data_file = pd.DataFrame(data_file)
# data_file = data_file.drop(columns = ['Electricity.Timestep', 'Sum', '[kWh]'])
# row2 = data_file[data_file.Time == '2016/07/01']
# load2 = row2['Proper kWh'].to_list()
# loads.append(load2)

# data_path = Path('JulyProfiles7.csv')
# data_file = pd.read_csv(data_path)
# data_file = pd.DataFrame(data_file)
# data_file = data_file.drop(columns = ['Electricity.Timestep', 'Sum', '[kWh]'])
# row3 = data_file[data_file.Time == '2016/07/01']
# load3 = row3['Proper kWh'].to_list()
# loads.append(load3)

# data_path = Path('JulyProfiles8.csv')
# data_file = pd.read_csv(data_path)
# data_file = pd.DataFrame(data_file)
# data_file = data_file.drop(columns = ['Electricity.Timestep', 'Sum', '[kWh]'])
# row4 = data_file[data_file.Time == '2016/07/01']
# load4 = row4['Proper kWh'].to_list()
# loads.append(load4)

# data_path = Path('JulyProfiles9.csv')
# data_file = pd.read_csv(data_path)
# data_file = pd.DataFrame(data_file)
# data_file = data_file.drop(columns = ['Electricity.Timestep', 'Sum', '[kWh]'])
# row5 = data_file[data_file.Time == '2016/07/01']
# load5 = row5['Proper kWh'].to_list()
# loads.append(load5)


#list of each agents solar panel number
solar_panels = [7, 7, 1, 5, 4]
#solar_panels = [5, 10, 5, 7, 7, 6, 10, 8, 4]


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
print('Solar for 03/07/2016:', solar)

#k_tim is the grid c/kwh price for a time period- looking at Standard time period in Summer here.  This is updated in the for loop
k_tim = 136.60
#area of one of the seven solar panels being used in m^2
A = 2*0.994
#one module is 17.64% efficient
n_pv = 0.1764
#efficiency loss parameter. According to [49] eff = 0.08 (inverter losses) + 0.02 (some modules not behaving as well as others) + 0.002 (resistive loss) + assume no temp and suntracking losses + 0.05 (damage + soiling losses )
eff = 1 - 0.152
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
SOC = data_file[data_file.Time_Period == 23]
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
Test_Residuals = pd.DataFrame(columns = ['Iteration', 'Global Prim', 'Global Dual'])
Test_Trades = pd.DataFrame(columns=['Agent#','Time Period', 'TradeID', 'Quantity (kWh)', 'Price (c/kWh)', 'Avg. Price for Time Period (c/kwh)', 'Amount paid/received for Trade Transaction (c)', 'Iteration'])
#cycle through and create agents
for t in range(len(hours)):
    agents = []
    time_period = hours[t]
    tim = time_classification[t]
    k_tim = grid_price[season][tim] * 0.9
    print(k_tim)
    print(SOC_bat)
    for i in range(num_agents):
        print(i)
        print('num panels', solar_panels[i])
        agent, agents = func.createAgent(loads[i][time_period], SOC_bat[i][0], solar_panels[i], agents, solar, time_period, k_tim)
        SolarDF = func.createSolarFile(agent, time_period, solar, SOC_bat[i][0], solar_panels[i], SolarDF)

    print("TIME PERIOD:", t)
    max_Iter = 1500
    #the higher the commission fees- the less the trading quantities that occur (makes sense if you think of cost function).  
    #the higher the trade commission fees- the lower the trading price, but because of lower trade quantities (zero if possible) - less economic benefit for prosumers
    Commission_Fees = 0 #- for decentralized models (for economic comparison)
    #Commission_Fees = 0.1 - used and it worked for the first day#- for centralized models 50c/kwh or might use 1c/kwh as done in [12] - using 1c/kwh gets almost the same price as having 0 commission fees and trades are at a slightly lower quantity
    #using 50c/kwh commission fee results in vastly lower prices but basically 0 traded quantities
    penalty_factor = 0.01
    residual_primal = 1e-4
    resiudal_dual = 1e-4
    #residual_primal = 1e-3
    #resiudal_dual = 1e-3

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
    print('Part', part)
    #create players for this optimisation run
    # for i in range(num_agents):
    #     init = solar_panels[i]*A*n_pv*eff*0.001- loads[i][time_period]
    #     init = init/(num_agents-1)
    #     p = part[i].nonzero()[0]
    #     for j in range(len(p)):
    #         row = p[j].tolist()
    #         Trades[row, i] = init

    # print('Initial Trades', Trades)
    players = func.createPlayers(agents, part, preferences, penalty_factor)
    prim = float('inf')
    dual = float('inf')
    iteration = 0
    SW = 0
    simulation_time = 0
    prim_previous = 0
    lapsed = 0
    start_time = time.time()
    ouch = 0
    prim_list = []
    window = 25
    #local optimisation function
    while ((prim > residual_primal or dual>resiudal_dual) and iteration< max_Iter):
        iteration+=1
        temp = np.copy(Trades)
        for i in range(num_agents):
            temp[:,i] = players[i].optimize(Trades[i,:])
            #print('Trades', i, temp[:,i])
            #print('Primal res', players[i].Res_primal)
            #print('Dual res', players[i].Res_dual)
            Prices[:,i][part[i,:].nonzero()] = players[i].y
        temp = temp*10000
        temp = np.round(temp, 0)
        temp = temp / 10000
        Trades = np.copy(temp)
        prim = sum([players[i].Res_primal for i in range(num_agents)])
        dual = sum([players[i].Res_dual for i in range(num_agents)])
        prim_list.append(prim*10000)    
        if (len(prim_list) ==  window):
            prim_list, penalty_factor, players = func.checkRho(prim_list, penalty_factor, players)   
        #if the trades aren't changing for long enough
        # if (ouch == 50):
        #     ouch = 0
        #     p = part[0].nonzero()[0]
        #     for i in range(len(p)):
        #         row = p[i].tolist()
        #         t1 = Trades[row, i]
        #         t2 = Trades[i, row]
        #         Trades[row, i] = (t1+t2)/2
        if t== 1:
            test_prim = sum(round(players[i].Res_primal * 10000) for i in range(num_agents))
            test_dual = sum(round(players[i].Res_dual * 10000) for i in range(num_agents))
            row = Test_Residuals.shape[0]
            Test_Residuals.loc[row, 'Iteration'] = iteration
            Test_Residuals.loc[row, 'Global Prim'] = test_prim
            Test_Residuals.loc[row, 'Global Dual'] = test_dual
            Test_Residuals.to_csv(r'C:\Users\Inessa\Desktop\4th_Year\FYP\Methodology_Eth\optimisation\Final optimisation\Faster Attempts\Results\Test Residuals.csv')
            row = Test_Trades.shape[0]
            Test_Trades.loc[row, 'Iteration'] = iteration
            Test_Trades = func.createTradeFile(players, Test_Trades, time_period, 0, part)
            Test_Trades.to_csv(r'C:\Users\Inessa\Desktop\4th_Year\FYP\Methodology_Eth\optimisation\Final optimisation\Faster Attempts\Results\Test Trades.csv')
        lapsed = time.time()-start_time
    #print('Trades', Trades)
    print('iterations:', iteration)
    simulation_time += lapsed
    Price_avg = Prices[Prices!=0].mean()
    print("Avg Price:", Price_avg)
    SW = sum([players[i].SW for i in range(num_agents)])
    ind_row = TotalSocialWelfareDF.shape[0]
    TotalSocialWelfareDF.loc[ind_row, 'Time Period'] = time_period
    TotalSocialWelfareDF.loc[ind_row, 'Total Social Welfare (R/kwh)'] = SW
    print("Total Social Welfare:", SW)
    print(iteration)
    if iteration == 1000:
        suboptimal = suboptimal + 1
    # print(prim)
    # print(dual)
    # print(players[0].variables.t)
    # print(players[1].variables.t)
    # print(players[2].variables.t)
    # print(players[3].variables.t)
    # print(players[0].y[0])
    # print("prosumer0 battery charge", players[0].variables.p[0])
    # print("prosumer0 grid export", players[0].variables.p[1])
    # print("prosumer0 grid household load", players[0].variables.p[2])
    # print("prosumer0 battery discharge", players[0].variables.p[3])
    # print("prosumer0 solar", players[0].variables.p[4])
    # print("prosumer0 grid import", players[0].variables.p[5])
    # #print(players[1].variables.p)
    # print("######################################")
    # print("prosumer1 battery charge", players[1].variables.p[0])
    # print("prosumer1 grid export", players[1].variables.p[1])
    # print("prosumer1 grid household load", players[1].variables.p[2])
    # print("prosumer1 battery discharge", players[1].variables.p[3].x)
    # print("prosumer1 solar", players[1].variables.p[4])
    # print("prosumer1 grid import", players[1].variables.p[5])
    # print("######################################")
    # print("prosumer2 battery charge", players[2].variables.p[0])
    # print("prosumer2 grid export", players[2].variables.p[1])
    # print("prosumer2 grid household load", players[2].variables.p[2])
    # print("prosumer2 battery discharge", players[2].variables.p[3])
    # print("prosumer2 solar", players[2].variables.p[4])
    # print("prosumer2 grid import", players[2].variables.p[5])
    # print("######################################")
    # print("prosumer3 battery charge", players[3].variables.p[0])
    # print("prosumer3 grid export", players[3].variables.p[1])
    # print("prosumer3 grid household load", players[3].variables.p[2])
    # print("prosumer3 battery discharge", players[3].variables.p[3])
    # print("prosumer3 solar", players[3].variables.p[4])
    # print("prosumer3 grid import", players[3].variables.p[5])
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
    PowerPointsDF = func.createPowerPoints(players, time_period, PowerPointsDF)
    TradesDF = func.createTradeFile(players, TradesDF, time_period, Price_avg, part)
    SOC_DF = func.createSOCFile(SOC_bat, SOC_DF, time_period)
    Metrics_DF = func.createMetricsFile(Metrics_DF, simulation_time, time_period, iteration)
    ind_row = Price_DF.shape[0]
    Price_DF.loc[ind_row, 'Time Period'] = time_period
    Price_DF.loc[ind_row, 'Avg Price (c/kwh)'] = Price_avg*100

    # print('Test global prim_res', test_prim)
    # print('Test global dual_res', test_dual)




#TradesDF.to_csv('Trade_Tests.csv')
#SolarDF.to_csv('Solar_Tests.csv')
#SOC_DF.to_csv('SOC_Tests.csv')
#etrics_DF.to_csv('Overall Optimisation Metrics Test.csv') 
#Price_DF.to_csv('Average Trading Prices.csv')


TradesDF.to_csv(r"C:\Users\Inessa\Desktop\4th_Year\FYP\Methodology_Eth\optimisation\Final optimisation\Faster Attempts\Results\Trade_Tests.csv")
SolarDF.to_csv(r'C:\Users\Inessa\Desktop\4th_Year\FYP\Methodology_Eth\optimisation\Final optimisation\Faster Attempts\Results\Solar_Tests.csv')
SOC_DF.to_csv(r'C:\Users\Inessa\Desktop\4th_Year\FYP\Methodology_Eth\optimisation\Final optimisation\Faster Attempts\Results\SOC_Tests.csv')
Metrics_DF.to_csv(r'C:\Users\Inessa\Desktop\4th_Year\FYP\Methodology_Eth\optimisation\Final optimisation\Faster Attempts\Results\Overall Optimisation Metrics Test.csv') 
Price_DF.to_csv(r'C:\Users\Inessa\Desktop\4th_Year\FYP\Methodology_Eth\optimisation\Final optimisation\Faster Attempts\Results\Average Trading Prices.csv')
PowerPointsDF.to_csv(r'C:\Users\Inessa\Desktop\4th_Year\FYP\Methodology_Eth\optimisation\Final optimisation\Faster Attempts\Results\Power Set Points.csv')
TotalSocialWelfareDF.to_csv(r'C:\Users\Inessa\Desktop\4th_Year\FYP\Methodology_Eth\optimisation\Final optimisation\Faster Attempts\Results\Social Welfare.csv')
