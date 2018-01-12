#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
created by antimoth at 2018-01-04
"""

import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "btc_cacheserver.settings")

import json
import logging
import time
import traceback


from amqpstorm import Connection
from web3 import Web3, RPCProvider
from web3.contract import ConciseContract
from django.db import connection
from django.db.utils import OperationalError

from btc_cacheserver import settings
from btc_cacheserver.defines import WriteChainMsgTypes, UserMapsContractMethods, UserContractMethods
from btc_cacheserver.contract.models import TransactionInfo, User, PlatFormInfo, LoanInformation, RepaymentInfo, InstallmentInfo

logging.basicConfig(level=logging.DEBUG)
contract_instances = {}

provider = RPCProvider(host=settings.BLOCKCHAIN_RPC_HOST, port=settings.BLOCKCHAIN_RPC_PORT)
w3 = Web3(provider)
w3.eth.defaultAccount = settings.BLOCKCHAIN_ACCOUNT

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


def transaction_exec(_ins, method, *args, **kwargs):
    method_call = getattr(_ins, method)
    print(args, kwargs)
    tx_hash = method_call(*args, **kwargs)
    tx_receipt = None
    _wait = 0
    while tx_receipt is None and _wait < settings.TRANSACTION_MAX_WAIT:
        tx_receipt = w3.eth.getTransactionReceipt(tx_hash)
        time.sleep(2)
        _wait += 1
    print(tx_receipt)
    return tx_receipt   


def pure_get_exec(_ins, method, *args, **kwargs):
    method_call = getattr(_ins, method)
    print(args, kwargs)
    return method_call(*args, **kwargs)


def write_tx_record(_ins, method, *args, **kwargs):
    tx_receipt = transaction_exec(_ins, method, *args, **kwargs) 
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


def create_user_contract(user_id, *args):
    try:
        _ins = get_contract_instance(settings.CONTRACT_ADDRESS, abi_file_path=settings.CONTRACT_ABI_FILE)
        result, _transaction = write_tx_record(_ins,UserMapsContractMethods.CREATE_USER_CONTRACT, *args, transact=transact_kwargs) 
        user = User.objects.get(pk=user_id)
        if not user:
            raise Exception("no specfied user!")

        if _transaction is not None:
            _transaction.types = WriteChainMsgTypes.MSG_TYPE_USER
            _transaction.user = user
            _transaction.save()

        if not result:
            return result

        user_contract_address = pure_get_exec(_ins, UserMapsContractMethods.GET_USER_CONTRACT_ADDR, *args)
        if user_contract_address:
            user.contract = user_contract_address
            user.save()

        return result 

    except OperationalError as dbe:
        print(dbe, dir(dbe), traceback.format_exc())
        connection.close()
        return False

    except Exception as e:
        print(traceback.format_exc())
        return False



def update_loan(user_id, loan_id, *args):
    try:
        user = User.objects.get(pk=user_id)
        if not user:
            raise Exception("no specfied user!")

        loan = PlatFormInfo.objects.get(pk=loan_id)
        if not loan:
            raise Exception("no specfied loan!")

        contract_address = user.contract
        _ins = get_contract_instance(contract_address, abi_file_path=settings.USER_CONTRACT_ABI_FILE)
        result, _transaction = write_tx_record(_ins, UserContractMethods.UPDATE_LOAN, loan_id, *args, transact=transact_kwargs)

        if _transaction is not None:
            _transaction.types = WriteChainMsgTypes.MSG_TYPE_LOAN
            _transaction.platform = loan
            _transaction.save()

        if not result:
            return result

        _tag = pure_get_exec(_ins, UserContractMethods.LOAN_TAG, loan_id)
        if _tag:
            loan.tag = _tag.encode("raw_unicode_escape")
            loan.save()

        return result

    except OperationalError as dbe:
        print(dbe, dir(dbe), traceback.format_exc())
        connection.close()
        return False

    except Exception as e:
        print(traceback.format_exc())
        return False


def update_expend(user_id, loan_id, expend_id, *args):
    try:
        user = User.objects.get(pk=user_id)
        if not user:
            raise Exception("no specfied user!")

        loan = PlatFormInfo.objects.get(pk=loan_id)
        if not loan:
            raise Exception("no specfied loan!")

        expend = LoanInformation.objects.get(pk=expend_id)
        if not expend:
            raise Exception("no specfied expend!")

        contract_address = user.contract
        _ins = get_contract_instance(contract_address, abi_file_path=settings.USER_CONTRACT_ABI_FILE)
        result, _transaction = write_tx_record(_ins, UserContractMethods.UPDATE_EXPEND, loan_id, expend_id, *args, transact=transact_kwargs)

        if _transaction is not None:
            _transaction.types = WriteChainMsgTypes.MSG_TYPE_EXPEND
            _transaction.loan = expend
            _transaction.save()

        if not result:
            return result

        _tag = pure_get_exec(_ins, UserContractMethods.EXPENDITURE_TAG, loan_id, expend_id)
        if _tag:
            expend.tag = _tag.encode("raw_unicode_escape")
            expend.save()

        return result

    except OperationalError as dbe:
        print(dbe, dir(dbe), traceback.format_exc())
        connection.close()
        return False

    except Exception as e:
        print(traceback.format_exc())
        return False


def update_installment(user_id, loan_id, expend_id, installment_id, *args):
    try:
        user = User.objects.get(pk=user_id)
        if not user:
            raise Exception("no specfied user!")

        loan = PlatFormInfo.objects.get(pk=loan_id)
        if not loan:
            raise Exception("no specfied loan!")

        expend = LoanInformation.objects.get(pk=expend_id)
        if not expend:
            raise Exception("no specfied expend!")

        installment = InstallmentInfo.objects.get(pk=installment_id)
        if not installment:
            raise Exception("no specfied installment!")

        contract_address = user.contract
        _ins = get_contract_instance(contract_address, abi_file_path=settings.USER_CONTRACT_ABI_FILE)
        result, _transaction = write_tx_record(_ins, UserContractMethods.UPDATE_INSTALLMENT, loan_id, expend_id, installment_id, *args, transact=transact_kwargs)

        if _transaction is not None:
            _transaction.types = WriteChainMsgTypes.MSG_TYPE_INSTALLMENT
            _transaction.installment = installment
            _transaction.save()

        if not result:
            return result

        _tag = pure_get_exec(_ins, UserContractMethods.INSTALLMENT_TAG, loan_id, expend_id, installment_id)
        if _tag:
            installment.tag = _tag.encode("raw_unicode_escape")
            installment.save()

        return result

    except OperationalError as dbe:
        print(dbe, dir(dbe), traceback.format_exc())
        connection.close()
        return False

    except Exception as e:
        print(traceback.format_exc())
        return False



def update_repayment(user_id, loan_id, expend_id, repayment_id, *args):
    try:
        user = User.objects.get(pk=user_id)
        if not user:
            raise Exception("no specfied user!")

        loan = PlatFormInfo.objects.get(pk=loan_id)
        if not loan:
            raise Exception("no specfied loan!")

        expend = LoanInformation.objects.get(pk=expend_id)
        if not expend:
            raise Exception("no specfied expend!")

        repayment = RepaymentInfo.objects.get(pk=repayment_id)
        if not repayment:
            raise Exception("no specfied repayment!")

        contract_address = user.contract
        _ins = get_contract_instance(contract_address, abi_file_path=settings.USER_CONTRACT_ABI_FILE)
        result, _transaction = write_tx_record(_ins, UserContractMethods.UPDATE_REPAYMENT, loan_id, expend_id, repayment_id, *args, transact=transact_kwargs)

        if _transaction is not None:
            _transaction.types = WriteChainMsgTypes.MSG_TYPE_REPAYMENT
            _transaction.repayment = repayment
            _transaction.save()

        if not result:
            return result

        _tag = pure_get_exec(_ins, UserContractMethods.REPAYMENT_TAG, loan_id, expend_id, repayment_id)
        if _tag:
            repayment.tag = _tag.encode("raw_unicode_escape")
            repayment.save()

        return result

    except OperationalError as dbe:
        print(dbe, dir(dbe), traceback.format_exc())
        connection.close()
        return False

    except Exception as e:
        print(traceback.format_exc())
        return False


def on_message(message):
    """This function is called on message received.
    :param message:
    :return:
    """
    msg_body = message.body
    print("Message:", msg_body)

    _json = json.loads(msg_body)
    _msg_type = _json["type"]

    data = _json["data"]
    if WriteChainMsgTypes.MSG_TYPE_USER == _msg_type:
        result = create_user_contract(data["user_id"], data["user_name"].encode("utf-8"), data["id_no"], data["phone_no"])

    elif WriteChainMsgTypes.MSG_TYPE_LOAN == _msg_type:
        result = update_loan(data["user_id"], data["loan_id"], data["credit"], data["platform"].encode("utf-8"))

    elif WriteChainMsgTypes.MSG_TYPE_EXPEND == _msg_type:
        result = update_expend(data["user_id"], data["loan_id"], data["expend_id"], 
                data["apply_amount"], data["receive_amount"], data["time_stamp"], 
                data["interest"], data["order_number"], data["overdue_days"], 
                data["bank_card"], data["purpose"].encode("utf-8"))

    elif WriteChainMsgTypes.MSG_TYPE_INSTALLMENT == _msg_type:
        result = update_installment(data["user_id"], data["loan_id"], data["expend_id"],
                data["installment_id"], data["installment_number"], data["repay_time"],
                data["repay_amount"])

    elif WriteChainMsgTypes.MSG_TYPE_REPAYMENT == _msg_type:
        result = update_repayment(data["user_id"], data["loan_id"], data["expend_id"],
                data["repayment_id"], data["installment_number"], data["repay_amount"],
                data["repay_time"], data["overdue_days"], data["repay_types"])

    if result:
        message.ack()
    else:
        message.reject(requeue=True)

    # Reject the message.
    # message.reject()

    # Reject the message, and put it back in the queue.
    # message.reject(requeue=True)


def consumer():
    with Connection(settings.MQ_HOST, settings.MQ_USER, settings.MQ_PASSWORD, port=settings.MQ_PORT) as connection:
        
        with connection.channel() as channel:
            
            # Declare the Queue
            channel.queue.declare(settings.WRITE_BLOCKCHAIN_QUEUE, durable=True)
            channel.exchange.declare(settings.WRITE_BLOCKCHAIN_EXCHANGE, exchange_type="topic", durable=True)
            channel.queue.bind(settings.WRITE_BLOCKCHAIN_QUEUE, settings.WRITE_BLOCKCHAIN_EXCHANGE, settings.WRITE_BLOCKCHAIN_QUEUE)

            # Set QoS to 1.
            # This will limit the consumer to only prefetch a 1 messages.
            # This is a recommended setting, as it prevents the
            # consumer from keeping all of the messages in a queue to itself.
            channel.basic.qos(1)

            # Start consuming the queue using the callback
            # 'on_message' and last require the message to be acknowledged.
            channel.basic.consume(on_message, settings.WRITE_BLOCKCHAIN_QUEUE, no_ack=False)

            try:
                # Start consuming messages.
                # to_tuple equal to False means that messages consumed
                # are returned as a Message object, rather than a tuple.
                channel.start_consuming(to_tuple=False)
            except KeyboardInterrupt:
                channel.close()


if __name__ == '__main__':
    consumer()
