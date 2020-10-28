import subprocess as subprocess
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


ganache_url = "http://127.0.0.1:8545"

web3 =Web3(Web3.HTTPProvider(ganache_url))

#Check if node is connected
print('Testing script is connected:', web3.isConnected())

web3.eth.defaultAccount = web3.eth.accounts[1]

#perform steps to access the smart contract
address = web3.toChecksumAddress('0xa0Dc61164631b017a1Ed74e41e34A624B554A3c7')

#how to import abi and bytecode using truffle 
PATH_TRUFFLE_WK = 'C:/Users/Inessa/Desktop/4th_Year/FYP/Methodology_Eth/energy'
truffleFile = json.load(open(PATH_TRUFFLE_WK + '/build/contracts/Energy.json'))
abi = truffleFile['abi']
bytecode = truffleFile['bytecode']

#fetch the smart contract
contract = web3.eth.contract(address=address, abi =abi)

#1) run admin initialisation scripts - deregister peers, start trading period etc.
p = subprocess.Popen(r'..\..\cd\Scripts\activate.bat && python test0.py')
p.wait()

#2) then, each peer registers, runs initial optimisation script, adds local residuals and then submit trade bids for the first time this time period

#subprocess.Popen(r'..\..\cd\Scripts\activate.bat &&python test1.py', creationflags=subprocess.CREATE_NEW_CONSOLE)
p1 = subprocess.Popen(r'..\..\cd\Scripts\activate.bat &&python test1.py')
p2 = subprocess.Popen(r'..\..\cd\Scripts\activate.bat &&python test2.py', creationflags=subprocess.CREATE_NEW_CONSOLE)
p3 = subprocess.Popen(r'..\..\cd\Scripts\activate.bat &&python test3.py', creationflags=subprocess.CREATE_NEW_CONSOLE)
p4 = subprocess.Popen(r'..\..\cd\Scripts\activate.bat &&python test4.py', creationflags=subprocess.CREATE_NEW_CONSOLE)
p5 = subprocess.Popen(r'..\..\cd\Scripts\activate.bat &&python test5.py', creationflags=subprocess.CREATE_NEW_CONSOLE)


p1.wait()
p2.wait()
p3.wait()
p4.wait()
p5.wait()

Times = pd.DataFrame(columns = ['Agent#', 'Iteration', 'Time (s)'])

optimal = contract.functions.is_optimal().call()

print(optimal)
Max_Iter = 500
iteration = 0
#3) main testing script checks if trades are optimal
while ((optimal == 0) and (iteration<Max_Iter)):
     data_path = Path(r'Results\Step2Times.csv')
     data_file = pd.read_csv(data_path)
     data_file = pd.DataFrame(data_file)
     ind_row = data_file.shape[0]
     
     iteration = contract.functions.iteration().call()
     print('Iteration:', iteration)
     data_file.loc[ind_row, 'Iteration'] = iteration
     data_file.loc[ind_row, 'Step'] = 2
     data_file.loc[ind_row, 'Agent'] = 1
    #a) each peer needs retrieve trade bids to run local optimisation, calculate and broadcast local residuals (save outputted trades)- one script each (run one at a time)
     start_time = TIME.time()
     p1 = subprocess.Popen(r'..\..\cd\Scripts\activate.bat &&python test1_step2.py')
     p1.wait()
     final_time = TIME.time()
     t1 = final_time - start_time - 2
     data_file.loc[ind_row, 'Time'] = t1
     ind_row = ind_row + 1
     print('Time for agent1 to complete step2', final_time - start_time)
     start_time = TIME.time()
     p2 = subprocess.Popen(r'..\..\cd\Scripts\activate.bat &&python test2_step2.py', creationflags=subprocess.CREATE_NEW_CONSOLE)
     p2.wait()
     final_time = TIME.time()
     t2 = final_time - start_time - 2
     data_file.loc[ind_row, 'Iteration'] = iteration
     data_file.loc[ind_row, 'Step'] = 2
     data_file.loc[ind_row, 'Agent'] = 2
     data_file.loc[ind_row, 'Time'] = t2
     ind_row = ind_row + 1
     print('Time for agent2 to complete step2', final_time - start_time)
     start_time = TIME.time()
     p3 = subprocess.Popen(r'..\..\cd\Scripts\activate.bat &&python test3_step2.py', creationflags=subprocess.CREATE_NEW_CONSOLE)
     p3.wait()
     final_time = TIME.time()
     t3 = final_time - start_time - 2
     data_file.loc[ind_row, 'Iteration'] = iteration
     data_file.loc[ind_row, 'Step'] = 2
     data_file.loc[ind_row, 'Agent'] = 3
     data_file.loc[ind_row, 'Time'] = t3
     ind_row = ind_row + 1
