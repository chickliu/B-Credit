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
from web3.exceptions import BadFunctionCallOutput
from datetime import datetime

import base
from btc_cacheserver import settings
from btc_cacheserver.defines import WriteChainMsgTypes, ContractNames, InterfaceMethods
from btc_cacheserver.util.procedure_logging import Procedure
from btc_cacheserver.contract.models import User, LoanInfo, ExpendInfo, InstallmentInfo, RepaymentInfo, TransactionInfo


w3 = base.create_web3_instance(10000)


class OutGasError(Exception):
    pass


def update_data(method, *args):
    procedure = Procedure("<%s>" % method)
    interface = base.get_contract_instance(settings.INTERFACE_ADDRESS, base.get_abi_path(ContractNames.INTERFACE))
    tx = base.transaction_exec_v2(interface, method, *args)
    procedure.info("UPDATE_DATA tx is: %s", tx.transactionHash)
    if tx.get("cumulativeGasUsed", 0) == settings.BLOCKCHAIN_CALL_GAS_LIMIT:
        raise OutGasError("gas out limit! transaction failed!")
    return tx.transactionHash


def update_loan(data):
    loan_tag = data["loan_tag"]
    user_tag = data["user_tag"]
    tx_hash = update_data(InterfaceMethods.UPDATE_LOAN, 
        ContractNames.LOAN_CONTROLLER,
        w3.toBytes(hexstr=user_tag), 
        w3.toBytes(hexstr=loan_tag), 
        data["platform"].encode("utf-8"),
        data["credit"] or 0
    )
    try:
        _record = LoanInfo.objects.get(tag=loan_tag)

        if _record.owner.tag != user_tag:
            raise Exception("unexpected user tag in loaninfo, bad dada!")

        _record.credit_ceiling=data["credit"] or 0
        _record.platform=data["platform"]

    except LoanInfo.DoesNotExist:
        user = User.objects.get(tag=user_tag)
        _record = LoanInfo(
            owner=user,
            tag=loan_tag,
            credit_ceiling=data["credit"] or 0,
            platform=data["platform"]
        )

    _record.save()

    tx = TransactionInfo.objects.get(transactionHash=tx_hash)
    tx.loan = _record
    tx.save()

def mock_loan(data):
    _loan_data = {
        "user_tag": data["user_tag"],
        "loan_tag": data["loan_tag"],
        "platform": "",
        "credit": 0,
    }
    update_loan(_loan_data)

def update_expend(data):
    loan_tag = data["loan_tag"]
    expend_tag = data["expend_tag"]

    tx_hash = update_data(InterfaceMethods.UPDATE_EXPEND,
        ContractNames.LOAN_CONTROLLER,
        w3.toBytes(hexstr=data["user_tag"]), 
        w3.toBytes(hexstr=loan_tag), 
        w3.toBytes(hexstr=expend_tag), 
        data["order_number"][-32:].encode("utf-8"),
        data["bank_card"].encode("utf-8"),
        data["purpose"].encode("utf-8"),
        data.get("overdue_days",0),
        data["apply_amount"],
        data["receive_amount"],
        int(data["time_stamp"]),
        data["interest"]
    )

    try:
        _record = ExpendInfo.objects.get(tag=expend_tag)

        if _record.loaninfo.tag != loan_tag:
            raise Exception("unexpected loan tag in expendinfo, bad data!")

        _record.apply_amount = data["apply_amount"]
        _record.exact_amount = data["receive_amount"]     
        _record.interest = data["interest"]
        _record.overdue_days = data["overdue_days"]
        _record.apply_time = datetime.fromtimestamp(int(data["time_stamp"]))
        _record.bank_card = data["bank_card"]
        _record.order_number = data["order_number"][-32:]
        _record.reason = data["purpose"]

    except ExpendInfo.DoesNotExist:
        loan = LoanInfo.objects.get(tag=loan_tag)
        _record = ExpendInfo(
            loaninfo=loan,          
            apply_amount=data["apply_amount"],   
            exact_amount=data["receive_amount"],
            interest=data["interest"],
            overdue_days=data.get("overdue_days", 0),
            apply_time=datetime.fromtimestamp(int(data["time_stamp"])),     
            bank_card=data["bank_card"],
            tag=expend_tag,
            order_number=data["order_number"][-32:],
            reason=data["purpose"]
        )

    _record.save()

    tx = TransactionInfo.objects.get(transactionHash=tx_hash)
    tx.expend = _record
    tx.save()


def mock_expend(data):
    _expend_data = {
        "user_tag": data["user_tag"], 
        "loan_tag": data["loan_tag"], 
        "expend_tag": data["expend_tag"], 
        "bank_card": "",
        "order_number": "",
        "purpose": "",
        "apply_amount": 0,
        "receive_amount": 0,
        "interest": 0,
        "time_stamp": int(time.time()),
        "overdue_days":0,
    }
    update_expend(_expend_data)

