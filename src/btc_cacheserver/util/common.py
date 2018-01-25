# !/usr/bin/env python
# -*- coding: utf-8 -*-

"""
created by antimoth at 2018-01-23
"""

import os
import json
import time

from web3 import Web3, RPCProvider
from solc import compile_files

from django.conf import settings
from btc_cacheserver.defines import RouteMethods, ContractNames

contract_instances = {}


def get_sol_path(contract_name):
    return os.path.join(settings.CONTRACT_DIR, "%s.sol" % contract_name)


def get_compile_path(contract_name):
    return os.path.join(settings.CONTRACT_DIR, "%s.json" % contract_name)


def get_abi_path(contract_name):
    return os.path.join(settings.CONTRACT_DIR, "%s-abi.json" % contract_name)


BASE_SOL_ROLES = get_sol_path(ContractNames.ROLES)
BASE_SOL_RBAC = get_sol_path(ContractNames.RBAC)
BASE_SOL_PAUSABLE = get_sol_path(ContractNames.PAUSABLE)

CONTRACT_BASE_SOLS = {
    ContractNames.CONTROLLER_ROUTE: [
        BASE_SOL_ROLES, BASE_SOL_RBAC, BASE_SOL_PAUSABLE,
    ],
    ContractNames.INTERFACE: [
        BASE_SOL_ROLES, BASE_SOL_RBAC, BASE_SOL_PAUSABLE,
        get_sol_path(ContractNames.CONTROLLER_ROUTE),
        get_sol_path(ContractNames.LOAN_CONTROLLER),
    ],
    ContractNames.LOAN_CONTRACT_ROUTE: [
        BASE_SOL_ROLES, BASE_SOL_RBAC, BASE_SOL_PAUSABLE,
    ],
    ContractNames.LOAN_CONTROLLER: [
        BASE_SOL_ROLES, BASE_SOL_RBAC, BASE_SOL_PAUSABLE,
        get_sol_path(ContractNames.LOAN_CONTRACT_ROUTE),
        get_sol_path(ContractNames.USER_LOAN),
    ],
    ContractNames.USER_LOAN_STORE_ROUTE: [
        BASE_SOL_ROLES, BASE_SOL_RBAC, BASE_SOL_PAUSABLE,
    ],
    ContractNames.USER_LOAN: [
        BASE_SOL_ROLES, BASE_SOL_RBAC, BASE_SOL_PAUSABLE,
        get_sol_path(ContractNames.USER_LOAN_STORE_ROUTE),
        get_sol_path(ContractNames.USER_LOAN_STORE),
    ],
    ContractNames.USER_LOAN_STORE: [
        BASE_SOL_ROLES, BASE_SOL_RBAC, BASE_SOL_PAUSABLE,
    ],
}


def get_base_sols(contract_name):
    return CONTRACT_BASE_SOLS.get(contract_name, [])


def get_compile(contract_name):
    contract_sol_file = get_sol_path(contract_name)
    files = get_base_sols(contract_name) + [contract_sol_file, ]
    contract_compile_file = get_compile_path(contract_name)
    if not os.path.exists(contract_compile_file):
        compiled_sol = compile_files(files)[
            "{c_file}:{name}".format(c_file=contract_sol_file,
                                     name=contract_name)]
        with open(contract_compile_file, "w+") as fo:
            fo.write(json.dumps(compiled_sol))

    else:
        with open(contract_compile_file, "r") as fo:
            compiled_sol = json.loads(fo.read())

    return compiled_sol


def get_abi(contract_name):
    contract_abi_file = get_abi_path(contract_name)
    if not os.path.exists(contract_abi_file):

        compiled_sol = get_compile(contract_name)

        abi = compiled_sol["abi"]
        with open(contract_abi_file, "w+") as fo:
            fo.write(json.dumps(abi, indent=2))

    else:
        with open(contract_abi_file, "r") as fo:
            abi = json.loads(fo.read())

    return abi


def create_web3_instance(time_out=1000):
    provider = RPCProvider(host=settings.BLOCKCHAIN_RPC_HOST,
                           port=settings.BLOCKCHAIN_RPC_PORT)
    _ins = Web3(provider)
    _ins.eth.defaultAccount = settings.BLOCKCHAIN_ACCOUNT
    _ins.personal.unlockAccount(settings.BLOCKCHAIN_ACCOUNT,
                                settings.BLOCKCHAIN_PASSWORD, time_out)
    return _ins


w3 = create_web3_instance()

transact_kwargs = {"from": settings.BLOCKCHAIN_ACCOUNT,
                   "gas": settings.BLOCKCHAIN_CALL_GAS_LIMIT, }


def get_contract_instance(contract_address, abi_file_path=None,
                          account_time_out=10000):
    if contract_address in contract_instances:
        _ins = contract_instances[contract_address]

    else:
        if not os.path.exists(abi_file_path):
            raise Exception("abi file not found!")

        with open(abi_file_path, "r") as fo:
            abi_json = json.loads(fo.read())

        # _ins = w3.eth.contract(abi_json, contract_address, ContractFactoryClass=ConciseContract)
        _ins = w3.eth.contract(abi_json, contract_address)
        contract_instances[contract_address] = _ins

    w3.personal.unlockAccount(settings.BLOCKCHAIN_ACCOUNT,
                              settings.BLOCKCHAIN_PASSWORD, account_time_out)

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


def transaction_exec_v2(_ins, method, *args, **kwargs):
    tx_ins = _ins.transact(transact_kwargs)
    return transaction_exec(tx_ins, method, *args, **kwargs)


def transaction_exec_result(_ins, method, *args, **kwargs):
    tx_ins = _ins.call(transact_kwargs)
    method_call = getattr(tx_ins, method)
    return method_call(*args, **kwargs)


def pure_get_exec(_ins, method, *args, **kwargs):
    method_call = getattr(_ins, method)
    return method_call(*args, **kwargs)


def role_added_from_contract_ins(role_dest_address, dest_contract,
                                 role=RouteMethods.ROLE_WRITER):
    return transaction_exec_v2(dest_contract, RouteMethods.ADMIN_ADD_ROLE,
                               role_dest_address, role)


def role_added(role_dest_address, dest_contract_name, dest_contract_address,
               role=RouteMethods.ROLE_WRITER):
    _contract = get_contract_instance(dest_contract_address,
                                      get_abi_path(dest_contract_name))
    return role_added_from_contract_ins(role_dest_address, _contract, role)


def role_removed_from_contract_ins(role_dest_address, dest_contract,
                                   role=RouteMethods.ROLE_WRITER):
    return transaction_exec_v2(dest_contract, RouteMethods.ADMIN_REMOVE_ROLE,
                               role_dest_address, role)


def role_removed(role_dest_address, dest_contract_name, dest_contract_address,
                 role=RouteMethods.ROLE_WRITER):
    _contract = get_contract_instance(dest_contract_address,
                                      get_abi_path(dest_contract_name))
    return role_removed_from_contract_ins(role_dest_address, _contract, role)

