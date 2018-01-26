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
from amqpstorm import Message
from web3 import exceptions
from django.db import connection
from django.db.utils import OperationalError

import base
from btc_cacheserver import settings
from btc_cacheserver.defines import WriteChainMsgTypes, ContractNames, RouteMethods, InterfaceMethods
from btc_cacheserver.util.procedure_logging import Procedure
from btc_cacheserver.contract.models import TransactionInfo, User, PlatFormInfo, LoanInformation, RepaymentInfo, InstallmentInfo
from deploy import deploy



def on_message(message):
    """This function is called on message received.
    :param message:
    :return:
    """
    msg_body = message.body
    print("Message:", msg_body)

    _json = json.loads(msg_body)

    data = _json["data"]
    try:
        queue_name = settings.WRITE_BLOCKCHAIN_QUEUE + "_" + data["user_tag"][-1]

        # Message Properties.
        properties = {
            'content_type': 'application/json',
        }
        msg = Message.create(message.channel, json.dumps(_json), properties)

        # Publish the message to a queue called, 'simple_queue'.
        msg.publish(queue_name, settings.WRITE_BLOCKCHAIN_EXCHANGE)

        message.ack()

    except OperationalError:
        traceback.print_exc()
        connection.close()
        message.reject(requeue=True)

    except Exception as e:
        traceback.print_exc()
        message.reject(requeue=True)


def consumer():
    with Connection(settings.MQ_HOST, settings.MQ_USER, settings.MQ_PASSWORD, port=settings.MQ_PORT) as connection:
        
        with connection.channel() as channel:
            
            # Declare the Queue
            channel.exchange.declare(settings.WRITE_BLOCKCHAIN_EXCHANGE, exchange_type="topic", durable=True)
            channel.queue.declare(settings.WRITE_BLOCKCHAIN_QUEUE, durable=True)
            channel.queue.bind(settings.WRITE_BLOCKCHAIN_QUEUE, settings.WRITE_BLOCKCHAIN_EXCHANGE, settings.WRITE_BLOCKCHAIN_QUEUE)
            for i in range(16):
                queue_name = settings.WRITE_BLOCKCHAIN_QUEUE + "_" + hex(i)[-1]
                channel.queue.declare(queue_name, durable=True)
                channel.queue.bind(queue_name, settings.WRITE_BLOCKCHAIN_EXCHANGE, queue_name)

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
    # create_user_controller(ContractNames.LOAN_CONTROLLER)

    # controller_address = get_controller_address(ContractNames.LOAN_CONTROLLER)
    # print(controller_address)
    # create_loan_contract("d49a42c1a7ea8ab91d6437c66f58c2c123bd4ee49b9188960bab8ed5e357b116", controller_address)

    # print(get_loan_contract_address(ContractNames.LOAN_CONTROLLER, "d49a42c1a7ea8ab91d6437c66f58c2c123bd4ee49b9188960bab8ed5e357b117"))
    consumer()
