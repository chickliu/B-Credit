#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
created by antimoth at 2018-01-05
"""


class WriteChainMsgTypes(object):

    MSG_TYPE_USER = "user"
    MSG_TYPE_LOAN = "loan"
    MSG_TYPE_EXPEND = "expend"
    MSG_TYPE_INSTALLMENT = "installment"
    MSG_TYPE_REPAYMENT = "repayment"


class ContractNames(object):
    ROLES                 = "Roles"
    RBAC                  = "RBAC"
    PAUSABLE              = "Pausable"

    INTERFACE             = "Interface"
    CONTROLLER_ROUTE      = "ControllerRoute"

    LOAN_CONTROLLER       = "LoanController"
    LOAN_CONTRACT_ROUTE   = "LoanContractRoute"

    USER_LOAN             = "UserLoan"
    USER_LOAN_STORE_ROUTE = "UserLoanStoreRoute"
    USER_LOAN_STORE       = "UserLoanStore"


class RoleBase(object):
    ROLE_WRITER       = "writer"
    ROLE_CALLER       = "caller"
    ROLE_ADMIN        = "admin"

    NAME              = "name"
    CHECK_ROLE        = "checkRole"
    HAS_ROLE          = "hasRole"
    ADMIN_ADD_ROLE    = "adminAddRole"
    ADMIN_REMOVE_ROLE = "adminRemoveRole"
    UNPAUSE           = "unpause"
    PAUSE             = "pause"
    PAUSED            = "paused"


class RouteMethods(RoleBase):
    SET_ADDRESS         = "setAddress"
    SET_CURRENT_VERSION = "setCurrentVersion"
    GET_MAX_VERSION     = "getMaxVersion"
    GET_CURRENT_VERSION = "getCurrentVersion"
    GET_ADDRESS         = "getAddress"
    GET_CURRENT_ADDRESS = "getCurrentAddress"


class LoanMethods(RoleBase):
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


class UserLoanMethods(LoanMethods):
    SET_USER_LOAN_STORE_ROUTE         = "setUserLoanStoreRoute"

    GET_USER_LOAN_STORE_ROUTE_ADDRESS = "getUserLoanStoreRouteAddress"

    GET_USER_LOAN_STORE_ADDRESS       = "getUserLoanStoreAddress"
    GET_USER_LOAN_STORE_VERSION       = "getUserLoanStoreVersion"


class LoanControllerMethods(UserLoanMethods):
    SET_LOAN_CONTRACT_ROUTE = "setLoanContractRoute"

    GET_LOAN_CONTRACT_ROUTE_ADDRESS = "getLoanContractRouteAddress"

    GET_LOAN_CONTRACT_ADDRESS = "getLoanContractAddress"
    GET_LOAN_CONTRACT_VERSION = "getLoanContractVersion"


class InterfaceMethods(LoanControllerMethods):
    SET_CONTROLLER_ROUTE = "setControllerRoute"

    GET_CONTROLLER_ROUTE_ADDRESS = "getControllerRouteAddress"

    GET_CONTROLLER_ADDRESS = "getControllerAddress"
    GET_CONTROLLER_VERSION = "getControllerVersion"


