import gurobipy as gb
import time
from Prosumer import Prosumer
import numpy as np

##THIS SCRIPT BUILDS ON TESTING.PY
# Added functionality- automatically generate agents and run optimisation for these agents

#list description of all agents
agents = []

#keep track of how many runs of the optimisation code result in suboptimal results
suboptimal = 0

#create a, b, Pmax and Pmin values for each participant's assets
def createAssets(assets_con, assets_prod):
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
            b = k_tim #change this grid import price for each time period
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

#list of loads[i][j] where i = agent number and j = time_period
loads = [[0.100335206], [0.289092163], [0.074726916], [0.088529768]]

#list of each agents solar panel number
solar_panels = [7, 7, 7, 0]

#list containing list of solar radiation (W/m^2) per time period 
solar = [733]
#k_tim is the grid c/kwh price for a time period- looking at Standard time period in Summer here
k_tim = 136.60
#area of one of the seven solar panels being used in m^2
A = 2*0.994
#one module is 17.64% efficient
n_pv = 0.1764
#efficiency loss parameter. According to [49] eff = 0.08 (inverter losses) + 0.02 (some modules not behaving as well as others) + 0.002 (resistive loss) + assume no temp and suntracking losses + 0.05 (damage + soiling losses )
eff = 0.152
#setting this for testing purposes
time_period = 0

#universal battery paramaters
SOC_max = 0.85*3.7
SOC_min = 0.25*3.7

#for each agent in each time period, need to assign BatterCharge[Upper Consumption], Solar[Lower Production] = Solar[Upper Production] and HouseholdLoad[]
assets_con_temp = {0: {'Type': 'BatteryCharge', 'Lower Price': [11.0, 13.5], 'Upper Price': [14.5, 17.0], 'Lower Consumption': [0, 0.1], 'Upper Consumption': []}, 
            1: {'Type': 'GridExport', 'Lower Price': [0], 'Upper Price': [0], 'Lower Production': [0], 'Upper Production': [10]},
            2: {'Type': 'HouseholdLoad', 'Lower Price': [101, 107], 'Upper Price': [107.36, 107.46], 'Lower Consumption': [], 'Upper Consumption': []}}
assets_prod_temp = {0: {'Type': 'BatteryDischarge', 'Lower Price': [11.0, 13.5], 'Upper Price': [14.5, 17.0], 'Lower Production': [0, 0.0001], 'Upper Production': [0.36, 0.37]},
            1: {'Type': 'Solar', 'Lower Price': [0], 'Upper Price': [0], 'Lower Production': [], 'Upper Production': []},
            2: {'Type': 'GridImport', 'Lower Price': [107.46, 136.60], 'Upper Price': [136.61, 172.66], 'Lower Production': [0, 0], 'Upper Production': [10, 10.0001]}} #GridImport cost function based on ranges of grid price depending on Time of Use in Summer

#create assets_con and assets_pro list to input into createAssets
def createParameters(load, SOC_bat, solar_num):
    assets_con = assets_con_temp
    assets_prod = assets_prod_temp

    #battery charging upper consumption
    max_charge = SOC_max - SOC_bat
    max_charge_temp = [round((max_charge*0.9), 2), round(max_charge, 2)]
    assets_con[0]['Upper Consumption'] = max_charge_temp

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
def createAgent(load, SOC_bat, solar_num, existing_agents):
    if (solar_num):
        Type = 'Prosumer'
    else:
        Type = 'Consumer'
    assets_con, assets_prod = createParameters(load, SOC_bat, solar_num)
    #print(assets_con)
    #print(assets_prod)
    asset_list = createAssets(assets_con, assets_prod)
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
def createPlayers(agents, part, preferences, penalty_factor):
    players = [None] * len(agents)
    for i in range(len(agents)):
        p = Prosumer(agents[i], part, preferences, penalty_factor)
        players[i] = p
    return players

num_agents = len(solar_panels)

#starting SOC_bat for all agents
SOC_bat = 0.7*3.7*np.ones([num_agents, 1])

#cycle through and create agents
for i in range(num_agents):
    print(i)
    agent, agents = createAgent(loads[i][time_period], SOC_bat[i][0], solar_panels[i], agents)


max_Iter = 1500
#Commission_Fees = 0.01 - for centralized models (for economic comparison)
Commission_Fees = 0
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
players = createPlayers(agents, part, preferences, penalty_factor)
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
print(Price_avg)
SW = sum([players[i].SW for i in range(num_agents)])
print("Total Social Welfare:", SW)
print(iteration)
if iteration == 1000:
    suboptimal = suboptimal + 1
print(prim)
print(dual)
print(players[0].variables.t)
print(players[1].variables.t)
print(players[2].variables.t)
print(players[3].variables.t)
print(players[0].y)
print(players[1].y)
print(players[2].y)
print(players[3].y)
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
print("prosumer1 battery discharge", players[1].variables.p[3])
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