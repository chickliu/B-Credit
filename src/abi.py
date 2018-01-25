import sys
import traceback

from base import get_abi
from btc_cacheserver import defines

def recursive_attr(set_container, _class):
    set_container.update(_class.__dict__.values())
    print(_class.__bases__)
    for _base_class in _class.__bases__:
        recursive_attr(set_container, _base_class)

try:
    contract_name = sys.argv[1]
    try:
        base_class_name = sys.argv[2]
        _class = getattr(defines, base_class_name, {})
        base_methods = set()
        recursive_attr(base_methods, _class)
        '''
        base_methods = set(_class.__dict__.values())

        print(_class.__bases__)
        for _base_class in _class.__bases__:
            base_methods.update(item for item in _base_class.__dict__.values())
        '''
    except IndexError:
        traceback.print_exc()
        base_methods = []
    
    print(base_methods)
    abi = get_abi(contract_name)
    print("%s attr:\n" %  contract_name)
    print("\n".join(sorted(item.get("name", "") for item in abi if item.get("name", "") not in base_methods)))

except Exception as e:
    traceback.print_exc()
    print("usage: python3 abi.py {contract_name} [{defines_base_class}]")
