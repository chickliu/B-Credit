import os
import json
import time

from web3 import Web3, RPCProvider
from solc import compile_source

from btc_cacheserver import settings

if not os.path.exists("./test.json"):
    with open("./test.sol", "r") as fo:
        content = fo.read()
    
    compiled_sol = compile_source(content)
    with open("./test.json", "w+") as fo:
        fo.write(json.dumps(compiled_sol))
else:
    with open("./test.json", "r") as fo:
        compiled_sol = json.loads(fo.read())

contract_interface = compiled_sol['<stdin>:UserMapsContract']

# web3.py instance
provider = RPCProvider(host=settings.BLOCKCHAIN_RPC_HOST, port=settings.BLOCKCHAIN_RPC_PORT)
w3 = Web3(provider)
w3.personal.unlockAccount(settings.BLOCKCHAIN_ACCOUNT, settings.BLOCKCHAIN_PASSWORD, 1000)
# Instantiate and deploy contract
contract = w3.eth.contract(abi=contract_interface['abi'], bytecode=contract_interface['bin'],code_runtime=contract_interface['bin-runtime'])

# Get transaction hash from deployed contract
tx_hash = contract.deploy(transaction={'from': settings.BLOCKCHAIN_ACCOUNT, 'gas': settings.BLOCKCHAIN_CALL_GAS_LIMIT})

# Get tx receipt to get contract address
tx_receipt = None
while tx_receipt is None:
    tx_receipt = w3.eth.getTransactionReceipt(tx_hash)
    time.sleep(2)
print("deploy transaction:", tx_receipt)
contract_address = tx_receipt['contractAddress']
print("UserMapsContract address:", contract_address)
