#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
created by antimoth at 2018-01-04
"""

import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "btc_cacheserver.settings")

import time
import json
import copy
import requests

from amqpstorm import Connection
from amqpstorm import Message
from django.utils import timezone
from django.db import connection
from django.db.utils import OperationalError
from web3.exceptions import BadFunctionCallOutput
from datetime import datetime

import base
from btc_cacheserver import settings
from btc_cacheserver.defines import ContractNames
from btc_cacheserver.util.procedure_logging import Procedure
from btc_cacheserver.contract.models import User, LoanInfo, ExpendInfo, InstallmentInfo, RepaymentInfo

w3 = base.create_web3_instance(10000)
default_tz = timezone.get_default_timezone()


class OutGasError(Exception):
    pass


def get_mq_msg_readied(queue_name):
    url="http://10.2.0.150:8762/api/queues/%%2f/%s"
    rsp = requests.get(url % queue_name, auth=("admin", "admin"))
    return rsp.json().get("messages")

def check_installments(user_tag_str, record, loan_index, expend_index, installment_counter):
    arguments = copy.copy(locals())
    procedure = Procedure("<installment>")
    procedure.start(arguments)

    for index in range(1, installment_counter + 1):

        result = base.get_installment(ContractNames.LOAN_CONTROLLER, user_tag_str, loan_index, expend_index, index)

        procedure.info("chain installment data: %s", result)

        _tag, installment_number, repay_time, repay_amount = result 
        
        _tag = w3.toHex(_tag.encode('raw_unicode_escape')).strip("\0")[2:]
        chain_date = datetime.fromtimestamp(repay_time, tz=default_tz)

        try:
            installment = InstallmentInfo.objects.get(tag=_tag)

            if installment.installment_number != installment_number:
                print("update")
                installment.installment_number = installment_number

            if installment.repay_time.timestamp() != repay_time:
                print("update", installment.repay_time, chain_date, repay_time)
                installment.repay_time = chain_date

            if installment.repay_amount != repay_amount:
                print("update")
                installment.repay_amount = repay_amount

        except InstallmentInfo.DoesNotExist:

            procedure.info("create installment %s", _tag)

            installment = InstallmentInfo(
                expendinfo=record,
                installment_number=installment_number,
                repay_time=chain_date,
                repay_amount=repay_amount,
                tag=_tag
            )

        installment.save()


def check_repayments(user_tag_str, record, loan_index, expend_index, repayment_counter):
    arguments = copy.copy(locals())
    procedure = Procedure("<repayment>")
    procedure.start(arguments)

    for index in range(1, repayment_counter + 1):

        result = base.get_repayment(ContractNames.LOAN_CONTROLLER, user_tag_str, loan_index, expend_index, index)

        procedure.info("chain repayment data: %s", result)

        _tag, installment_number, overdue_days, repay_types, repay_amount, repay_time = result

        _tag = w3.toHex(_tag.encode('raw_unicode_escape')).strip("\0")[2:]
        chain_date = datetime.fromtimestamp(repay_time, tz=default_tz)

        try:
            repayment = RepaymentInfo.objects.get(tag=_tag)

            if repayment.installment_number != installment_number:
                print("update")
                repayment.installment_number = installment_number

            if repayment.real_repay_time.timestamp() != repay_time:
                print("update", repayment.real_repay_time, chain_date, repay_time)
                repayment.real_repay_time = chain_date

            if repayment.overdue_days != overdue_days:
                print("update")
                repayment.overdue_days = overdue_days

            if repayment.real_repay_amount != repay_amount:
                print("update")
                repayment.real_repay_amount = repay_amount

            if repayment.repay_amount_type != repay_types:
                print("update")
                repayment.repay_amount_type = repay_types

        except RepaymentInfo.DoesNotExist:

            procedure.info("create repayment %s", _tag)

            repayment = RepaymentInfo(
                expendinfo=record, 
                installment_number=installment_number,
                real_repay_time=chain_date,
                overdue_days=overdue_days,
                real_repay_amount=repay_amount,
                repay_amount_type =repay_types,
                tag=_tag
            )

        repayment.save()

def check_expends(user_tag_str, record, loan_index, expend_times):
    arguments = copy.copy(locals())
    procedure = Procedure("<expend>")
    procedure.start(arguments)

    for index in range(1, expend_times + 1):

        result = base.get_expend(ContractNames.LOAN_CONTROLLER, user_tag_str, loan_index, index)

        procedure.info("chain expend data: %s", result)

        _tag, order_number, bank_card, purpose, installment_counter, repayment_counter, overdue_days, apply_amount, receive_amount, timestamp, interest = result

        if not installment_counter:
            raise BadFunctionCallOutput("no installment, rewrite!")

        if not repayment_counter:
            raise BadFunctionCallOutput("no repayment, rewrite!")

        chain_purpose = w3.toText(purpose.encode("raw_unicode_escape")).strip("\0")
        chain_order_number = w3.toText(order_number.encode("raw_unicode_escape")).strip("\0")
        chain_bank_card = w3.toText(bank_card.encode("raw_unicode_escape")).strip("\0")

        _tag = w3.toHex(_tag.encode('raw_unicode_escape')).strip("\0")[2:]

        chain_date = datetime.fromtimestamp(timestamp, tz=default_tz)

        if not chain_order_number:
            raise BadFunctionCallOutput("mock expend, rewrite!")

        try:
            expend = ExpendInfo.objects.get(tag=_tag)

            if expend.installment_counter != installment_counter: 
                expend.installment_counter = installment_counter

            if expend.repayment_counter != repayment_counter:
                expend.repayment_counter = repayment_counter

            if expend.apply_amount != apply_amount:
                print("update")
                expend.apply_amount = apply_amount

            if expend.exact_amount != receive_amount:
                print("update")
                expend.exact_amount = receive_amount

            if expend.apply_time.timestamp() != timestamp:
                print("update", expend.apply_time, chain_date, timestamp)
                expend.apply_time = chain_date
            
            if expend.interest != interest:
                print("update")
                expend.interest = interest

            if expend.order_number != chain_order_number:
                print("update")
                expend.order_number = chain_order_number

            if expend.overdue_days != overdue_days:
                print("update")
                expend.overdue_days = overdue_days
            
            if expend.bank_card !=chain_bank_card:
                print("update")
                expend.bank_card = chain_bank_card

            if expend.reason != chain_purpose:
                print("update")
                expend.reason = chain_purpose

        except ExpendInfo.DoesNotExist:

            procedure.info("create expendinfo %s", _tag)

            expend = ExpendInfo(
                 loaninfo=record, 
                 order_number=chain_order_number,
                 apply_amount=apply_amount, 
                 exact_amount=receive_amount, 
                 reason=chain_purpose,
                 apply_time=chain_date, 
                 interest=interest, 
                 bank_card=chain_bank_card, 
                 overdue_days=overdue_days, 
                 tag=_tag, 
                 installment_counter=installment_counter, 
                 repayment_counter=repayment_counter
            )

        expend.save()

        check_installments(user_tag_str, expend, loan_index, index, installment_counter)
        check_repayments(user_tag_str, expend, loan_index, index, repayment_counter)


def check_loans(user_tag_str, record, loan_times):
    arguments = copy.copy(locals())
    procedure = Procedure("<loan>")
    procedure.start(arguments)

    for index in range(1, loan_times + 1):

        result = base.get_loan(ContractNames.LOAN_CONTROLLER, user_tag_str, index)

        procedure.info("chain loan data: %s", result)

        _tag, platform, expend_times, credit = result 

        if not expend_times:
            raise BadFunctionCallOutput("no expend, rewrite!")

        chain_platform = w3.toText(platform.encode("raw_unicode_escape")).strip("\0")

       # cut "0x" at the beginning of the _tag 
        _tag = w3.toHex(_tag.encode('raw_unicode_escape')).strip("\0")[2:]

        if not chain_platform:
            raise BadFunctionCallOutput("mock loan, rewrite!")

        try:
            loan  = LoanInfo.objects.get(tag=_tag)

            if loan.expend_counter!= expend_times:
                loan.expend_counter = expend_times

            if loan.platform != chain_platform:
                print("update")
                loan.platform = chain_platform

            if loan.credit_ceiling != credit:
                print("update")
                loan.credit_ceiling = credit

        except LoanInfo.DoesNotExist:
            procedure.info("create loan %s", _tag)

            loan = LoanInfo(
                platform=chain_platform, 
                credit_ceiling=credit, 
                expend_counter=expend_times, 
                tag=_tag,
                owner=record
            )

        loan.save()

        check_expends(user_tag_str, loan, index, expend_times)


def check_latest_update(user_tag_str):
    arguments = copy.copy(locals())
    procedure = Procedure("<latest_update>")
    procedure.start(arguments)
    
    latest_update = base.get_latest_update(ContractNames.LOAN_CONTROLLER, user_tag_str)
    try:
        record = User.objects.get(tag=user_tag_str)
    except User.DoesNotExist:
        record = User(tag=user_tag_str)
        record.save()
    loan_times = base.get_loan_times(ContractNames.LOAN_CONTROLLER, user_tag_str)
    if not loan_times:
        raise BadFunctionCallOutput("no loan, rewrite!")
    check_loans(user_tag_str, record, loan_times)

    record.latest_update = latest_update
    record.loan_counter = loan_times
    record.save()


def on_message(message):
    """This function is called on message received.
    :param message:
    :return:
    """

    procedure = Procedure("<CHECK_MSG>")

    rewrite_message_count = get_mq_msg_readied("write_blockchain_queue_re")
    while rewrite_message_count > 0:
        time.sleep(40 * rewrite_message_count)
        rewrite_message_count = get_mq_msg_readied("write_blockchain_queue_re")

    msg_body = message.body

    _json = json.loads(msg_body)
    _msg_type = _json["type"]

    data = _json["data"]
    try:
        user_tag_str = data["user_tag"]
        procedure.start(" message(%s) for user(%s)", _msg_type, user_tag_str)

        check_latest_update(user_tag_str)

        procedure.info("ACK_CHECK_MSG, message is %s", msg_body)
        message.ack()

    except OperationalError:
        procedure.exception("MSG_MYSQL_ERROR, REJECT_REQUEUE_CHECK_MSG, message is %s", msg_body)
        connection.close()
        message.reject(requeue=True)

    except BadFunctionCallOutput:
        procedure.exception("MOCK_CHECK_MSG, REJECT_REWRITE, message is %s", msg_body)
        _data = {"data": {"no_id": data["id_no"], }, }
        # Message Properties.
        properties = {
            'content_type': 'application/json',
        }
        msg = Message.create(message.channel, json.dumps(_data), properties)

        # Publish the message to a queue called, 'simple_queue'.
        msg.publish(settings.CHECK_BLOCKCHAIN_QUERY, settings.CHECK_BLOCKCHAIN_EXCHANGE)

        time.sleep(40)

        # rewrite_message_count = get_mq_msg_readied("write_blockchain_queue_re")
        # while rewrite_message_count > 0:
        #     time.sleep(40 * rewrite_message_count)
        #     rewrite_message_count = get_mq_msg_readied("write_blockchain_queue_re")

        message.reject(requeue=True)

    except Exception:
        procedure.exception("ERROR_CHECK_MSG, REJECT_REDISTRIBUTE, message is %s", msg_body)
        message.reject(requeue=True)



def consumer():
    with Connection(settings.MQ_HOST, settings.MQ_USER, settings.MQ_PASSWORD, port=settings.MQ_PORT) as connection:
        
        with connection.channel() as channel:
            
            # Declare the Queue
            channel.exchange.declare(settings.CHECK_BLOCKCHAIN_EXCHANGE, exchange_type="topic", durable=True)

            channel.queue.declare(settings.CHECK_BLOCKCHAIN_QUEUE, durable=True)
            channel.queue.bind(settings.CHECK_BLOCKCHAIN_QUEUE, settings.CHECK_BLOCKCHAIN_EXCHANGE, settings.CHECK_BLOCKCHAIN_QUEUE)

            channel.queue.declare(settings.CHECK_BLOCKCHAIN_QUERY, durable=True)
            channel.queue.bind(settings.CHECK_BLOCKCHAIN_QUERY, settings.CHECK_BLOCKCHAIN_EXCHANGE, settings.CHECK_BLOCKCHAIN_QUERY)

            # Set QoS to 1.
            # This will limit the consumer to only prefetch a 1 messages.
            # This is a recommended setting, as it prevents the
            # consumer from keeping all of the messages in a queue to itself.
            channel.basic.qos(1)

            # Start consuming the queue using the callback
            # 'on_message' and last require the message to be acknowledged.
            channel.basic.consume(on_message, settings.CHECK_BLOCKCHAIN_QUEUE, no_ack=False)

            try:
                # Start consuming messages.
                # to_tuple equal to False means that messages consumed
                # are returned as a Message object, rather than a tuple.
                channel.start_consuming(to_tuple=False)
            except KeyboardInterrupt:
                channel.close()

if __name__ == '__main__':
    # queue_name = settings.WRITE_BLOCKCHAIN_QUEUE + "_" + sys.argv[1]
    # consumer(queue_name)
    consumer()
    # _user = "dd12c0b5a74995e1f0a4141d95acaf37f7607f8940cc24633e0ca5a9c9d87820"
    # check_latest_update(_user)
