import gurobipy as gb
import time
from Prosumer import Prosumer
import numpy as np
import pandas as pd

#functions created to be used in other scripts
##CONSTANT VARIABLES
#area of one of the seven solar panels being used in m^2
A = 2*0.994
#one module is 17.64% efficient
n_pv = 0.1764
#efficiency loss parameter. According to [49] eff = 0.08 (inverter losses) + 0.02 (some modules not behaving as well as others) + 0.002 (resistive loss) + assume no temp and suntracking losses + 0.05 (damage + soiling losses )
eff = 0.152
#universal battery paramaters
SOC_max = 0.85*3.7
SOC_min = 0.25*3.7


#create a, b, Pmax and Pmin values for each participant's assets
def createAssets(assets_con, assets_prod, k):
    #need to create a dictionary of assets that can be used to create an agent
    asset_list = dict()
    for i in range(len(assets_con)):
        con_asset = assets_con[i]
        if con_asset['Type'] == 'GridExport':
                a = 0
                b = 0
                ub = 0
                lb = -10
                asset_list[i] = {'Type': con_asset['Type'], 'a': a, 'b': b, 'ub': ub, 'lb': lb}
        else:
                Pri_min = con_asset['Lower Price']
                Pri_min = np.asarray(Pri_min)
                #conver to $/kwh 
                Pri_min = Pri_min / 100
                Pri_max = con_asset['Upper Price']
                Pri_max = np.asarray(Pri_max)
                Pri_max = Pri_max / 100
                Pmax = con_asset ['Lower Consumption']
                Pmax = np.asarray(Pmax)
                Pmax = -Pmax
                Pmin = con_asset['Upper Consumption']
                Pmin = np.asarray(Pmin)
                Pmin = -Pmin
                a, b, ub, lb = UtilityCurvesGenCon(Pri_min, Pri_max, Pmax, Pmin)
                asset_list[i] = {'Type': con_asset['Type'], 'a': a[0], 'b': b[0], 'ub': ub[0], 'lb': lb[0]}

    for i in range(len(assets_con), len(assets_con) + len(assets_prod)):
        prod_asset = assets_prod[i- len(assets_con)]
        if prod_asset['Type'] == 'Solar':
                a = 0
                b = 0
                ub = prod_asset['Upper Production']
                lb = prod_asset['Lower Production']
                asset_list[i] = {'Type': prod_asset['Type'], 'a': a, 'b': b, 'ub': ub, 'lb': lb}
        
        elif prod_asset['Type'] == 'GridImport':
            a = 0 
            b = k/100 #change this grid import price for each time period
            ub = 10
            lb = 0
            asset_list[i] = {'Type': prod_asset['Type'], 'a': a, 'b': b, 'ub': ub, 'lb': lb}
        
        else:
                Pri_min = prod_asset['Lower Price']
                Pri_min = np.asarray(Pri_min)
                #convert to $/kwh 
                Pri_min = Pri_min / 100
                Pri_max = prod_asset['Upper Price']
                Pri_max = np.asarray(Pri_max)
                Pri_max = Pri_max / 100
                Pmax = prod_asset ['Lower Production']
                Pmax = np.asarray(Pmax)
                Pmax = - Pmax
                Pmin = prod_asset['Upper Production']
                Pmin = np.asarray(Pmin)
                Pmin = -Pmin
                a, b, ub, lb = UtilityCurvesGenPro(Pri_min, Pri_max, Pmax, Pmin)
                #if prod_asset['Type']=='BatteryDischarge':
                    #print(a)
                    #print(b)
                    #print(ub)
                    #print(lb)
                asset_list[i] = {'Type': prod_asset['Type'], 'a': a[0], 'b': b[0], 'ub': ub[0], 'lb': lb[0]}
    
    return asset_list

