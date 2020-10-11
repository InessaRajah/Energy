import json
from web3 import Web3

ganache_url = "http://127.0.0.1:7545"

web3 =Web3(Web3.HTTPProvider(ganache_url))

#Check if node is connected
print(web3.isConnected())

#write transactions to blockchain using smart contract- thes transactions are stored as blocks on the blockchain
# previous smart contract tutorial was just about reading data from the smart contract

#sets the first ganache account to default account- so can sign account without sharing the account's private key
web3.eth.defaultAccount = web3.eth.accounts[0]

#smart contract adress and abi
address = web3.toChecksumAddress('0x1aC5C77e22b7B53Be11d90F7f667418BA79F1dbC')
abi = json.loads('[{"constant":false,"inputs":[{"name":"_greeting","type":"string"}],"name":"setGreeting","outputs":[],"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":true,"inputs":[],"name":"greet","outputs":[{"name":"","type":"string"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":true,"inputs":[],"name":"greeting","outputs":[{"name":"","type":"string"}],"payable":false,"stateMutability":"view","type":"function"},{"inputs":[],"payable":false,"stateMutability":"nonpayable","type":"constructor"}]')

#fetch the smart contract
contract = web3.eth.contract(address=address, abi =abi)

#call() function - read data
greet = contract.functions.greet().call()

#print(greet)

#update the greeting- i.e. call setGreeting() function
#get transaction has back immediately
tx_hash = contract.functions.setGreeting("NEW GREETING").transact()

#want to get transaction receipt back to indicate that mining was successful and transaction has been logged on the blockchain
#this next line means wait until transaction receipt is received before continuing with code execution
web3.eth.waitForTransactionReceipt(tx_hash)

print('Updated greeting: {}'.format(
    contract.functions.greet().call()
))