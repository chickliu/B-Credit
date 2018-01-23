#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
created by antimoth at 2018-01-23
"""

import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "btc_cacheserver.settings")

import json
import time


from web3 import Web3, RPCProvider
from web3.contract import ConciseContract
from solc import compile_files

from btc_cacheserver import settings

contract_instances = {}

def get_compile(contract_name, contract_dir, base_sols):
    contract_sol_file = os.path.join(contract_dir, "%s.sol" % contract_name)
    files = base_sols + [contract_sol_file, ]
    contract_compile_file = os.path.join(contract_dir, "%s.json" % contract_name)
    if not os.path.exists(contract_compile_file):
        compiled_sol = compile_files(files)["{c_file}:{name}".format(c_file=contract_sol_file, name=contract_name)]
        with open(contract_compile_file, "w+") as fo:
            fo.write(json.dumps(compiled_sol))
    
    else:
        with open(contract_compile_file, "r") as fo:
            compiled_sol = json.loads(fo.read())
    
    return compiled_sol

def get_abi(contract_name, contract_dir, base_sols):
    contract_abi_file = os.path.join(contract_dir, "%s-abi.json" % contract_name)
    if not os.path.exists(contract_abi_file):
        
        compiled_sol = get_compile(contract_name, contract_dir, base_sols)
    
        abi = compiled_sol["abi"]
        with open(contract_abi_file, "w+") as fo:
            fo.write(json.dumps(abi, indent=2))
    
    else:
        with open(contract_abi_file, "r") as fo:
            abi = json.loads(fo.read())

    return abi

def create_web3_instance(time_out=1000):
    provider = RPCProvider(host=settings.BLOCKCHAIN_RPC_HOST, port=settings.BLOCKCHAIN_RPC_PORT)
    _ins = Web3(provider)
    _ins.eth.defaultAccount = settings.BLOCKCHAIN_ACCOUNT
    _ins.personal.unlockAccount(settings.BLOCKCHAIN_ACCOUNT, settings.BLOCKCHAIN_PASSWORD, time_out)
    return _ins 


w3 = create_web3_instance()

transact_kwargs = {"from": settings.BLOCKCHAIN_ACCOUNT, "gas": settings.BLOCKCHAIN_CALL_GAS_LIMIT, }

def get_contract_instance(contract_address, abi_file_path=None, account_time_out=10000):

    if contract_address in contract_instances:
        _ins = contract_instances[contract_address]

    else:
        if not os.path.exists(abi_file_path):
            raise Exception("abi file not found!")

        with open(abi_file_path, "r") as fo:
            abi_json = json.loads(fo.read())

        _ins = w3.eth.contract(abi_json, contract_address, ContractFactoryClass=ConciseContract)
        contract_instances[contract_address] = _ins

    w3.personal.unlockAccount(settings.BLOCKCHAIN_ACCOUNT, settings.BLOCKCHAIN_PASSWORD, account_time_out)
    
    return _ins

def get_transaction_receipt(tx_hash):
    tx_receipt = None
    _wait = 0
    while tx_receipt is None and _wait < settings.TRANSACTION_MAX_WAIT:
        tx_receipt = w3.eth.getTransactionReceipt(tx_hash)
        time.sleep(2)
        _wait += 1
    return tx_receipt   


def transaction_exec(_ins, method, *args, **kwargs):
    method_call = getattr(_ins, method)
    tx_hash = method_call(*args, **kwargs)
    return get_transaction_receipt(tx_hash)  


def pure_get_exec(_ins, method, *args, **kwargs):
    method_call = getattr(_ins, method)
    return method_call(*args, **kwargs)