#utility curve used to generate a and b values for consumptive assets cost functions
def UtilityCurvesGenCon(Pri_min, Pri_max, Pmax, Pmin):
    lb = np.around( (Pmin[1] - Pmin[0])*np.random.rand(1) + Pmin[0], decimals = 2)
    ub = np.around( (Pmax[1] - Pmax[0])*np.random.rand(1) + Pmax[0], decimals = 2)
    Lmin = np.around( (Pri_min[1] - Pri_min[0])* np.random.rand(1) + Pri_min[0], decimals = 2)
    Lmax = np.around( (Pri_max[1] - Pri_max[0])* np.random.rand(1) + Pri_max[0], decimals = 2)
    try:
        a = (Lmax-Lmin)/(ub-lb)
    except ZeroDivisionError:
        a = np.zeros(1)
    if (a == float('inf')):
        a = np.zeros(1)
    if (ub - lb == 0):
        a = np.zeros(1)
    b = np.around(Lmax - a*ub, decimals = 5)
    a = np.around(a, 5)
    lb = np.around(lb, 5)
    ub = np.around(ub, 5)
    a= a.tolist()
    b = b.tolist()
    lb = lb.tolist()
    ub = ub.tolist()
    return a, b, ub, lb


#utility curve used to generate a and b values for productive assets cost functions
def UtilityCurvesGenPro(Pri_min, Pri_max, Pmax, Pmin):
    ub = np.around( (Pmin[1] - Pmin[0])*np.random.rand(1) + Pmin[0], decimals = 2)
    lb = np.around( (Pmax[1] - Pmax[0])*np.random.rand(1) + Pmax[0], decimals = 2)
    Lmin = np.around( (Pri_min[1] - Pri_min[0])* np.random.rand(1) + Pri_min[0], decimals = 2)
    Lmax = np.around( (Pri_max[1] - Pri_max[0])* np.random.rand(1) + Pri_max[0], decimals = 2)
    try:
        a = (Lmax-Lmin)/(ub-lb)
    except ZeroDivisionError:
        a = np.zeros(1)
    if (a == float('inf')):
        a = np.zeros(1)
    if (ub - lb == 0):
        a = np.zeros(1)
    b = np.around(Lmax - a*ub, decimals = 5)
    a = np.around(a, 5)
    lb = np.around(lb, 5)
    lb = -lb
    ub = np.around(ub, 5)
    ub = -ub
    a= a.tolist()
    b = b.tolist()
    lb = lb.tolist()
    ub = ub.tolist()

    return a, b, ub, lb



    #for each agent in each time period, need to assign BatterCharge[Upper Consumption], Solar[Lower Production] = Solar[Upper Production] and HouseholdLoad[]
assets_con_temp = {0: {'Type': 'BatteryCharge', 'Lower Price': [80, 90], 'Upper Price': [100, 111], 'Lower Consumption': [0, 0.1], 'Upper Consumption': []}, 
            1: {'Type': 'GridExport', 'Lower Price': [0], 'Upper Price': [0], 'Lower Production': [0], 'Upper Production': [10]},
            2: {'Type': 'HouseholdLoad', 'Lower Price': [101, 107], 'Upper Price': [107.36, 107.46], 'Lower Consumption': [], 'Upper Consumption': []}}
assets_prod_temp = {0: {'Type': 'BatteryDischarge', 'Lower Price': [80, 90], 'Upper Price': [100, 111], 'Lower Production': [0, 0.0001], 'Upper Production': [0.36, 0.37]},
            1: {'Type': 'Solar', 'Lower Price': [0], 'Upper Price': [0], 'Lower Production': [], 'Upper Production': []},
            2: {'Type': 'GridImport', 'Lower Price': [107.46, 136.60], 'Upper Price': [136.61, 172.66], 'Lower Production': [0, 0], 'Upper Production': [10, 10.0001]}} #GridImport cost function based on ranges of grid price depending on Time of Use in Summer

#create assets_con and assets_pro list to input into createAssets
def createParameters(load, SOC_bat, solar_num, solar, time_period):
    assets_con = assets_con_temp
    assets_prod = assets_prod_temp

    #battery charging upper consumption
    max_charge = SOC_max - SOC_bat
    max_charge_temp = [round((max_charge*0.9), 2), round(max_charge, 2)]
    assets_con[0]['Upper Consumption'] = max_charge_temp

    #trying to set max discharge
    max_discharge  = SOC_bat - (0.55*3.7)
    max_discharge_temp = [round((max_discharge*0.9), 2), round(max_discharge, 2)]
    assets_prod[0]['Upper Production'] = max_discharge_temp
    
    #set household load upper and lower consumption
    lower = [load*0.9, load - 0.0000000005]
    upper = [load, load*1.1]
    assets_con[2]['Upper Consumption'] = upper
    assets_con[2]['Lower Consumption'] = lower

    #set solar production
    sol_output = solar_num * 0.001 *(solar[time_period]*A*n_pv*eff)
    assets_prod[1]['Lower Production'] = round(sol_output, 2)
    assets_prod[1]['Upper Production'] = round(sol_output, 2)

    return assets_con, assets_prod