#     ind_row = Times.shape[0]
#     Times[ind_row, 'Agent#'] = 3
#     Times[ind_row, 'Iteration'] = iteration
#     Times[ind_row, 'Time (s)'] = t3
     print('Time for agent3 to complete step2', final_time - start_time)
     start_time = TIME.time()
     p4 = subprocess.Popen(r'..\..\cd\Scripts\activate.bat &&python test4_step2.py', creationflags=subprocess.CREATE_NEW_CONSOLE)
     p4.wait()
     final_time = TIME.time()
     t4 = final_time - start_time - 2
     data_file.loc[ind_row, 'Iteration'] = iteration
     data_file.loc[ind_row, 'Step'] = 2
     data_file.loc[ind_row, 'Agent'] = 4
     data_file.loc[ind_row, 'Time'] = t4
     ind_row = ind_row + 1
     print('Time for agent4 to complete step2', final_time - start_time)

     start_time = TIME.time()
     p5 = subprocess.Popen(r'..\..\cd\Scripts\activate.bat &&python test5_step2.py', creationflags=subprocess.CREATE_NEW_CONSOLE)
     p5.wait()
     final_time = TIME.time()
     t5 = final_time - start_time - 2
     data_file.loc[ind_row, 'Iteration'] = iteration
     data_file.loc[ind_row, 'Step'] = 2
     data_file.loc[ind_row, 'Agent'] = 5
     data_file.loc[ind_row, 'Time'] = t5
     ind_row = ind_row + 1
     print('Time for agent5 to complete step2', final_time - start_time)
     data_file.to_csv(r'C:\Users\Inessa\Desktop\4th_Year\FYP\Methodology_Eth\combination\testing_parallel4\Results\Step2Times.csv') 
     print('Global dres', contract.functions.global_dres().call())
     print('Global pres', contract.functions.global_pres().call())
     data_path = Path(r'Results\Residuals.csv')
     data_file = pd.read_csv(data_path)
     res = pd.DataFrame(data_file)
     row = res.shape[0]
     res.loc[row, 'Iteration'] = iteration
     res.loc[row, 'Global pres'] = contract.functions.global_pres().call()
     res.loc[row, 'Global dres'] = contract.functions.global_dres().call()
     res.to_csv(r'C:\Users\Inessa\Desktop\4th_Year\FYP\Methodology_Eth\combination\testing_parallel4\Results\Residuals.csv')
     #check if optimal
     optimal = contract.functions.is_optimal().call()
     print('Is optimal?', optimal)

