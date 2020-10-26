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

p = subprocess.Popen(r'..\..\cd\Scripts\activate.bat && python test0.py')
p.wait()
#subprocess.Popen(r'..\..\cd\Scripts\activate.bat &&python test1.py', creationflags=subprocess.CREATE_NEW_CONSOLE)
subprocess.Popen(r'..\..\cd\Scripts\activate.bat &&python test1.py')
subprocess.Popen(r'..\..\cd\Scripts\activate.bat &&python test2.py')
subprocess.Popen(r'..\..\cd\Scripts\activate.bat &&python test3.py')
subprocess.Popen(r'..\..\cd\Scripts\activate.bat &&python test4.py')