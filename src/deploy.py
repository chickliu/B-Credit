import sys
import traceback

from base import deploy


if __name__ == "__main__":

    try:
        _name = sys.argv[1]
        
        _args = sys.argv[2:]
        
        deploy(_name, _args)
    except Exception as e:
        traceback.print_exc()
        print("usage: python3 deploy.py {contract_name} [{contract_argument1} {contract_argument2} ...]")
