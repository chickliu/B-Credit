import sys
import traceback
import copy

from base import get_compile, create_web3_instance, transact_kwargs, get_transaction_receipt
from btc_cacheserver.util.procedure_logging import Procedure


def deploy(contract_name, contract_arguments):
    arguments = copy.copy(locals())
    procedure = Procedure("<%s>" % contract_name)
    procedure.start(arguments)
    contract_interface = get_compile(contract_name)
    
    # web3.py instance
    w3 = create_web3_instance()
    # Instantiate and deploy contract
    contract = w3.eth.contract(abi=contract_interface["abi"], bytecode=contract_interface['bin'],code_runtime=contract_interface['bin-runtime'])
    
    # Get transaction hash from deployed contract
    procedure.info(contract_arguments)
    tx_hash = contract.deploy(transaction=transact_kwargs, args=contract_arguments)
    
    # Get tx receipt to get contract address
    tx_receipt = get_transaction_receipt(tx_hash)
    procedure.info("deploy transaction: %s " % tx_receipt.transactionHash)
    
    contract_address = tx_receipt['contractAddress']
    procedure.end("%s address: %s", contract_name, contract_address)
    return contract_address


if __name__ == "__main__":

    try:
        _name = sys.argv[1]
        
        _args = sys.argv[2:]
        
        deploy(_name, _args)
    except Exception as e:
        traceback.print_exc()
        print("usage: python3 deploy.py {contract_name} [{contract_argument1} {contract_argument2} ...]")
