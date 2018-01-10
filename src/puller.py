#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
created by antimoth at 2018-01-04
"""

import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "btc_cacheserver.settings")

import json
import logging

from datetime import datetime
from web3 import Web3, RPCProvider
from web3.contract import ConciseContract

from btc_cacheserver import settings
from btc_cacheserver.defines import UserContractMethods
from btc_cacheserver.contract.models import User, PlatFormInfo, LoanInformation, RepaymentInfo, InstallmentInfo

logging.basicConfig(level=logging.INFO)
contract_instances = {}

provider = RPCProvider(host=settings.BLOCKCHAIN_RPC_HOST, port=settings.BLOCKCHAIN_RPC_PORT)
w3 = Web3(provider)

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


def pure_get_exec(_ins, method, *args, **kwargs):
    method_call = getattr(_ins, method)
    print("pure_get_blockchain,", method, args, kwargs)
    return method_call(*args, **kwargs)


def pull_installments(_ins, record, loan_index, expend_index, installment_counter):

    print("pull installments, expend_id: %s, index: %s, loan_index: %s" % (record.id, expend_index, loan_index), installment_counter)

    for index in range(1, installment_counter + 1):

        installment_number, repay_time, repay_amount, owner, _tag = pure_get_exec(_ins, UserContractMethods.GET_INSTALLMENT_BY_INDEX, loan_index, expend_index, index)
        
        try:
            installment = InstallmentInfo.objects.get(tag=_tag.encode("raw_unicode_escape"))

            if installment.creator != owner:
                installment.creator = owner

            if owner != settings.BLOCKCHAIN_ACCOUNT:
                print("update %s" % installment)

                if installment.installment_number != installment_number:
                    installment.installment_number = installment_number

                chain_date = datetime.fromtimestamp(repay_time)
                if installment.repay_time != chain_date:
                    installment.repay_time = chain_date

                if installment.repay_amount != repay_amount:
                    installment.repay_amount = repay_amount

        except InstallmentInfo.DoesNotExist:

            print("create installment!")

            installment = InstallmentInfo(
                loan_info=record,
                installment_number=installment_number,
                repay_time=datetime.fromtimestamp(repay_time),
                repay_amount=repay_amount,
                tag=_tag.encode("raw_unicode_escape"),
                creator=owner
            )

        installment.save()


def pull_repayments(_ins, record, loan_index, expend_index, repayment_counter):

    print("pull repayments , expend_id: %s, index: %s, loan_index: %s" % (record.id, expend_index, loan_index), repayment_counter)

    for index in range(1, repayment_counter + 1):

        installment_number, repay_amount, repay_time, overdue_days, repay_types, owner, _tag = pure_get_exec(_ins, UserContractMethods.GET_REPAYMENT_BY_INDEX, loan_index, expend_index, index)

        try:
            repayment = RepaymentInfo.objects.get(tag=_tag.encode("raw_unicode_escape"))

            if repayment.creator != owner:
                repayment.creator = owner

            if owner != settings.BLOCKCHAIN_ACCOUNT:
                if repayment.installment_number != installment_number:
                    repayment.installment_number = installment_number

                chain_date = datetime.fromtimestamp(repay_time)
                if repay_time.real_repay_time != chain_date:
                    repayment.real_repay_time = chain_date

                if repayment.overdue_days != overdue_days:
                    repayment.overdue_days = overdue_days

                if repayment.real_repay_amount != repay_amount:
                    repayment.real_repay_amount = repay_amount

                if repay_amount.repay_amount_type != repay_types:
                    repayment.repay_amount_type = repay_types

        except RepaymentInfo.DoesNotExist:

            print("create repayment!")

            repayment = RepaymentInfo(
                loan_info=record, 
                installment_number=installment_number,
                real_repay_time=datetime.fromtimestamp(repay_time),
                overdue_days=overdue_days,
                real_repay_amount=repay_amount,
                repay_amount_type =repay_types,
                tag=_tag.encode("raw_unicode_escape"),
                creator=owner
            )

        repayment.save()

def pull_expends(_ins, record, loan_index, expend_times):

    print("pull expends, loan_id: %s, index: %s" % (record.id, loan_index), expend_times)

    for index in range(1, expend_times + 1):

        apply_amount, receive_amount, timestamp, interest, order_number, overdue_days, bank_card, purpose, installment_counter, repayment_counter, owner, _tag = pure_get_exec(_ins, UserContractMethods.GET_EXPEND_BY_INDEX, loan_index, index)

        print("times: ", installment_counter, repayment_counter)

        chain_purpose = purpose.replace("\x00", "").encode("raw_unicode_escape").decode("utf-8")

        try:
            expend = LoanInformation.objects.get(tag=_tag.encode("raw_unicode_escape"))

            if expend.installment_counter != installment_counter: 
                expend.installment_counter = installment_counter

            if expend.repayment_counter != repayment_counter:
                expend.repayment_counter = repayment_counter

            if expend.creator != owner:
                expend.creator = owner

            if owner != settings.BLOCKCHAIN_ACCOUNT:
                print("update %s!" % expend)

                if expend.apply_amount != apply_amount:
                    expend.apply_amount = apply_amount

                if expend.exact_amount != receive_amount:
                    expend.exact_amount = receive_amount

                chain_date = datetime.fromtimestamp(timestamp)
                if expend.apply_time != chain_date:
                    expend.apply_time = chain_date
                
                if expend.interest != interest:
                    expend.interest = interest

                if expend.order_number != order_number:
                    expend.order_number = order_number

                if expend.overdue_days != overdue_days:
                    expend.overdue_days = overdue_days
                
                if expend.bank_card != bank_card:
                    expend.bank_card = bank_card

                if expend.reason != chain_purpose:
                    expend.reason = chain_purpose

        except LoanInformation.DoesNotExist:

            print("create expend!")

            expend = LoanInformation(
                 platform=record, 
                 order_number=order_number,
                 apply_amount=apply_amount, 
                 exact_amount=receive_amount, 
                 reason=chain_purpose,
                 apply_time=datetime.fromtimestamp(timestamp), 
                 interest=interest, 
                 bank_card=bank_card, 
                 overdue_days=overdue_days, 
                 tag=_tag, 
                 installment_counter=installment_counter, 
                 repayment_counter=repayment_counter, 
                 creator=owner
            )

        expend.save()

        pull_installments(_ins, expend, loan_index, index, installment_counter)
        pull_repayments(_ins, expend, loan_index, index, repayment_counter)


def pull_loans(_ins, record, loan_times):

    print("pull loans, user_id: %s" % record.id, loan_times)

    for index in range(1, loan_times + 1):

        platform, credit, expend_times, owner, loan_tag = pure_get_exec(_ins, UserContractMethods.GET_LOAN_BY_INDEX, index)

        print("expend_times: ", expend_times)

        chain_platform = platform.replace("\x00", "").encode("raw_unicode_escape").decode("utf-8")

        try:
            loan  = PlatFormInfo.objects.get(tag=loan_tag.encode("raw_unicode_escape"))
            if loan.creator != owner:
                loan.creator = owner

            if loan.expend_counter!= expend_times:
                loan.expend_counter = expend_times

            if owner != settings.BLOCKCHAIN_ACCOUNT:
                print("update %s" % loan)

                if loan.platform != chain_platform:
                    loan.platform = chain_platform

                if loan.credit_ceiling != credit:
                    loan.credit_ceiling = credit

        except PlatFormInfo.DoesNotExist:

            print("create loan!")

            loan = PlatFormInfo(
                platform=chain_platform, 
                credit_ceiling=credit, 
                expend_counter=expend_times, 
                tag=loan_tag.encode("raw_unicode_escape"),
                owner=record,
                creator=owner
            )

        loan.save()

        pull_expends(_ins, loan, index, expend_times)


def pull_blockchain_data():

    records = User.objects.filter(contract__isnull=False)

    for record in records:
        contract_address = record.contract

        _ins = get_contract_instance(contract_address, abi_file_path=settings.USER_CONTRACT_ABI_FILE)
        latest_update = pure_get_exec(_ins, UserContractMethods.GET_LATEST_UPDATE)
        if latest_update == record.latest_update:
            continue

        loan_times = pure_get_exec(_ins, UserContractMethods.GET_LOAN_TIMES)
        pull_loans(_ins, record, loan_times)

        record.latest_update = latest_update
        record.loan_counter = loan_times
        record.save()


if __name__ == '__main__':
    pull_blockchain_data()


