#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
created by antimoth at 2018-01-23
"""

import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "btc_cacheserver.settings")

import json
import time
import copy


from web3 import Web3, RPCProvider
from solc import compile_files

from btc_cacheserver import settings
from btc_cacheserver.defines import RouteMethods, ContractNames,InterfaceMethods
from btc_cacheserver.util.procedure_logging import Procedure
from btc_cacheserver.contract.models import User, TransactionInfo, ContractDeployInfo

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
        compiled_sol = compile_files(files)["{c_file}:{name}".format(c_file=contract_sol_file, name=contract_name)]
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

        # _ins = w3.eth.contract(abi_json, contract_address, ContractFactoryClass=ConciseContract)
        _ins = w3.eth.contract(abi_json, contract_address)
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
    tx_receipt = get_transaction_receipt(tx_hash)  

    _transaction = TransactionInfo(
        transactionHash=tx_receipt.transactionHash,
        method=method
    )   
    _transaction.save()

    return tx_receipt



def transaction_exec_v2(_ins, method, *args, **kwargs):
    tx_ins = _ins.transact(transact_kwargs)
    return transaction_exec(tx_ins, method, *args, **kwargs)


def transaction_exec_local_result(_ins, method, *args, **kwargs):
    tx_ins = _ins.call(transact_kwargs)
    method_call = getattr(tx_ins, method)
    return method_call(*args, **kwargs)


def pure_get_exec(_ins, method, *args, **kwargs):
    method_call = getattr(_ins, method)
    return method_call(*args, **kwargs)

def deploy(contract_name, contract_arguments):
    arguments = copy.copy(locals())
    procedure = Procedure("<%s>" % contract_name)
    procedure.start(arguments)
    contract_interface = get_compile(contract_name)
    
    # Instantiate and deploy contract
    contract = w3.eth.contract(abi=contract_interface["abi"], bytecode=contract_interface['bin'],code_runtime=contract_interface['bin-runtime'])
    
    # Get transaction hash from deployed contract
    tx_hash = contract.deploy(transaction=transact_kwargs, args=contract_arguments)
    
    # Get tx receipt to get contract address
    tx_receipt = get_transaction_receipt(tx_hash)
    procedure.info("deploy transaction: %s " % tx_receipt.transactionHash)
    
    contract_address = tx_receipt['contractAddress']
    procedure.end("%s address: %s", contract_name, contract_address)

    _record = ContractDeployInfo(
        address=contract_address,
        name=contract_name,
        tx=tx_receipt.transactionHash
    )
    _record.save()

    return contract_address

def role_added_from_contract_ins(role_dest_address, dest_contract, role=RouteMethods.ROLE_WRITER):
    return transaction_exec_v2(dest_contract, RouteMethods.ADMIN_ADD_ROLE,  role_dest_address, role)

def role_added(role_dest_address, dest_contract_name, dest_contract_address, role=RouteMethods.ROLE_WRITER):
    _contract = get_contract_instance(dest_contract_address, get_abi_path(dest_contract_name))
    return role_added_from_contract_ins(role_dest_address, _contract, role)

def role_removed_from_contract_ins(role_dest_address, dest_contract, role=RouteMethods.ROLE_WRITER):
    return transaction_exec_v2(dest_contract, RouteMethods.ADMIN_REMOVE_ROLE,  role_dest_address, role)

def role_removed(role_dest_address, dest_contract_name, dest_contract_address, role=RouteMethods.ROLE_WRITER):
    _contract = get_contract_instance(dest_contract_address, get_abi_path(dest_contract_name))
    return role_removed_from_contract_ins(role_dest_address, _contract, role)

def has_role(check_address, dest_contract_name, dest_contract_address, role=RouteMethods.ROLE_WRITER):
    _contract = get_contract_instance(dest_contract_address, get_abi_path(dest_contract_name))
    return role_removed_from_contract_ins(check_address, _contract, role)

def create_loan_store(user_tag_str, loan_contract_address):
    procedure = Procedure("<%s>" % user_tag_str)

    loan_store_route = get_contract_instance(settings.USER_LOAN_STORE_ROUTE_ADDRESS, get_abi_path(ContractNames.USER_LOAN_STORE_ROUTE))

    has_call_role = transaction_exec_local_result(loan_store_route, RouteMethods.HAS_ROLE, loan_contract_address, RouteMethods.ROLE_CALLER)
    if not has_call_role:
        role_added_from_contract_ins(loan_contract_address, loan_store_route, RouteMethods.ROLE_CALLER)

    loan_store_address = transaction_exec_local_result(loan_store_route, RouteMethods.GET_CURRENT_ADDRESS, loan_contract_address)
    procedure.info("loan_store_address is %s", loan_store_address)


    if not int(loan_store_address, 16):
        loan_store_address = deploy(
            ContractNames.USER_LOAN_STORE,
            [w3.toBytes(hexstr=user_tag_str), ]
        )

    _tx = transaction_exec_v2(loan_store_route, RouteMethods.SET_ADDRESS, loan_contract_address, loan_store_address, True)
    procedure.info(" %s(%s) %s %s(%s)  tx is %s", 
            ContractNames.USER_LOAN_STORE_ROUTE, 
            settings.USER_LOAN_STORE_ROUTE_ADDRESS, 
            RouteMethods.SET_ADDRESS, 
            ContractNames.USER_LOAN_STORE, 
            loan_store_address, 
            _tx.transactionHash
    )

    loan_store = get_contract_instance(loan_store_address, get_abi_path(ContractNames.USER_LOAN_STORE))

    has_write_role = transaction_exec_local_result(loan_store, RouteMethods.HAS_ROLE, loan_contract_address, RouteMethods.ROLE_WRITER)
    if not has_write_role:
        role_added_from_contract_ins(loan_contract_address, loan_store, RouteMethods.ROLE_WRITER)

    has_call_role = transaction_exec_local_result(loan_store, RouteMethods.HAS_ROLE, loan_contract_address, RouteMethods.ROLE_CALLER)
    if not has_call_role:
        role_added_from_contract_ins(loan_contract_address, loan_store, RouteMethods.ROLE_CALLER)

    return loan_store_address

def create_loan_contract(user_tag_str, controller_address):
    procedure = Procedure("<%s>" % user_tag_str)
    bytes_user_tag = w3.toBytes(hexstr=user_tag_str)

    loan_contract_route = get_contract_instance(settings.LOAN_CONTRACT_ROUTE_ADDRESS, get_abi_path(ContractNames.LOAN_CONTRACT_ROUTE))

    has_call_role = transaction_exec_local_result(loan_contract_route, RouteMethods.HAS_ROLE, controller_address, RouteMethods.ROLE_CALLER)
    if not has_call_role:
        role_added_from_contract_ins(controller_address, loan_contract_route, RouteMethods.ROLE_CALLER)

    loan_contract_address = transaction_exec_local_result(loan_contract_route, RouteMethods.GET_CURRENT_ADDRESS, bytes_user_tag)
    procedure.info("loan_contract_address is %s", loan_contract_address)

    if not int(loan_contract_address, 16):
        loan_contract_address = deploy(
            ContractNames.USER_LOAN,
            [bytes_user_tag, settings.USER_LOAN_STORE_ROUTE_ADDRESS, ],
        )

    _tx = transaction_exec_v2(loan_contract_route, RouteMethods.SET_ADDRESS, bytes_user_tag, loan_contract_address, True)
    procedure.info(" %s(%s) %s %s(%s)  tx is %s", 
            ContractNames.LOAN_CONTRACT_ROUTE, 
            settings.LOAN_CONTRACT_ROUTE_ADDRESS, 
            RouteMethods.SET_ADDRESS, 
            ContractNames.USER_LOAN, 
            loan_contract_address, 
            _tx.transactionHash
    )

    try:
        _user = User.objects.get(tag=user_tag_str)
    except User.DoesNotExist:
        _user = User(tag=user_tag_str)
        _user.save()

    create_loan_store(user_tag_str, loan_contract_address)
    

    loan_contract = get_contract_instance(loan_contract_address, get_abi_path(ContractNames.USER_LOAN))

    has_write_role = transaction_exec_local_result(loan_contract, RouteMethods.HAS_ROLE, controller_address, RouteMethods.ROLE_WRITER)
    if not has_write_role:
        role_added_from_contract_ins(controller_address, loan_contract, RouteMethods.ROLE_WRITER)

    has_call_role = transaction_exec_local_result(loan_contract, RouteMethods.HAS_ROLE, controller_address, RouteMethods.ROLE_CALLER)
    if not has_call_role:
        role_added_from_contract_ins(controller_address, loan_contract, RouteMethods.ROLE_CALLER)

    return loan_contract_address

def create_user_controller(controller_name):
    procedure = Procedure("<%s>" % controller_name)
    
    interface_address = settings.INTERFACE_ADDRESS
    controller_route = get_contract_instance(settings.CONTROLLER_ROUTE_ADDRESS, get_abi_path(ContractNames.CONTROLLER_ROUTE))

    has_call_role = transaction_exec_local_result(controller_route, RouteMethods.HAS_ROLE, interface_address, RouteMethods.ROLE_CALLER)
    if not has_call_role:
        role_added_from_contract_ins(interface_address, controller_route, RouteMethods.ROLE_CALLER)

    controller_address = transaction_exec_local_result(controller_route, RouteMethods.GET_CURRENT_ADDRESS, controller_name)
    procedure.info("controller_address is %s", controller_address)

    if not int(controller_address, 16):
        controller_address = deploy(
            ContractNames.LOAN_CONTROLLER,
            [settings.LOAN_CONTRACT_ROUTE_ADDRESS, ],
        )

    # set current loan controller address to route
    _tx = transaction_exec_v2(controller_route, RouteMethods.SET_ADDRESS, ContractNames.LOAN_CONTROLLER, controller_address, True)
    procedure.info(" %s(%s) %s %s(%s)  tx is %s", 
            ContractNames.CONTROLLER_ROUTE, 
            settings.CONTROLLER_ROUTE_ADDRESS, 
            RouteMethods.SET_ADDRESS, 
            ContractNames.LOAN_CONTROLLER, 
            controller_address, 
            _tx.transactionHash
    )

    # add authorization for interface
    controller = get_contract_instance(controller_address, get_abi_path(ContractNames.LOAN_CONTROLLER))

    has_write_role = transaction_exec_local_result(controller, RouteMethods.HAS_ROLE, interface_address, RouteMethods.ROLE_WRITER)
    if not has_write_role:
        role_added_from_contract_ins(interface_address, controller, RouteMethods.ROLE_WRITER)

    has_call_role = transaction_exec_local_result(controller, RouteMethods.HAS_ROLE, interface_address, RouteMethods.ROLE_CALLER)
    if not has_call_role:
        role_added_from_contract_ins(interface_address, controller, RouteMethods.ROLE_CALLER)

    return controller_address


def get_controller_address(controller_name):
    interface = get_contract_instance(settings.INTERFACE_ADDRESS, get_abi_path(ContractNames.INTERFACE))
    return transaction_exec_local_result(interface, InterfaceMethods.GET_CONTROLLER_ADDRESS, controller_name)

def get_loan_contract_address(controller_name, user_tag_str):
    interface = get_contract_instance(settings.INTERFACE_ADDRESS, get_abi_path(ContractNames.INTERFACE))
    return transaction_exec_local_result(interface, InterfaceMethods.GET_LOAN_CONTRACT_ADDRESS, controller_name, w3.toBytes(hexstr=user_tag_str))

def get_loan_store_address(controller_name, user_tag_str):
    interface = get_contract_instance(settings.INTERFACE_ADDRESS, get_abi_path(ContractNames.INTERFACE))
    return transaction_exec_local_result(interface, InterfaceMethods.GET_USER_LOAN_STORE_ADDRESS, controller_name, w3.toBytes(hexstr=user_tag_str))

def get_latest_update(controller_name, user_tag_str):
    interface = get_contract_instance(settings.INTERFACE_ADDRESS, get_abi_path(ContractNames.INTERFACE))
    return transaction_exec_local_result(interface, InterfaceMethods.GET_LATEST_UPDATE, controller_name, w3.toBytes(hexstr=user_tag_str))

def get_loan_times(controller_name, user_tag_str):
    interface = get_contract_instance(settings.INTERFACE_ADDRESS, get_abi_path(ContractNames.INTERFACE))
    return transaction_exec_local_result(interface, InterfaceMethods.GET_LOAN_TIMES, controller_name, w3.toBytes(hexstr=user_tag_str))

def get_loan(controller_name, user_tag_str, index):
    interface = get_contract_instance(settings.INTERFACE_ADDRESS, get_abi_path(ContractNames.INTERFACE))
    return transaction_exec_local_result(interface, InterfaceMethods.GET_LOAN_BY_INDEX, controller_name, w3.toBytes(hexstr=user_tag_str), index)

def get_expend(controller_name, user_tag_str, index, expend_index):
    interface = get_contract_instance(settings.INTERFACE_ADDRESS, get_abi_path(ContractNames.INTERFACE))
    return transaction_exec_local_result(interface, InterfaceMethods.GET_EXPEND_BY_INDEX, controller_name, w3.toBytes(hexstr=user_tag_str), index, expend_index)

def get_installment(controller_name, user_tag_str, index, expend_index, installment_index):
    interface = get_contract_instance(settings.INTERFACE_ADDRESS, get_abi_path(ContractNames.INTERFACE))
    return transaction_exec_local_result(interface, InterfaceMethods.GET_INSTALLMENT_BY_INDEX, controller_name, w3.toBytes(hexstr=user_tag_str), index, expend_index, installment_index)

def get_repayment(controller_name, user_tag_str, index, expend_index, repayment_index):
    interface = get_contract_instance(settings.INTERFACE_ADDRESS, get_abi_path(ContractNames.INTERFACE))
    return transaction_exec_local_result(interface, InterfaceMethods.GET_REPAYMENT_BY_INDEX, controller_name, w3.toBytes(hexstr=user_tag_str), index, expend_index, repayment_index)


