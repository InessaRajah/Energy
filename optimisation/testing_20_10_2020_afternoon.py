#perform optimisation for all peers
import gurobipy as gb
import time
from Prosumer import Prosumer
import numpy as np

##functions
#create a, b, Pmax and Pmin values for prosumer's assets
def createAssetsPro(assets_con, assets_prod):
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
        
        elif con_asset['Type'] == 'HouseholdLoad':
            a = 0
            b = 0
            ub = sum(con_asset['Upper Consumption'])/len(con_asset['Upper Consumption'])
            print(ub)
            lb = sum(con_asset['Lower Consumption'])/len(con_asset['Lower Consumption'])
            print(lb)
            asset_list[i] = {'Type': con_asset['Type'], 'a': a, 'b': b, 'ub': -lb, 'lb': -ub}

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
                ub = prod_asset['Upper Production'][0]
                lb = prod_asset['Lower Production'][0]
                asset_list[i] = {'Type': prod_asset['Type'], 'a': a, 'b': b, 'ub': ub, 'lb': lb}
        
        elif prod_asset['Type'] == 'GridImport':
            a = 0 
            b = prod_asset['Upper Price'][0]
            ub = 10
            lb = 0
            asset_list[i] = {'Type': prod_asset['Type'], 'a': a, 'b': b, 'ub': ub, 'lb': lb}
        else:
                Pri_min = prod_asset['Lower Price']
                Pri_min = np.asarray(Pri_min)
                #conver to $/kwh 
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
                asset_list[i] = {'Type': prod_asset['Type'], 'a': a[0], 'b': b[0], 'ub': ub[0], 'lb': lb[0]}
    
    return asset_list


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

#create individual agents            
def createAgent(Type, assets_con, assets_prod, existing_agents):
    asset_list = createAssetsPro(assets_con, assets_prod)
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

#intialization stuff
time_periods = 2
load = []
solar_radiation = []
SOC_init = 0.7*3.7
SOC_max = 0.85*3.7
SOC_min = 0.25*3.7
grid_price_con = 148.09
grid_price_pro = {'Summer': {'Peak': 172.68, 'Standard': 136.60, 'Off-peak': 107.46}, 'Winter': {'Peak': 397.27, 'Standard': 162.74, 'Off-peak': 114.83}}

#need to define agents individually and in list   
agents = []
#Generated Load Profiles, Example 1
assets_con0 = {0: {'Type': 'BatteryCharge', 'Lower Price': [11.0, 13.5], 'Upper Price': [14.5, 17.0], 'Lower Consumption': [0, 0.1], 'Upper Consumption': [0.7, 0.74]}, 
            1: {'Type': 'GridExport', 'Lower Price': [0], 'Upper Price': [0], 'Lower Production': [0], 'Upper Production': [10]},
            2: {'Type': 'HouseholdLoad', 'Lower Price': [0], 'Upper Price': [0], 'Lower Consumption': [0.100335206*0.9, 0.1003352055], 'Upper Consumption': [0.100335206, 0.100335206*1.1]}}
assets_prod0 = {0: {'Type': 'BatteryDischarge', 'Lower Price': [11.0, 13.5], 'Upper Price': [14.5, 17.0], 'Lower Production': [0, 0.0001], 'Upper Production': [0.36, 0.37]},
            1: {'Type': 'Solar', 'Lower Price': [0], 'Upper Price': [0], 'Lower Production': [0.136], 'Upper Production': [0.136]},
            2: {'Type': 'GridImport', 'Lower Price': [107.68], 'Upper Price': [107.68], 'Lower Production': [0, 0], 'Upper Production': [10, 10.0001]}} #GridImport cost function based on ranges of grid price depending on Time of Use in Summer
agent0, agents = createAgent('Prosumer', assets_con0, assets_prod0, agents)

#Generated Load Profiles, Example 2
assets_con1 = {0: {'Type': 'BatteryCharge', 'Lower Price': [11.0, 13.5], 'Upper Price': [14.5, 17.0], 'Lower Consumption': [0, 0.1], 'Upper Consumption': [0.7, 0.74]}, 
            1: {'Type': 'GridExport', 'Lower Price': [0], 'Upper Price': [0], 'Lower Production': [0], 'Upper Production': [10]},
            2: {'Type': 'HouseholdLoad', 'Lower Price': [0], 'Upper Price': [0], 'Lower Consumption': [0.289092163*0.9, 0.2890921625], 'Upper Consumption': [0.289092163, 0.289092163*1.1]}}
assets_prod1 = {0: {'Type': 'BatteryDischarge', 'Lower Price': [11.0, 13.5], 'Upper Price': [14.5, 17.0], 'Lower Production': [0, 0.0001], 'Upper Production': [0.36, 0.37]},
            1: {'Type': 'Solar', 'Lower Price': [0], 'Upper Price': [0], 'Lower Production': [0.136], 'Upper Production': [0.136]},
            2: {'Type': 'GridImport', 'Lower Price': [107.68], 'Upper Price': [107.68], 'Lower Production': [0, 0], 'Upper Production': [10.001, 10]}} #GridImport cost function based on ranges of grid price depending on Time of Use in Summer
