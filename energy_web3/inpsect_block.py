#tutorial for inspecting blocks that have been stored in the blockchain
#blocks are made of multiple transactions
# block time is the amount of time it takes for transactions to be included in a block
#throughput= transactions/second

import json
from web3 import Web3

infura_url= 'https://mainnet.infura.io/v3/e2d71d4dbfee489c86afa0c7c09beca7'

web3 =Web3(Web3.HTTPProvider(infura_url))

#Check if node is connected
print(web3.isConnected())


latest = web3.eth.blockNumber
#rint(latest)

#returns data stored in the latest block
#print(web3.eth.getBlock(latest))

#latest block's hash value gotten from EtherScan
hash  = '0xb15000bc87060b46956f644f61bfd80d31a30d7f7a10dd9dbbf78643c694ab45'
#want to view the second transaction stored in the latest block
print(web3.eth.getTransactionByBlock(hash, 2))

