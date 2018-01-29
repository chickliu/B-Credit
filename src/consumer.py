#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
created by antimoth at 2018-01-04
"""

import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "btc_cacheserver.settings")

import time
import sys
import json
import random


from amqpstorm import Connection
from django.db import connection
from django.db.utils import OperationalError

import base
from btc_cacheserver import settings
from btc_cacheserver.defines import WriteChainMsgTypes, ContractNames, RouteMethods, InterfaceMethods
from btc_cacheserver.util.procedure_logging import Procedure
from deploy import deploy


w3 = base.create_web3_instance(10000)


def _deploy_user_contract(user_tag_str):
    user_contract_address = deploy(
        ContractNames.USER_CONTRACT, 
        [w3.toBytes(hex=user_tag_str), settings.USER_LOAN_STORE_ROUTE_ADDRESS, ]
    )
    data_store_route = base.get_contract_instance(settings.USER_LOAN_STORE_ROUTE_ADDRESS, settings.get_abi_path(ContractNames.DATA_STORE_ROUTE))
    base.transaction_exec_v2(data_store_route, RouteMethods.ADMIN_ADD_ROLE, user_contract_address, RouteMethods.ROLE_WRITER)
    base.transaction_exec_v2(data_store_route, RouteMethods.ADMIN_ADD_ROLE, user_contract_address, RouteMethods.ROLE_CALLER)

    loan_store_address = deploy(
        ContractNames.LOAN_DATA_STORE,
        [w3.toBytes(hex=user_tag_str), ],
    )
    base.transaction_exec_v2(data_store_route, RouteMethods.SET_ADDRESS, user_contract_address, loan_store_address, True)

    loan_store = base.get_contract_instance(loan_store_address, settings.get_abi_path(ContractNames.LOAN_DATA_STORE))
    base.transaction_exec_v2(loan_store, RouteMethods.ADMIN_ADD_ROLE, user_contract_address, RouteMethods.ROLE_WRITER)
    base.transaction_exec_v2(loan_store, RouteMethods.ADMIN_ADD_ROLE, user_contract_address, RouteMethods.ROLE_CALLER)

    return user_contract_address


def create_loan_store(user_tag_str, loan_contract_address):
    procedure = Procedure("<%s>" % user_tag_str)

    loan_store_route = base.get_contract_instance(settings.USER_LOAN_STORE_ROUTE_ADDRESS, base.get_abi_path(ContractNames.USER_LOAN_STORE_ROUTE))

    has_call_role = base.transaction_exec_local_result(loan_store_route, RouteMethods.HAS_ROLE, loan_contract_address, RouteMethods.ROLE_CALLER)
    if not has_call_role:
        base.role_added_from_contract_ins(loan_contract_address, loan_store_route, RouteMethods.ROLE_CALLER)

    loan_store_address = base.transaction_exec_local_result(loan_store_route, RouteMethods.GET_CURRENT_ADDRESS, loan_contract_address)
    procedure.info("loan_store_address is %s", loan_store_address)


    if not int(loan_store_address, 16):
        loan_store_address = deploy(
            ContractNames.USER_LOAN_STORE,
            [w3.toBytes(hexstr=user_tag_str), ]
        )

    _tx = base.transaction_exec_v2(loan_store_route, RouteMethods.SET_ADDRESS, loan_contract_address, loan_store_address, True)
    procedure.info(" %s(%s) %s %s(%s)  tx is %s", 
            ContractNames.USER_LOAN_STORE_ROUTE, 
            settings.USER_LOAN_STORE_ROUTE_ADDRESS, 
            RouteMethods.SET_ADDRESS, 
            ContractNames.USER_LOAN_STORE, 
            loan_store_address, 
            _tx.transactionHash
    )

    loan_store = base.get_contract_instance(loan_store_address, base.get_abi_path(ContractNames.USER_LOAN_STORE))

    has_write_role = base.transaction_exec_local_result(loan_store, RouteMethods.HAS_ROLE, loan_contract_address, RouteMethods.ROLE_WRITER)
    if not has_write_role:
        base.role_added_from_contract_ins(loan_contract_address, loan_store, RouteMethods.ROLE_WRITER)

    has_call_role = base.transaction_exec_local_result(loan_store, RouteMethods.HAS_ROLE, loan_contract_address, RouteMethods.ROLE_CALLER)
    if not has_call_role:
        base.role_added_from_contract_ins(loan_contract_address, loan_store, RouteMethods.ROLE_CALLER)

    return loan_store_address

def create_loan_contract(user_tag_str, controller_address):
    procedure = Procedure("<%s>" % user_tag_str)
    bytes_user_tag = w3.toBytes(hexstr=user_tag_str)

    loan_contract_route = base.get_contract_instance(settings.LOAN_CONTRACT_ROUTE_ADDRESS, base.get_abi_path(ContractNames.LOAN_CONTRACT_ROUTE))

    has_call_role = base.transaction_exec_local_result(loan_contract_route, RouteMethods.HAS_ROLE, controller_address, RouteMethods.ROLE_CALLER)
    if not has_call_role:
        base.role_added_from_contract_ins(controller_address, loan_contract_route, RouteMethods.ROLE_CALLER)

    loan_contract_address = base.transaction_exec_local_result(loan_contract_route, RouteMethods.GET_CURRENT_ADDRESS, bytes_user_tag)
    procedure.info("loan_contract_address is %s", loan_contract_address)

    if not int(loan_contract_address, 16):
        loan_contract_address = deploy(
            ContractNames.USER_LOAN,
            [bytes_user_tag, settings.USER_LOAN_STORE_ROUTE_ADDRESS, ],
        )

    create_loan_store(user_tag_str, loan_contract_address)
    
    _tx = base.transaction_exec_v2(loan_contract_route, RouteMethods.SET_ADDRESS, bytes_user_tag, loan_contract_address, True)
    procedure.info(" %s(%s) %s %s(%s)  tx is %s", 
            ContractNames.LOAN_CONTRACT_ROUTE, 
            settings.LOAN_CONTRACT_ROUTE_ADDRESS, 
            RouteMethods.SET_ADDRESS, 
            ContractNames.USER_LOAN, 
            loan_contract_address, 
            _tx.transactionHash
    )

    loan_contract = base.get_contract_instance(loan_contract_address, base.get_abi_path(ContractNames.USER_LOAN))

    has_write_role = base.transaction_exec_local_result(loan_contract, RouteMethods.HAS_ROLE, controller_address, RouteMethods.ROLE_WRITER)
    if not has_write_role:
        base.role_added_from_contract_ins(controller_address, loan_contract, RouteMethods.ROLE_WRITER)

    has_call_role = base.transaction_exec_local_result(loan_contract, RouteMethods.HAS_ROLE, controller_address, RouteMethods.ROLE_CALLER)
    if not has_call_role:
        base.role_added_from_contract_ins(controller_address, loan_contract, RouteMethods.ROLE_CALLER)

    return loan_contract_address

def create_user_controller(controller_name):
    procedure = Procedure("<%s>" % controller_name)
    
    interface_address = settings.INTERFACE_ADDRESS
    controller_route = base.get_contract_instance(settings.CONTROLLER_ROUTE_ADDRESS, base.get_abi_path(ContractNames.CONTROLLER_ROUTE))

    has_call_role = base.transaction_exec_local_result(controller_route, RouteMethods.HAS_ROLE, interface_address, RouteMethods.ROLE_CALLER)
    if not has_call_role:
        base.role_added_from_contract_ins(interface_address, controller_route, RouteMethods.ROLE_CALLER)

    controller_address = base.transaction_exec_local_result(controller_route, RouteMethods.GET_CURRENT_ADDRESS, controller_name)
    procedure.info("controller_address is %s", controller_address)

    if not int(controller_address, 16):
        controller_address = deploy(
            ContractNames.LOAN_CONTROLLER,
            [settings.LOAN_CONTRACT_ROUTE_ADDRESS, ],
        )

    # set current loan controller address to route
    _tx = base.transaction_exec_v2(controller_route, RouteMethods.SET_ADDRESS, ContractNames.LOAN_CONTROLLER, controller_address, True)
    procedure.info(" %s(%s) %s %s(%s)  tx is %s", 
            ContractNames.CONTROLLER_ROUTE, 
            settings.CONTROLLER_ROUTE_ADDRESS, 
            RouteMethods.SET_ADDRESS, 
            ContractNames.LOAN_CONTROLLER, 
            controller_address, 
            _tx.transactionHash
    )

    # add authorization for interface
    controller = base.get_contract_instance(controller_address, base.get_abi_path(ContractNames.LOAN_CONTROLLER))

    has_write_role = base.transaction_exec_local_result(controller, RouteMethods.HAS_ROLE, interface_address, RouteMethods.ROLE_WRITER)
    if not has_write_role:
        base.role_added_from_contract_ins(interface_address, controller, RouteMethods.ROLE_WRITER)

    has_call_role = base.transaction_exec_local_result(controller, RouteMethods.HAS_ROLE, interface_address, RouteMethods.ROLE_CALLER)
    if not has_call_role:
        base.role_added_from_contract_ins(interface_address, controller, RouteMethods.ROLE_CALLER)

    return controller_address


def get_controller_address(controller_name):
    interface = base.get_contract_instance(settings.INTERFACE_ADDRESS, base.get_abi_path(ContractNames.INTERFACE))
    return base.transaction_exec_local_result(interface, InterfaceMethods.GET_CONTROLLER_ADDRESS, controller_name)

def get_loan_contract_address(controller_name, user_tag_str):
    interface = base.get_contract_instance(settings.INTERFACE_ADDRESS, base.get_abi_path(ContractNames.INTERFACE))
    return base.transaction_exec_local_result(interface, InterfaceMethods.GET_LOAN_CONTRACT_ADDRESS, controller_name, w3.toBytes(hexstr=user_tag_str))


def update_data(method, *args):

    procedure = Procedure("<%s>" % method)
    interface = base.get_contract_instance(settings.INTERFACE_ADDRESS, base.get_abi_path(ContractNames.INTERFACE))
    tx = base.transaction_exec_v2(interface, method, *args)
    procedure.info("UPDATE_DATA tx is: %s", tx.transactionHash)
    if tx.get("cumulativeGasUsed", 0) == settings.BLOCKCHAIN_CALL_GAS_LIMIT:
        raise Exception("gas out limit! transaction failed!")



def on_message(message):
    """This function is called on message received.
    :param message:
    :return:
    """
    # time.sleep(random.randint(1, 10))
    procedure = Procedure("<MSG-%s>" % sys.argv[1])
    msg_body = message.body

    _json = json.loads(msg_body)
    _msg_type = _json["type"]

    data = _json["data"]
    try:
        user_tag_str = data["user_tag"]
        loan_contract_address = get_loan_contract_address(ContractNames.LOAN_CONTROLLER, user_tag_str)
        if not int(loan_contract_address, 16):
            controller_address = get_controller_address(ContractNames.LOAN_CONTROLLER)
            create_loan_contract(user_tag_str, controller_address)

        if WriteChainMsgTypes.MSG_TYPE_USER == _msg_type:
            loan_contract_address = get_loan_contract_address(ContractNames.LOAN_CONTROLLER, user_tag_str)
            if not int(loan_contract_address, 16):
                controller_address = get_controller_address(ContractNames.LOAN_CONTROLLER)
                create_loan_contract(user_tag_str, controller_address)

        elif WriteChainMsgTypes.MSG_TYPE_LOAN == _msg_type:
            update_data(InterfaceMethods.UPDATE_LOAN, 
                ContractNames.LOAN_CONTROLLER,
                w3.toBytes(hexstr=data["user_tag"]), 
                w3.toBytes(hexstr=data["loan_tag"]), 
                data["platform"].encode("utf-8"),
                data["credit"] or 0
            )

        elif WriteChainMsgTypes.MSG_TYPE_EXPEND == _msg_type:
            update_data(InterfaceMethods.UPDATE_EXPEND,
                ContractNames.LOAN_CONTROLLER,
                w3.toBytes(hexstr=data["user_tag"]), 
                w3.toBytes(hexstr=data["loan_tag"]), 
                w3.toBytes(hexstr=data["expend_tag"]), 
                data["order_number"].encode("utf-8"),
                data["bank_card"].encode("utf-8"),
                data["purpose"].encode("utf-8"),
                data.get("overdue_days",0),
                data["apply_amount"],
                data["receive_amount"],
                int(data["time_stamp"]),
                data["interest"]
            )

        elif WriteChainMsgTypes.MSG_TYPE_INSTALLMENT == _msg_type:
            update_data(InterfaceMethods.UPDATE_INSTALLMENT,
                ContractNames.LOAN_CONTROLLER,
                w3.toBytes(hexstr=data["user_tag"]), 
                w3.toBytes(hexstr=data["loan_tag"]), 
                w3.toBytes(hexstr=data["expend_tag"]), 
                w3.toBytes(hexstr=data["installment_tag"]), 
                data["installment_number"],
                int(data["repay_time"]),
                data["repay_amount"]
            )

        elif WriteChainMsgTypes.MSG_TYPE_REPAYMENT == _msg_type:
            update_data(InterfaceMethods.UPDATE_REPAYMENT,
                ContractNames.LOAN_CONTROLLER,
                w3.toBytes(hexstr=data["user_tag"]), 
                w3.toBytes(hexstr=data["loan_tag"]), 
                w3.toBytes(hexstr=data["expend_tag"]), 
                w3.toBytes(hexstr=data["repayment_tag"]), 
                data["installment_number"],
                data.get("overdue_days", 0),
                data["repay_type"],
                data["repay_amount"],
                int(data["repay_time"])
            )
        else:
            procedure.info("UNKOWN_MSG, message is %s", msg_body)
            message.reject(requeue=False)
            # message.reject(requeue=True)
            return

        procedure.info("ACK_MSG, message is %s", msg_body)
        message.ack()

    except OperationalError:
        procedure.exception("MSG_WRITE_BLOCK_ERROR, message is %s", msg_body)
        connection.close()
        message.reject(requeue=False)
        # message.reject(requeue=True)
        # message.channel.close()

    except Exception as e:
        procedure.exception("MSG_WRITE_BLOCK_ERROR, message is %s", msg_body)
        try:
            if WriteChainMsgTypes.MSG_TYPE_EXPEND == _msg_type:
                update_data(InterfaceMethods.UPDATE_LOAN, 
                    ContractNames.LOAN_CONTROLLER,
                    w3.toBytes(hexstr=data["user_tag"]), 
                    w3.toBytes(hexstr=data["loan_tag"]), 
                    "",
                    0
                )

            elif WriteChainMsgTypes.MSG_TYPE_INSTALLMENT == _msg_type:
                update_data(InterfaceMethods.UPDATE_EXPEND,
                    ContractNames.LOAN_CONTROLLER,
                    w3.toBytes(hexstr=data["user_tag"]), 
                    w3.toBytes(hexstr=data["loan_tag"]), 
                    w3.toBytes(hexstr=data["expend_tag"]), 
                    "",
                    "",
                    "",
                    0,
                    0,
                    0,
                    int(time.time()),
                    0
                )

            elif WriteChainMsgTypes.MSG_TYPE_REPAYMENT == _msg_type:
                update_data(InterfaceMethods.UPDATE_EXPEND,
                    ContractNames.LOAN_CONTROLLER,
                    w3.toBytes(hexstr=data["user_tag"]), 
                    w3.toBytes(hexstr=data["loan_tag"]), 
                    w3.toBytes(hexstr=data["expend_tag"]), 
                    "",
                    "",
                    "",
                    0,
                    0,
                    0,
                    int(time.time()),
                    0
                )
        except Exception:
            procedure.exception("MSG_WRITE_BLOCK_ERROR, message is %s", msg_body)
            if WriteChainMsgTypes.MSG_TYPE_INSTALLMENT == _msg_type:
                update_data(InterfaceMethods.UPDATE_LOAN, 
                    ContractNames.LOAN_CONTROLLER,
                    w3.toBytes(hexstr=data["user_tag"]), 
                    w3.toBytes(hexstr=data["loan_tag"]), 
                    "",
                    0
                )
                update_data(InterfaceMethods.UPDATE_EXPEND,
                    ContractNames.LOAN_CONTROLLER,
                    w3.toBytes(hexstr=data["user_tag"]), 
                    w3.toBytes(hexstr=data["loan_tag"]), 
                    w3.toBytes(hexstr=data["expend_tag"]), 
                    "",
                    "",
                    "",
                    0,
                    0,
                    0,
                    int(time.time()),
                    0
                )

            elif WriteChainMsgTypes.MSG_TYPE_REPAYMENT == _msg_type:
                update_data(InterfaceMethods.UPDATE_LOAN, 
                    ContractNames.LOAN_CONTROLLER,
                    w3.toBytes(hexstr=data["user_tag"]), 
                    w3.toBytes(hexstr=data["loan_tag"]), 
                    "",
                    0
                )
                update_data(InterfaceMethods.UPDATE_EXPEND,
                    ContractNames.LOAN_CONTROLLER,
                    w3.toBytes(hexstr=data["user_tag"]), 
                    w3.toBytes(hexstr=data["loan_tag"]), 
                    w3.toBytes(hexstr=data["expend_tag"]), 
                    "",
                    "",
                    "",
                    0,
                    0,
                    0,
                    int(time.time()),
                    0
                )

        procedure.info("REJECT_MSG, message is %s", msg_body)
        message.reject(requeue=False)
        # message.reject(requeue=True)
        # message.channel.close()


def consumer(queue_name):
    with Connection(settings.MQ_HOST, settings.MQ_USER, settings.MQ_PASSWORD, port=settings.MQ_PORT) as connection:
        
        with connection.channel() as channel:
            
            # Declare the Queue
            channel.queue.declare(queue_name, durable=True, arguments={"x-dead-letter-exchange": settings.WRITE_BLOCKCHAIN_EXCHANGE, "x-dead-letter-routing-key": settings.WRITE_BLOCKCHAIN_QUEUE, })
            channel.exchange.declare(settings.WRITE_BLOCKCHAIN_EXCHANGE, exchange_type="topic", durable=True)
            channel.queue.bind(queue_name, settings.WRITE_BLOCKCHAIN_EXCHANGE, queue_name)

            # Set QoS to 1.
            # This will limit the consumer to only prefetch a 1 messages.
            # This is a recommended setting, as it prevents the
            # consumer from keeping all of the messages in a queue to itself.
            channel.basic.qos(1)

            # Start consuming the queue using the callback
            # 'on_message' and last require the message to be acknowledged.
            channel.basic.consume(on_message, queue_name, no_ack=False)

            try:
                # Start consuming messages.
                # to_tuple equal to False means that messages consumed
                # are returned as a Message object, rather than a tuple.
                channel.start_consuming(to_tuple=False)
            except KeyboardInterrupt:
                channel.close()

if __name__ == '__main__':
    queue_name = settings.WRITE_BLOCKCHAIN_QUEUE + "_" + sys.argv[1]
    consumer(queue_name)