#if not optimal- need to submit trade bids
#one script for each agent - read in trades from .csv and submit the trade bids.  Thereafter, while loop will repeat.
     if (optimal == 0):
        data_path = Path(r'Results\Step3Times.csv')
        data_file = pd.read_csv(data_path)
        data_file = pd.DataFrame(data_file)
        ind_row = data_file.shape[0]
        start_time = TIME.time()
        p1 = subprocess.Popen(r'..\..\cd\Scripts\activate.bat &&python test1_step3.py')
        p1.wait()
        final_time = TIME.time()
        t1 = final_time - start_time - 2
        data_file.loc[ind_row, 'Iteration'] = iteration
        data_file.loc[ind_row, 'Step'] = 3
        data_file.loc[ind_row, 'Agent'] = 1
        data_file.loc[ind_row, 'Time'] = t1
        ind_row = ind_row + 1
        print('Time for agent1 to complete step3', final_time - start_time)
        start_time = TIME.time()
        p2 = subprocess.Popen(r'..\..\cd\Scripts\activate.bat &&python test2_step3.py', creationflags=subprocess.CREATE_NEW_CONSOLE)
        p2.wait()
        final_time = TIME.time()
        t2 = final_time - start_time - 2
        data_file.loc[ind_row, 'Iteration'] = iteration
        data_file.loc[ind_row, 'Step'] = 3
        data_file.loc[ind_row, 'Agent'] = 2
        data_file.loc[ind_row, 'Time'] = t2
        ind_row = ind_row + 1
        print('Time for agent2 to complete step3', final_time - start_time)
        start_time = TIME.time()
        p3 = subprocess.Popen(r'..\..\cd\Scripts\activate.bat &&python test3_step3.py', creationflags=subprocess.CREATE_NEW_CONSOLE)
        p3.wait()
        final_time = TIME.time()
        t3 = final_time - start_time - 2
        data_file.loc[ind_row, 'Iteration'] = iteration
        data_file.loc[ind_row, 'Step'] = 3
        data_file.loc[ind_row, 'Agent'] = 3
        data_file.loc[ind_row, 'Time'] = t3
        ind_row = ind_row + 1
        print('Time for agent3 to complete step3', final_time - start_time)
        start_time = TIME.time()
        p4 = subprocess.Popen(r'..\..\cd\Scripts\activate.bat &&python test4_step3.py', creationflags=subprocess.CREATE_NEW_CONSOLE)
        p4.wait()
        final_time = TIME.time()
        t4 = final_time - start_time
        data_file.loc[ind_row, 'Iteration'] = iteration
        data_file.loc[ind_row, 'Step'] = 3
        data_file.loc[ind_row, 'Agent'] = 4
        data_file.loc[ind_row, 'Time'] = t4
        ind_row = ind_row + 1
        print('Time for agent4 to complete step3', final_time - start_time)
        start_time = TIME.time()
        #p5 = subprocess.Popen(r'..\..\cd\Scripts\activate.bat &&python test5_step3.py', creationflags=subprocess.CREATE_NEW_CONSOLE)
        p5 = subprocess.Popen(r'..\..\cd\Scripts\activate.bat &&python test5_step3.py', creationflags=subprocess.CREATE_NEW_CONSOLE)
        p5.wait()
        final_time = TIME.time()
        t5 = final_time - start_time
        data_file.loc[ind_row, 'Iteration'] = iteration
        data_file.loc[ind_row, 'Step'] = 3
        data_file.loc[ind_row, 'Agent'] = 5
        data_file.loc[ind_row, 'Time'] = t5
        ind_row = ind_row + 1
        print('Time for agent5 to complete step3', final_time - start_time)
        data_file.to_csv(r'C:\Users\Inessa\Desktop\4th_Year\FYP\Methodology_Eth\combination\testing_parallel4\Results\Step3Times.csv') 

    
     # c)if is optimal- then each peer needs to create trades from trade bids - one script each
     # d)each peer then needs to approve these trades - one script each

print('Done')
OptimalTrades = pd.DataFrame(columns = ['ID', 'Quantity (kWh)', 'Price (c/kWh)'])
ind_row = OptimalTrades.shape[0]
OptimalTrades.loc[ind_row, 'ID'] = 12
trade_temp = contract.functions.trade_bids_mapping(12).call()
OptimalTrades.loc[ind_row, 'Quantity (kWh)'] = trade_temp[2]/10000
OptimalTrades.loc[ind_row, 'Price (c/kWh)'] = trade_temp[3]/10000 * 100