agent1, agents = createAgent('Prosumer', assets_con1, assets_prod1, agents)

#Generated Load Profiles, Example 3
assets_con2 = {0: {'Type': 'BatteryCharge', 'Lower Price': [11.0, 13.5], 'Upper Price': [14.5, 17.0], 'Lower Consumption': [0, 0.1], 'Upper Consumption': [0.7, 0.74]}, 
            1: {'Type': 'GridExport', 'Lower Price': [0], 'Upper Price': [0], 'Lower Production': [0], 'Upper Production': [10]},
            2: {'Type': 'HouseholdLoad', 'Lower Price': [0], 'Upper Price': [0], 'Lower Consumption': [0.074726916*0.9, 0.0747269155], 'Upper Consumption': [0.074726916, 0.074726916*1.1]}}
assets_prod2 = {0: {'Type': 'BatteryDischarge', 'Lower Price': [11.0, 13.5], 'Upper Price': [14.5, 17.0], 'Lower Production': [0, 0.0001], 'Upper Production': [0.36, 0.37]},
            1: {'Type': 'Solar', 'Lower Price': [0], 'Upper Price': [0], 'Lower Production': [0.136], 'Upper Production': [0.136]},
            2: {'Type': 'GridImport', 'Lower Price': [107.68], 'Upper Price': [107.68], 'Lower Production': [0, 0], 'Upper Production': [10.001, 10]}} #GridImport cost function based on ranges of grid price depending on Time of Use in Summer
agent2, agents = createAgent('Prosumer', assets_con2, assets_prod2, agents)

#Generated Load Profiles, Example 4
assets_con3 = {0: {'Type': 'BatteryCharge', 'Lower Price': [11.0, 13.5], 'Upper Price': [14.5, 17.0], 'Lower Consumption': [0, 0.1], 'Upper Consumption': [0.7, 0.74]}, 
            1: {'Type': 'GridExport', 'Lower Price': [0], 'Upper Price': [0], 'Lower Production': [0], 'Upper Production': [10]},
            2: {'Type': 'HouseholdLoad', 'Lower Price': [0, 0], 'Upper Price': [0], 'Lower Consumption': [0.088529768*0.9, 0.0885297675], 'Upper Consumption': [0.088529768, 0.088529768*1.1]}} #price range given here is the range of prices in c/kwh that is Summer Time of Use ranges depending on the time
assets_prod3 = {0: {'Type': 'BatteryDischarge', 'Lower Price': [11.0, 13.5], 'Upper Price': [14.5, 17.0], 'Lower Production': [0, 0.0001], 'Upper Production': [0.0, 0.000001]},
            1: {'Type': 'Solar', 'Lower Price': [0], 'Upper Price': [0], 'Lower Production': [0], 'Upper Production': [0]},
            2: {'Type': 'GridImport', 'Lower Price': [148.09], 'Upper Price': [148.09], 'Lower Production': [0, 0], 'Upper Production': [10.001, 10]}} #GridImport cost function based on ranges of grid price depending on Time of Use in Summer
agent3, agents = createAgent('Consumer', assets_con3, assets_prod3, agents)
print(agents)
max_Iter = 30000
Commission_Fees = 0
penalty_factor = 0.001
# penalty_factor = 5e-4
residual_primal = 1e-4
resiudal_dual = 1e-4

#agent0 = {'Index': 0, 'Type': 'Prosumer', 'AssetNum': 5, 'Assets': { 0: {'Type': 'BatteryCharge', 'a': 1111, 'b': 1111, 'ub' : 0, 'lb': -0.74}, 1: {'Type': 'BatteryDischarge', 'a': 1111, 'b': 1111, 'ub' : 0.37, 'lb' : 0}, 
#            2: {'Type': 'Grid', 'a': 0.1, 'b': 2703.98, 'ub' : 10, 'lb' : 0}, 3: {'Type': 'PV', 'a': 0, 'b': 0, 'ub' : 0.0376, 'lb' : 0.0376}, 4: {'Type': 'Load', 'a': 0, 'b': 0, 'ub' : 0, 'lb' : 0}}}


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
#Price_avg = Prices[Prices!=0].mean()
SW = sum([players[i].SW for i in range(num_agents)])
print("Total Social Welfare:", SW)
print(iteration)
print(prim)
print(dual)
print(players[0].variables.t)
print(players[0].variables.t[0].x)
print(players[1].variables.t)
print(players[2].variables.t)
print(players[3].variables.t)
print(players[0].y)
print(players[1].y)
print(players[2].y)
print(players[3].y)
print("prosumer0 battery charge", players[0].variables.p[0].x)
print("prosumer0 grid export", players[0].variables.p[1].x)
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
#print(agents)
