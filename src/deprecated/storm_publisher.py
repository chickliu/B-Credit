import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "btc_cacheserver.settings")
import logging
import json


from amqpstorm import Connection
from amqpstorm import Message

from btc_cacheserver import settings
from btc_cacheserver.defines import WriteChainMsgTypes
from btc_cacheserver.contract.models import User, PlatFormInfo, LoanInformation, InstallmentInfo, RepaymentInfo

logging.basicConfig(level=logging.DEBUG)


def push_users(channel):
    records = User.objects.filter(contract__isnull=True)
    for record in records:
        _json = {
            "type": WriteChainMsgTypes.MSG_TYPE_USER,
            "data": {
                "user_id": record.id,
                "user_name": record.username,
                "id_no": record.id_no,
                "phone_no": record.phone_no,
            },
        
        }
        # Message Properties.
        properties = {
            'content_type': 'application/json',
        }
        message = Message.create(channel, json.dumps(_json), properties)

        # Publish the message to a queue called, 'simple_queue'.
        message.publish(settings.WRITE_BLOCKCHAIN_QUEUE, settings.WRITE_BLOCKCHAIN_EXCHANGE)


def push_loans(channel):
    records = PlatFormInfo.objects.filter(tag__isnull=True)
    for record in records:
        _json = {
            "type": WriteChainMsgTypes.MSG_TYPE_LOAN,
            "data": {
                "user_id": record.owner_id,
                "loan_id": record.id,
                "credit": record.credit_ceiling,
                "platform": record.platform,
            },
        
        }
        # Message Properties.
        properties = {
            'content_type': 'application/json',
        }
        message = Message.create(channel, json.dumps(_json), properties)

        # Publish the message to a queue called, 'simple_queue'.
        message.publish(settings.WRITE_BLOCKCHAIN_QUEUE, settings.WRITE_BLOCKCHAIN_EXCHANGE)


def push_expends(channel):
    records = LoanInformation.objects.filter(tag__isnull=True)
    for record in records:
        _json = {
            "type": WriteChainMsgTypes.MSG_TYPE_EXPEND,
            "data": {
                "user_id": record.platform.owner_id,
                "loan_id": record.platform_id,
                "expend_id": record.id,
                "apply_amount": record.apply_amount,
                "receive_amount": record.exact_amount,
                "time_stamp": int(record.apply_time.timestamp()),
                "interest": record.interest,
                "order_number": record.order_number,
                "overdue_days": record.overdue_days,
                "bank_card": record.bank_card,
                "purpose": record.reason,
            },
        
        }
        # Message Properties.
        properties = {
            'content_type': 'application/json',
        }
        message = Message.create(channel, json.dumps(_json), properties)

        # Publish the message to a queue called, 'simple_queue'.
        message.publish(settings.WRITE_BLOCKCHAIN_QUEUE, settings.WRITE_BLOCKCHAIN_EXCHANGE)


def push_installments(channel):
    records = InstallmentInfo.objects.filter(tag__isnull=True)
    for record in records:
        _json = {
            "type": WriteChainMsgTypes.MSG_TYPE_INSTALLMENT,
            "data": {
                "user_id": record.loan_info.platform.owner_id,
                "loan_id": record.loan_info.platform_id,
                "expend_id": record.loan_info_id,
                "installment_id": record.id,
                "repay_amount": record.repay_amount,
                "installment_number": record.installment_number,
                "repay_time": int(record.repay_time.timestamp()),
            },
        
        }
        # Message Properties.
        properties = {
            'content_type': 'application/json',
        }
        message = Message.create(channel, json.dumps(_json), properties)

        # Publish the message to a queue called, 'simple_queue'.
        message.publish(settings.WRITE_BLOCKCHAIN_QUEUE, settings.WRITE_BLOCKCHAIN_EXCHANGE)


def push_repayments(channel):
    records = RepaymentInfo.objects.filter(tag__isnull=True)
    for record in records:
        _json = {
            "type": WriteChainMsgTypes.MSG_TYPE_REPAYMENT,
            "data": {
                "user_id": record.loan_info.platform.owner_id,
                "loan_id": record.loan_info.platform_id,
                "expend_id": record.loan_info_id,
                "repayment_id": record.id,
                "repay_amount": record.real_repay_amount,
                "installment_number": record.installment_number,
                "repay_time": int(record.real_repay_time.timestamp()),
                "overdue_days": record.overdue_days,
                "repay_types": record.repay_amount_type,
            },
        
        }
        # Message Properties.
        properties = {
            'content_type': 'application/json',
        }
        message = Message.create(channel, json.dumps(_json), properties)

        # Publish the message to a queue called, 'simple_queue'.
        message.publish(settings.WRITE_BLOCKCHAIN_QUEUE, settings.WRITE_BLOCKCHAIN_EXCHANGE)


def publish_message():
    with Connection(settings.MQ_HOST, settings.MQ_USER, settings.MQ_PASSWORD, port=settings.MQ_PORT) as connection:
        with connection.channel() as channel:
            # Declare the Queue
            channel.queue.declare(settings.WRITE_BLOCKCHAIN_QUEUE, durable=True)
            channel.exchange.declare(settings.WRITE_BLOCKCHAIN_EXCHANGE, exchange_type="topic", durable=True)
            channel.queue.bind(settings.WRITE_BLOCKCHAIN_QUEUE, settings.WRITE_BLOCKCHAIN_EXCHANGE, settings.WRITE_BLOCKCHAIN_QUEUE)
            push_users(channel)
            push_loans(channel)
            push_expends(channel)
            push_installments(channel)
            push_repayments(channel)


if __name__ == '__main__':
    publish_message()