ind_row = OptimalTrades.shape[0]
OptimalTrades.loc[ind_row, 'ID'] = 13
trade_temp = contract.functions.trade_bids_mapping(13).call()
OptimalTrades.loc[ind_row, 'Quantity (kWh)'] = trade_temp[2]/10000
OptimalTrades.loc[ind_row, 'Price (c/kWh)'] = trade_temp[3]/10000 * 100

ind_row = OptimalTrades.shape[0]
OptimalTrades.loc[ind_row, 'ID'] = 14
trade_temp = contract.functions.trade_bids_mapping(14).call()
OptimalTrades.loc[ind_row, 'Quantity (kWh)'] = trade_temp[2]/10000
OptimalTrades.loc[ind_row, 'Price (c/kWh)'] = trade_temp[3]/10000 * 100

ind_row = OptimalTrades.shape[0]
OptimalTrades.loc[ind_row, 'ID'] = 15
trade_temp = contract.functions.trade_bids_mapping(15).call()
OptimalTrades.loc[ind_row, 'Quantity (kWh)'] = trade_temp[2]/10000
OptimalTrades.loc[ind_row, 'Price (c/kWh)'] = trade_temp[3]/10000 * 100

ind_row = OptimalTrades.shape[0]
OptimalTrades.loc[ind_row, 'ID'] = 21
trade_temp = contract.functions.trade_bids_mapping(21).call()
OptimalTrades.loc[ind_row, 'Quantity (kWh)'] = trade_temp[2]/10000
OptimalTrades.loc[ind_row, 'Price (c/kWh)'] = trade_temp[3]/10000 * 100

ind_row = OptimalTrades.shape[0]
OptimalTrades.loc[ind_row, 'ID'] = 23
trade_temp = contract.functions.trade_bids_mapping(23).call()
OptimalTrades.loc[ind_row, 'Quantity (kWh)'] = trade_temp[2]/10000
OptimalTrades.loc[ind_row, 'Price (c/kWh)'] = trade_temp[3]/10000 * 100

ind_row = OptimalTrades.shape[0]
OptimalTrades.loc[ind_row, 'ID'] = 24
trade_temp = contract.functions.trade_bids_mapping(24).call()
OptimalTrades.loc[ind_row, 'Quantity (kWh)'] = trade_temp[2]/10000
OptimalTrades.loc[ind_row, 'Price (c/kWh)'] = trade_temp[3]/10000 * 100

ind_row = OptimalTrades.shape[0]
OptimalTrades.loc[ind_row, 'ID'] = 25
trade_temp = contract.functions.trade_bids_mapping(25).call()
OptimalTrades.loc[ind_row, 'Quantity (kWh)'] = trade_temp[2]/10000
OptimalTrades.loc[ind_row, 'Price (c/kWh)'] = trade_temp[3]/10000 * 100

ind_row = OptimalTrades.shape[0]
OptimalTrades.loc[ind_row, 'ID'] = 31
trade_temp = contract.functions.trade_bids_mapping(31).call()
OptimalTrades.loc[ind_row, 'Quantity (kWh)'] = trade_temp[2]/10000
OptimalTrades.loc[ind_row, 'Price (c/kWh)'] = trade_temp[3]/10000 * 100

ind_row = OptimalTrades.shape[0]
OptimalTrades.loc[ind_row, 'ID'] = 32
trade_temp = contract.functions.trade_bids_mapping(32).call()
OptimalTrades.loc[ind_row, 'Quantity (kWh)'] = trade_temp[2]/10000
OptimalTrades.loc[ind_row, 'Price (c/kWh)'] = trade_temp[3]/10000 * 100

ind_row = OptimalTrades.shape[0]
OptimalTrades.loc[ind_row, 'ID'] = 34
trade_temp = contract.functions.trade_bids_mapping(34).call()
OptimalTrades.loc[ind_row, 'Quantity (kWh)'] = trade_temp[2]/10000
OptimalTrades.loc[ind_row, 'Price (c/kWh)'] = trade_temp[3]/10000 * 100

