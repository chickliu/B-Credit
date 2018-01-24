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


class ContractNames(object):
    ROLES               = "Roles"
    RBAC                = "RBAC"
    PAUSABLE            = "Pausable"

    CONTROLLER_ROUTE    = "ControllerRoute"
    DATA_STORE_ROUTE    = "DataStoreRoute"
    INTERFACE           = "Interface"
    USER_CONTROLLER     = "UserController"
    USER_CONTRACT_STORE = "UserContractStore"
    USER_CONTRACT       = "UserContract"
    LOAN_DATA_STORE     = "LoanDataStore"


class ContractMethodsBase(object):
    ROLE_WRITER       = "writer"
    ROLE_CALLER       = "caller"

    # "checkRole"
    # "hasRole"
    ADMIN_REMOVE_ROLE = "adminRemoveRole"
    ADMIN_ADD_ROLE    = "adminAddRole"
    UNPAUSE           = "unpause"
    PAUSE             = "pause"


class LoanMethods(ContractMethodsBase):
    GET_LOAN_TIMES           = "getLoanTimes"
    GET_LATEST_UPDATE        = "getLatestUpdate"
    GET_LOAN_BY_INDEX        = "getLoanByIndex"
    GET_EXPEND_BY_INDEX      = "getExpendByIndex"
    GET_INSTALLMENT_BY_INDEX = "getInstallmentByIndex"
    GET_REPAYMENT_BY_INDEX   = "getRepaymentByIndex"

    UPDATE_LOAN              = "updateLoan"
    UPDATE_EXPEND            = "updateExpenditure"
    UPDATE_INSTALLMENT       = "updateInstallment"
    UPDATE_REPAYMENT         = "updateRepayment"


class UserContractMethods(LoanMethods):
    SET_STORE    = "setStore"
    SET_ROUTER   = "setRouter"

    GET_USER_TAG = "getUserTag"

class InterfaceMethods(LoanMethods):
    SET_ROUTER             = "setRouter"
    SET_CONTROLLER         = "setController"
    GET_CONTROLLER_ADDRESS = "getControllerAddress"
    GET_USER_ADDRESS       = "getUserContractAddress"


class StoreMethods(ContractMethodsBase):
    SET_ADDRESS         = "setAddress"
    SET_CURRENT_VERSION = "setCurrentVersion"
    GET_MAX_VERSION     = "getMaxVersion"
    GET_CURRENT_VERSION = "getCurrentVersion"
    GET_ADDRESS         = "getAddress"
    GET_CURRENT_ADDRESS = "getCurrentAddress"


