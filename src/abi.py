import sys
import traceback

from base import get_abi
from btc_cacheserver.util.procedure_logging import Procedure

try:
    procedure = Procedure("contract_abi")
    procedure.start(sys.argv)
    
    contract_name = sys.argv[1]
    
    
    
    abi = get_abi(contract_name)
    procedure.end("%s attr: %s", contract_name, [item.get("name") for item in abi])

except Exception as e:
    traceback.print_exc()
    print("usage: python3 abi.py {contract_name}")