def update_installment(data):
    installment_tag = data["installment_tag"]
    expend_tag = data["expend_tag"]

    tx_hash = update_data(InterfaceMethods.UPDATE_INSTALLMENT,
        ContractNames.LOAN_CONTROLLER,
        w3.toBytes(hexstr=data["user_tag"]), 
        w3.toBytes(hexstr=data["loan_tag"]), 
        w3.toBytes(hexstr=expend_tag), 
        w3.toBytes(hexstr=installment_tag), 
        data["installment_number"],
        int(data["repay_time"]),
        data["repay_amount"]
    )


    try:
        _record = InstallmentInfo.objects.get(tag=installment_tag)

        if _record.expendinfo.tag != expend_tag:
            raise Exception("unexpected expend tag in installmentinfo, bad data!")

        _record.installment_number = data["installment_number"]
        _record.repay_amount = data["repay_amount"]
        _record.repay_time = datetime.fromtimestamp(int(data["repay_time"]))

    except InstallmentInfo.DoesNotExist:
        expend = ExpendInfo.objects.get(tag=expend_tag)
        _record = InstallmentInfo(
            expendinfo=expend,          
            installment_number=data["installment_number"],
            repay_amount=data["repay_amount"],
            repay_time=datetime.fromtimestamp(int(data["repay_time"])),     
            tag=installment_tag
        )

    _record.save()

    tx = TransactionInfo.objects.get(transactionHash=tx_hash)
    tx.installment = _record
    tx.save()

def update_repayment(data):
    repayment_tag = data["repayment_tag"]
    expend_tag = data["expend_tag"]

    tx_hash = update_data(InterfaceMethods.UPDATE_REPAYMENT,
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

    try:
        _record = RepaymentInfo.objects.get(tag=repayment_tag)
        
        if _record.expendinfo.tag != expend_tag:
            raise Exception("unexpected expend tag in repaymentinfo, bad data!")

        _record.installment_number = data["installment_number"]
        _record.overdue_days = data["overdue_days"]
        _record.repay_amount_type = data["repay_type"]
        _record.real_repay_amount = data["repay_amount"]
        _record.real_repay_time = datetime.fromtimestamp(int(data["repay_time"]))

    except RepaymentInfo.DoesNotExist:
        expend = ExpendInfo.objects.get(tag=expend_tag)
        _record = RepaymentInfo(
            expendinfo=expend,
            installment_number=data["installment_number"],
            overdue_days=data["overdue_days"],
            real_repay_time=datetime.fromtimestamp(int(data["repay_time"])),
            repay_amount_type=data["repay_type"],
            real_repay_amount=data["repay_amount"],
            tag=repayment_tag
        )

    _record.save()

    tx = TransactionInfo.objects.get(transactionHash=tx_hash)
    tx.repayment = _record
    tx.save()


def on_message(message):
    """This function is called on message received.
    :param message:
    :return:
    """
    time.sleep(random.randint(1, 10))
    procedure = Procedure("<MSG-%s>" % sys.argv[1])
    msg_body = message.body

    _json = json.loads(msg_body)
    _msg_type = _json["type"]

    data = _json["data"]
    try:
        user_tag_str = data["user_tag"]
        procedure.start(" message(%s) for user(%s)", _msg_type, user_tag_str)

        #  sure to create the user contract and the loan store contract
        base.get_loan_store_address(ContractNames.LOAN_CONTROLLER, user_tag_str)

        if WriteChainMsgTypes.MSG_TYPE_USER == _msg_type:
            base.get_loan_store_address(ContractNames.LOAN_CONTROLLER, user_tag_str)

        elif WriteChainMsgTypes.MSG_TYPE_LOAN == _msg_type:
            update_loan(data)

        elif WriteChainMsgTypes.MSG_TYPE_EXPEND == _msg_type:
            update_expend(data)

        elif WriteChainMsgTypes.MSG_TYPE_INSTALLMENT == _msg_type:
            update_installment(data)

        elif WriteChainMsgTypes.MSG_TYPE_REPAYMENT == _msg_type:
            update_repayment(data)

        else:
            raise Exception("unknown messsage type!")

        procedure.info("ACK_MSG, message is %s", msg_body)
        message.ack()

    except OperationalError:
        procedure.exception("MSG_MYSQL_ERROR, REJECT_REQUEUE_MSG, message is %s", msg_body)
        connection.close()
        message.reject(requeue=True)

    except BadFunctionCallOutput:
        controller_address = base.get_controller_address(ContractNames.LOAN_CONTROLLER)
        base.create_loan_contract(user_tag_str, controller_address)
        message.reject(requeue=True)

    except OutGasError:
        try:
            if WriteChainMsgTypes.MSG_TYPE_EXPEND == _msg_type:
                mock_loan(data)

            elif WriteChainMsgTypes.MSG_TYPE_INSTALLMENT == _msg_type:
                mock_expend(data)

            elif WriteChainMsgTypes.MSG_TYPE_REPAYMENT == _msg_type:
                mock_expend(data)

            else:
                raise Exception("upexpected OutGasError!")

            procedure.info("REJECT_REQUEUE_MSG, message is %s", msg_body)
            message.reject(requeue=True)

        except OutGasError:
            if WriteChainMsgTypes.MSG_TYPE_INSTALLMENT == _msg_type or WriteChainMsgTypes.MSG_TYPE_REPAYMENT == _msg_type:
                mock_loan(data)
                mock_expend(data)
                procedure.info("REJECT_REQUEUE_MSG_MSG, message is %s", msg_body)
                message.reject(requeue=True)
            else:
                procedure.exception("MSG_WRITE_BLOCK_ERROR, REJECT_REDISTRIBUTE, message is %s", msg_body)
                message.reject(requeue=False)

        except Exception:
            procedure.exception("MSG_WRITE_BLOCK_ERROR, REJECT_REDISTRIBUTE, message is %s", msg_body)
            message.reject(requeue=False)

    except Exception:
        procedure.exception("MSG_WRITE_BLOCK_ERROR, REJECT_REDISTRIBUTE, message is %s", msg_body)
        message.reject(requeue=False)



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
