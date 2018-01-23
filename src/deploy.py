import sys
import traceback

from base import get_compile, create_web3_instance, transact_kwargs, get_transaction_receipt
from btc_cacheserver.util.procedure_logging import Procedure

try:
    procedure = Procedure("contract_deploy")
    procedure.start(sys.argv)
    
    contract_name = sys.argv[1]
    
    contract_dir = sys.argv[2]
    
    try:
        base_sols = sys.argv[3].split(";")
    except IndexError as e:
        base_sols = []
    
    contract_interface = get_compile(contract_name, contract_dir, base_sols)
    
    # web3.py instance
    w3 = create_web3_instance()
    # Instantiate and deploy contract
    contract = w3.eth.contract(abi=contract_interface["abi"], bytecode=contract_interface['bin'],code_runtime=contract_interface['bin-runtime'])
    
    # Get transaction hash from deployed contract
    contract_arguments = sys.argv[4:]
    procedure.info(contract_arguments)
    tx_hash = contract.deploy(transaction=transact_kwargs, args=contract_arguments)
    
    # Get tx receipt to get contract address
    tx_receipt = get_transaction_receipt(tx_hash)
    procedure.info("deploy transaction: %s " % tx_receipt)
    
    contract_address = tx_receipt['contractAddress']
    procedure.end("%s address: %s", contract_name, contract_address)
except Exception as e:
    traceback.print_exc()
    print("usage: python3 deploy.py {contract_name} {contract_dir} [{base_contract_sol_file1;base_contract_sol_file2;base_contract_sol_file3}] [{contract_argument1} {contract_argument2}]")
