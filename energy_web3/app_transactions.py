#Tutorial about sending transactions on Ethereum
#whenever you call a smart contract function - you send a transaction

import json
from web3 import Web3

#using ganache url- we are connecting to the local blockchain running on our machine
ganache_url = "http://127.0.0.1:7545"

web3 =Web3(Web3.HTTPProvider(ganache_url))

#Check if node is connected
#print(web3.isConnected())

#let's send some cryptocurrency from account1 to account2

account_1="0x9F790d7D6F3F5079A9354348D1a53c55043FFB42" #like username

account_2= "0xBA99B7E944efc55c66e81B0bB359827F123E906b"

private_key1= "960bd6e6a5bba51c316ef5f2cb26c5e14fa69d2ad823e23caa4f41ec6cf42810" #like password- use it to sign transactions to authorise

#get the nonce
nonce = web3.eth.getTransactionCount(account_1)
#build transaction
tx = {
    'nonce': nonce,
    'to':account_2,
    'value': web3.toWei(1, 'ether'),
    'gas': 2000000,
    'gasPrice': web3.toWei('50', 'gwei')#gas is an amount of cryptocurrency you have to pay for a transaction - need to do this because of PoW.  Gas limit is the amount we are willing to pay. 
        #gas is not ether- would multiply the amount of gas a transaction costs by the price of gas at that time

}

#sign transaction
signed_tx = web3.eth.account.signTransaction(tx, private_key1)

#send transaction
tx_hash= web3.eth.sendRawTransaction(signed_tx.rawTransaction)

#get transaction hash
print(web3.toHex(tx_hash))
