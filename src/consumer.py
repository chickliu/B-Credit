#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
created by antimoth at 2018-01-04
"""

import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "btc_cacheserver.settings")

import json
import traceback


from amqpstorm import Connection
from web3 import exceptions
from django.db import connection
from django.db.utils import OperationalError

import base
from btc_cacheserver import settings
from btc_cacheserver.defines import WriteChainMsgTypes, ContractNames, UserContractMethods, StoreMethods, InterfaceMethods
from btc_cacheserver.util.procedure_logging import Procedure
from btc_cacheserver.contract.models import TransactionInfo, User, PlatFormInfo, LoanInformation, RepaymentInfo, InstallmentInfo
from deploy import deploy


w3 = base.create_web3_instance(10000)


def write_tx_record(_ins, method, *args, **kwargs):
    tx_receipt = base.transaction_exec_v2(_ins, method, *args, **kwargs) 
    if tx_receipt is None:
        return False, None
    _transaction = TransactionInfo(
        cumulativeGasUsed=tx_receipt.cumulativeGasUsed,
        gasUsed=tx_receipt.gasUsed,
        blockNumber=tx_receipt.blockNumber,
        transactionIndex=tx_receipt.transactionIndex,
        call_from=getattr(tx_receipt,"from"),
        call_to=tx_receipt.to,
        transactionHash=tx_receipt.transactionHash,
    )
    _transaction.save()
    return False if tx_receipt.get("cumulativeGasUsed", 0) == settings.BLOCKCHAIN_CALL_GAS_LIMIT else True, _transaction


def _deploy_user_contract(user_tag_str):
    user_contract_address = deploy(
        ContractNames.USER_CONTRACT, 
        [w3.toBytes(hex=user_tag_str), settings.DATA_STORE_ROUTE_ADDRESS, ]
    )
    data_store_route = base.get_contract_instance(settings.DATA_STORE_ROUTE_ADDRESS, settings.get_abi_path(ContractNames.DATA_STORE_ROUTE))
    base.transaction_exec_v2(data_store_route, StoreMethods.ADMIN_ADD_ROLE, user_contract_address, StoreMethods.ROLE_WRITER)
    base.transaction_exec_v2(data_store_route, StoreMethods.ADMIN_ADD_ROLE, user_contract_address, StoreMethods.ROLE_CALLER)

    loan_store_address = deploy(
        ContractNames.LOAN_DATA_STORE,
        [w3.toBytes(hex=user_tag_str), ],
    )
    base.transaction_exec_v2(data_store_route, StoreMethods.SET_ADDRESS, user_contract_address, loan_store_address, True)

    loan_store = base.get_contract_instance(loan_store_address, settings.get_abi_path(ContractNames.LOAN_DATA_STORE))
    base.transaction_exec_v2(loan_store, StoreMethods.ADMIN_ADD_ROLE, user_contract_address, StoreMethods.ROLE_WRITER)
    base.transaction_exec_v2(loan_store, StoreMethods.ADMIN_ADD_ROLE, user_contract_address, StoreMethods.ROLE_CALLER)

    return user_contract_address

def _deploy_user_controller(user_contract_store_address=None):
    procedure = Procedure("<UserController>")
    user_controller_address = deploy(
        ContractNames.USER_CONTROLLER,
        [settings.DATA_STORE_ROUTE_ADDRESS, ],
    )

    data_store_route = base.get_contract_instance(settings.DATA_STORE_ROUTE_ADDRESS, settings.get_abi_path(ContractNames.DATA_STORE_ROUTE))
    base.transaction_exec_v2(data_store_route, StoreMethods.ADMIN_ADD_ROLE, user_controller_address, StoreMethods.ROLE_WRITER)
    base.transaction_exec_v2(data_store_route, StoreMethods.ADMIN_ADD_ROLE, user_controller_address, StoreMethods.ROLE_CALLER)

    if user_contract_store_address is None:
        user_contract_store_address = deploy(
            ContractNames.USER_CONTRACT_STORE,
            [],
        )
    _version = base.transaction_exec_result(data_store_route, StoreMethods.SET_ADDRESS, user_controller_address, user_contract_store_address, True)
    procedure.info("%s store address is %s, version is %s" % (user_controller_address, user_contract_store_address, _version))

    user_contract_store = base.get_contract_instance(user_contract_store_address, settings.get_abi_path(ContractNames.USER_CONTRACT_STORE))
    base.transaction_exec_v2(user_contract_store, StoreMethods.ADMIN_ADD_ROLE, user_controller_address, StoreMethods.ROLE_WRITER)
    base.transaction_exec_v2(user_contract_store, StoreMethods.ADMIN_ADD_ROLE, user_controller_address, StoreMethods.ROLE_CALLER)

    return user_controller_address

def create_user_controller(controller_name):
    procedure = Procedure("<%s>" % controller_name)
    interface = base.get_contract_instance(settings.INTERFACE_ADDRESS, settings.get_abi_path(ContractNames.INTERFACE))
    user_controller_address = base.transaction_exec_result(interface, InterfaceMethods.GET_CONTROLLER_ADDRESS, controller_name)
    if not int(user_controller_address, 16):
        user_controller_address = _deploy_user_controller()

        controller_route = base.get_contract_instance(settings.CONTROLLER_ROUTE_ADDRESS, settings.get_abi_path(ContractNames.CONTROLLER_ROUTE))
        base.transaction_exec_v2(controller_route, StoreMethods.ADMIN_ADD_ROLE, settings.INTERFACE_ADDRESS, StoreMethods.ROLE_WRITER)
        base.transaction_exec_v2(controller_route, StoreMethods.ADMIN_ADD_ROLE, settings.INTERFACE_ADDRESS, StoreMethods.ROLE_CALLER)

        _version = base.transaction_exec_result(interface, InterfaceMethods.SET_CONTROLLER_ADDRESS, ContractNames.USER_CONTROLLER, user_controller_address)
        procedure.info("%s(%s) version is %s", ContractNames.USER_CONTROLLER, user_controller_address, _version)

    print(user_controller_address)



if __name__ == '__main__':
    create_user_controller(ContractNames.USER_CONTROLLER)
