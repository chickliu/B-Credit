#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
created by antimoth at 2018-01-05
"""


class WriteChainMsgTypes(object):

    MSG_TYPE_USER = "user"
    MSG_TYPE_LOAN = "loan"
    MSG_TYPE_EXPEND = "expend"
    MSG_TYPE_INSTALLMENT = "instalment"
    MSG_TYPE_REPAYMENT = "repayment"


class UserMapsContractMethods(object):
    CREATE_USER_CONTRACT = 'createUserContract'
    GET_USER_CONTRACT_ADDR = 'getUserContractAddr'
    GET_USER_CONTRACT_ADDR_BY_TAG = 'getUserContractAddrByTag'
    GET_USER_TAG = 'getUserTag'


class UserContractMethods(object):
    EXPENDITURE_TAG = 'expenditureTag' 
    LOAN_TAG = 'loanTag'
    REPAYMENT_TAG = 'repaymentTag'
    INSTALLMENT_TAG = 'installmentTag'

    GET_LOAN_TIMES = 'getLoanTimes'
    GET_LATEST_UPDATE = 'getLatestUpdate'
    GET_REPAYMENT_BY_INDEX = 'getRepaymentByIndex'
    GET_EXPEND_BY_INDEX = 'getExpendByIndex'
    GET_INSTALLMENT_BY_INDEX = 'getInstallmentByIndex'
    GET_LOAN_BY_INDEX = 'getLoanByIndex'

    UPDATE_LOAN = 'updateLoan'
    UPDATE_REPAYMENT = 'updateRepayment'
    UPDATE_INSTALLMENT = 'updateInstallment'
    UPDATE_EXPEND = 'updateExpend'
