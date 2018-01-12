# -*- coding: utf-8 -*-
import os
import json

from solc import compile_source

if not os.path.exists("./test.json"):
    with open("./test.sol", "r") as fo:
        content = fo.read()
    
    compiled_sol = compile_source(content)
    with open("./test.json", "w+") as fo:
        fo.write(json.dumps(compiled_sol))
else:
    with open("./test.json", "r") as fo:
        compiled_sol = json.loads(fo.read())

contract_abi = compiled_sol['<stdin>:UserMapsContract']["abi"]
print([item.get("name") for item in contract_abi])
with open("./test-map-contract-abi.json", "w+") as fo:
    fo.write(json.dumps(contract_abi, indent=2))


contract_abi = compiled_sol['<stdin>:UserContract']["abi"]
print([item.get("name") for item in contract_abi])
with open("./test-user-contract-abi.json", "w+") as fo:
    fo.write(json.dumps(contract_abi, indent=2))

