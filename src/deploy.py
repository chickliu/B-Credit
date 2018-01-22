import os, sys
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "btc_cacheserver.settings")
import json
import time

from web3 import Web3, RPCProvider
from solc import compile_files

from btc_cacheserver import settings

contract_name = sys.argv[1]
try:
    contract_dir = sys.argv[2]
except IndexError as e:
    contract_dir = os.path.dirname(__file__)

base_sols = sys.argv[3].split(";")
contract_sol_file = os.path.join(contract_dir, "%s.sol" % contract_name)
files = base_sols + [contract_sol_file, ]
print(files)
contract_compile_file = os.path.join(contract_dir, "%s.json" % contract_name)
contract_abi_file = os.path.join(contract_dir, "%s-abi.json" % contract_name)
print(contract_sol_file, contract_compile_file, contract_abi_file)

def get_compile():
    if not os.path.exists(contract_compile_file):
        compiled_sol = compile_files(files)["{c_file}:{name}".format(c_file=contract_sol_file, name=contract_name)]
        with open(contract_compile_file, "w+") as fo:
            fo.write(json.dumps(compiled_sol))
    
    else:
        with open(contract_compile_file, "r") as fo:
            compiled_sol = json.loads(fo.read())
    
    return compiled_sol

def get_abi():

    if not os.path.exists(contract_abi_file):
        
        compiled_sol = get_compile()
    
        abi = compiled_sol["abi"]
        with open(contract_abi_file, "w+") as fo:
            fo.write(json.dumps(abi, indent=2))
    
    else:
        with open(contract_abi_file, "r") as fo:
            abi = json.loads(fo.read())

    return abi


contract_interface = get_compile()

# web3.py instance
provider = RPCProvider(host=settings.BLOCKCHAIN_RPC_HOST, port=settings.BLOCKCHAIN_RPC_PORT)
w3 = Web3(provider)
w3.personal.unlockAccount(settings.BLOCKCHAIN_ACCOUNT, settings.BLOCKCHAIN_PASSWORD, 1000)
# Instantiate and deploy contract
contract = w3.eth.contract(abi=get_abi(), bytecode=contract_interface['bin'],code_runtime=contract_interface['bin-runtime'])

# Get transaction hash from deployed contract
print(sys.argv[4:])
tx_hash = contract.deploy(transaction={'from': settings.BLOCKCHAIN_ACCOUNT, 'gas': settings.BLOCKCHAIN_CALL_GAS_LIMIT}, args=sys.argv[4:])

# Get tx receipt to get contract address
tx_receipt = None
while tx_receipt is None:
    tx_receipt = w3.eth.getTransactionReceipt(tx_hash)
    time.sleep(2)
print("deploy transaction:", tx_receipt)
contract_address = tx_receipt['contractAddress']
print(contract_name, "address:", contract_address)