ind_row = OptimalTrades.shape[0]
OptimalTrades.loc[ind_row, 'ID'] = 35
trade_temp = contract.functions.trade_bids_mapping(35).call()
OptimalTrades.loc[ind_row, 'Quantity (kWh)'] = trade_temp[2]/10000
OptimalTrades.loc[ind_row, 'Price (c/kWh)'] = trade_temp[3]/10000 * 100

ind_row = OptimalTrades.shape[0]
OptimalTrades.loc[ind_row, 'ID'] = 41
trade_temp = contract.functions.trade_bids_mapping(41).call()
OptimalTrades.loc[ind_row, 'Quantity (kWh)'] = trade_temp[2]/10000
OptimalTrades.loc[ind_row, 'Price (c/kWh)'] = trade_temp[3]/10000 * 100

ind_row = OptimalTrades.shape[0]
OptimalTrades.loc[ind_row, 'ID'] = 42
trade_temp = contract.functions.trade_bids_mapping(42).call()
OptimalTrades.loc[ind_row, 'Quantity (kWh)'] = trade_temp[2]/10000
OptimalTrades.loc[ind_row, 'Price (c/kWh)'] = trade_temp[3]/10000 * 100

ind_row = OptimalTrades.shape[0]
OptimalTrades.loc[ind_row, 'ID'] = 43
trade_temp = contract.functions.trade_bids_mapping(43).call()
OptimalTrades.loc[ind_row, 'Quantity (kWh)'] = trade_temp[2]/10000
OptimalTrades.loc[ind_row, 'Price (c/kWh)'] = trade_temp[3]/10000 * 100

ind_row = OptimalTrades.shape[0]
OptimalTrades.loc[ind_row, 'ID'] = 45
trade_temp = contract.functions.trade_bids_mapping(45).call()
OptimalTrades.loc[ind_row, 'Quantity (kWh)'] = trade_temp[2]/10000
OptimalTrades.loc[ind_row, 'Price (c/kWh)'] = trade_temp[3]/10000 * 100

ind_row = OptimalTrades.shape[0]
OptimalTrades.loc[ind_row, 'ID'] = 51
trade_temp = contract.functions.trade_bids_mapping(51).call()
OptimalTrades.loc[ind_row, 'Quantity (kWh)'] = trade_temp[2]/10000
OptimalTrades.loc[ind_row, 'Price (c/kWh)'] = trade_temp[3]/10000 * 100

ind_row = OptimalTrades.shape[0]
OptimalTrades.loc[ind_row, 'ID'] = 52
trade_temp = contract.functions.trade_bids_mapping(52).call()
OptimalTrades.loc[ind_row, 'Quantity (kWh)'] = trade_temp[2]/10000
OptimalTrades.loc[ind_row, 'Price (c/kWh)'] = trade_temp[3]/10000 * 100

ind_row = OptimalTrades.shape[0]
OptimalTrades.loc[ind_row, 'ID'] = 53
trade_temp = contract.functions.trade_bids_mapping(53).call()
OptimalTrades.loc[ind_row, 'Quantity (kWh)'] = trade_temp[2]/10000
OptimalTrades.loc[ind_row, 'Price (c/kWh)'] = trade_temp[3]/10000 * 100

ind_row = OptimalTrades.shape[0]
OptimalTrades.loc[ind_row, 'ID'] = 54
trade_temp = contract.functions.trade_bids_mapping(54).call()
OptimalTrades.loc[ind_row, 'Quantity (kWh)'] = trade_temp[2]/10000
OptimalTrades.loc[ind_row, 'Price (c/kWh)'] = trade_temp[3]/10000 * 100

OptimalTrades.to_csv(r'C:\Users\Inessa\Desktop\4th_Year\FYP\Methodology_Eth\combination\testing_parallel4\Results\Optimal Trades Blockchain.csv') 
