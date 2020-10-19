#perform optimisation for all peers
import numpy as np
import numpy as np
#list description of all agents
agents = []
assets_con1 = {0: {'Type': 'BatteryCharge', 'Lower Price': [11.0, 13.5], 'Upper Price': [14.5, 17.0], 'Lower Consumption': [0, 0.1], 'Upper Consumption': [0.7, 0.74]}, 
            1: {'Type': 'GridExport', 'Lower Price': [0], 'Upper Price': [0], 'Lower Production': [0], 'Upper Production': [10]},
            2: {'Type': 'HouseholdLoad', 'Lower Price': [50, 54], 'Upper Price': [55, 56], 'Lower Consumption': [0.100335206*0.9, 0.1003352055], 'Upper Consumption': [0.100335206, 0.100335206*1.1]}}
assets_prod1 = {0: {'Type': 'BatteryDischarge', 'Lower Price': [11.0, 13.5], 'Upper Price': [14.5, 17.0], 'Lower Production': [0, 0.0001], 'Upper Production': [0.36, 0.37]},
            1: {'Type': 'Solar', 'Lower Price': [0], 'Upper Price': [0], 'Lower Production': [0.136], 'Upper Production': [0.136]},
            2: {'Type': 'GridImport', 'Lower Price': [107.46, 136.60], 'Upper Price': [136.61, 172.66], 'Lower Production': [0, 0], 'Upper Production': [10.001, 10]}} #GridImport cost function based on ranges of grid price depending on Time of Use in Summer
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
                if prod_asset['Type']=='BatteryDischarge':
                    print(a)
                    print(b)
                    print(ub)
                    print(lb)
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

#need to define agents individually and in list
#assets for prosumer one- a consumer would only have HouseholdLoad in assets_con and GridImport in assets_prod

agent0, agents = createAgent('Prosumer', assets_con1, assets_prod1, agents)


assets_con2 = {0: {'Type': 'BatteryCharge', 'Lower Price': [11.0, 13.5], 'Upper Price': [14.5, 17.0], 'Lower Consumption': [0, 0.1], 'Upper Consumption': [0.7, 0.74]}, 
            1: {'Type': 'GridExport', 'Lower Price': [0], 'Upper Price': [0], 'Lower Production': [0], 'Upper Production': [10]},
            2: {'Type': 'HouseholdLoad', 'Lower Price': [50, 54], 'Upper Price': [55, 56], 'Lower Consumption': [0.289092163*0.9, 0.2890921625], 'Upper Consumption': [0.289092163, 0.289092163*1.1]}}
assets_prod2 = {0: {'Type': 'BatteryDischarge', 'Lower Price': [11.0, 13.5], 'Upper Price': [14.5, 17.0], 'Lower Production': [0, 0.0001], 'Upper Production': [0.36, 0.37]},
            1: {'Type': 'Solar', 'Lower Price': [0], 'Upper Price': [0], 'Lower Production': [0.136], 'Upper Production': [0.136]},
            2: {'Type': 'GridImport', 'Lower Price': [107.46, 136.60], 'Upper Price': [136.61, 172.66], 'Lower Production': [0, 0], 'Upper Production': [10.001, 10]}} #GridImport cost function based on ranges of grid price depending on Time of Use in Summer
agent1, agents = createAgent('Prosumer', assets_con2, assets_prod2, agents)


print(agents)
agent = agents[0]
print(agent)
print(agent['Assets'][0]['a'])