#create individual agents            
def createAgent(load, SOC_bat, solar_num, existing_agents, solar, time_period, k_tim):
    assets_con, assets_prod = createParameters(load, SOC_bat, solar_num, solar, time_period)
    if (solar_num):
        Type = 'Prosumer'
    else:
        Type = 'Consumer'
        assets_prod[0]['Lower Production'] = [0, 0.0001]
        assets_prod[0]['Upper Production'] =[0.00011, 0.00012]
        assets_con[0]['Lower Consumption'] =[0, 0.0001]
        assets_con[0]['Upper Consumption'] = [0.00011, 0.00012]
    #print(assets_con)
    #print(assets_prod)
    agents = existing_agents
    asset_list = createAssets(assets_con, assets_prod, k_tim)
    agent = dict()
    index = len(existing_agents)
    asset_num = len(asset_list)
    agent['Index'] = index
    agent['Type'] = Type
    agent['AssetNum'] = asset_num
    agent['Assets'] = asset_list
    agents.append(agent)
    return agent, agents

#create list of players to participate in trading
def createPlayers(agents, part, preferences, penalty_factor, index):
    players = [None] * len(agents)
    for i in range(len(agents)):
        #print('Agent number:', i, "being made as a player")
        #print(agents[i])
        p = Prosumer(agents[i], part, preferences, penalty_factor, index)
        players[i] = p
    return players

def createTradeFile(players, Trades, time_period, avg_price, part):
    ind_row_current = Trades.shape[0]
    num_agents = len(players)
    num_trades = len(players) - 1
    for i in range(num_agents):
        trades = players[i].variables.t
        partners = part[i].nonzero()[0]
        for j in range(num_trades):
            Trades.loc[ind_row_current, 'Agent#'] = "agent" + str(i+1)
            Trades.loc[ind_row_current, 'Time Period'] = time_period
            Trades.loc[ind_row_current, 'TradeID'] = str(i+1) + str(partners[j]+1)
            Trades.loc[ind_row_current, 'Quantity (kWh)'] = trades[j].x
            Trades.loc[ind_row_current, 'Price (c/kWh)'] = players[i].y[j]*100
            Trades.loc[ind_row_current, 'Avg. Price for Time Period (c/kwh)'] = avg_price*100
            Trades.loc[ind_row_current, 'Amount paid/received for Trade Transaction (c)'] = (avg_price)*100*trades[j].x
            ind_row_current = ind_row_current + 1
    return Trades


def createSolarFile(agent, time_period, solar, SOC_bat, solar_panels, Solar):
    ind_row_current = Solar.shape[0]
    agent_num = agent['Index']
    Solar.loc[ind_row_current, 'Agent#'] = "agent"+str(agent_num+1)
    Solar.loc[ind_row_current, 'Time Period'] = time_period
    Solar.loc[ind_row_current, 'Solar Irradiation (W/m^2)'] = solar[time_period]
    Solar.loc[ind_row_current, 'Num_solar panels'] = solar_panels
    Solar.loc[ind_row_current, 'Solar Output energy (kWh)'] = agent['Assets'][4]['ub']  

    return Solar

def createSOCFile(SOC_bat, SOC_DF, time_period):
    ind_row_current = SOC_DF.shape[0]
    num_agents = len(SOC_bat)
    print(SOC_bat)
    for i in range(num_agents):
        SOC_DF.loc[ind_row_current, 'Agent#'] = 'agent'+str(i+1)
        SOC_DF.loc[ind_row_current, 'Time_Period'] = time_period
        SOC_DF.loc[ind_row_current, 'SOC (%)'] = (SOC_bat[i][0])/3.7 * 100
        ind_row_current= ind_row_current+1
    return SOC_DF


def createMetricsFile(Metrics_DF, simulation_time, time_period, iteration):
    ind_row_current = Metrics_DF.shape[0]
    Metrics_DF.loc[ind_row_current, 'Time Period'] = time_period
    Metrics_DF.loc[ind_row_current, 'Num Iterations'] = iteration
    Metrics_DF.loc[ind_row_current, 'Time (s)'] = simulation_time

    return Metrics_DF