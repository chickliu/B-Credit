import sys
import traceback

from base import get_abi
from btc_cacheserver.util.procedure_logging import Procedure

try:
    procedure = Procedure("contract_abi")
    procedure.start(sys.argv)
    
    contract_name = sys.argv[1]
    
    contract_dir = sys.argv[2]
    
    try:
        base_sols = sys.argv[3].split(";")
    except IndexError as e:
        base_sols = []
    
    abi = get_abi(contract_name, contract_dir, base_sols)
    procedure.end("%s attr: %s", contract_name, [item.get("name") for item in abi])

except Exception as e:
    traceback.print_exc()
    print("usage: python3 abi.py {contract_name} {contract_dir} [{base_contract_sol_file1;base_contract_sol_file2;base_contract_sol_file3}] [{contract_argument1} {contract_argument2}]")
