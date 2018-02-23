#!/usr/bin/env python
# -*- coding: utf-8 -*-

from btc_cacheserver.defines import ContractNames

CHANNEL_GROUP_MAIN = "main"

contract_names = (
    ContractNames.INTERFACE, ContractNames.CONTROLLER_ROUTE,
    ContractNames.LOAN_CONTROLLER, ContractNames.LOAN_CONTRACT_ROUTE,
    ContractNames.USER_LOAN, ContractNames.USER_LOAN_STORE, ContractNames.USER_LOAN_STORE_ROUTE,
)
contract_show_names = (
    u"接口合约", u"控制器路由合约", 
    u"控制器合约", u"借贷路由合约", 
    u"用户借贷合约", u"借贷存储合约", u"借贷存储路由合约",
)
map_contract_show_names = dict(zip(contract_names, contract_show_names))


class TransactionTypes(object):
    DEPLOY_TX                 = "deploy_tx"
    TRANSFER                  = "transfer"
    UNPAUSE                   = "unpause"
    PAUSE                     = "pause"
    ADMIN_ADD_ROLE            = "adminAddRole"
    ADMIN_REMOVE_ROLE         = "adminRemoveRole"
    SET_ADDRESS               = "setAddress"
    SET_CURRENT_VERSION       = "setCurrentVersion"
    UPDATE_LOAN               = "updateLoan"
    UPDATE_EXPENDITURE        = "updateExpenditure"
    UPDATE_INSTALLMENT        = "updateInstallment"
    UPDATE_REPAYMENT          = "updateRepayment"
    SET_USER_LOAN_STORE_ROUTE = "setUserLoanStoreRoute"
    SET_LOAN_CONTRACT_ROUTE   = "setLoanContractRoute"
    SET_CONTROLLER_ROUTE      = "setControllerRoute"

map_tx_types_to_show_names = {
    TransactionTypes.DEPLOY_TX                 : u"合约部署",
    TransactionTypes.TRANSFER                  : u"货币转账",
    TransactionTypes.UNPAUSE                   : u"合约控制",
    TransactionTypes.PAUSE                     : u"合约控制",
    TransactionTypes.ADMIN_ADD_ROLE            : u"合约配置",
    TransactionTypes.ADMIN_REMOVE_ROLE         : u"合约配置",
    TransactionTypes.SET_ADDRESS               : u"合约配置",
    TransactionTypes.SET_CURRENT_VERSION       : u"合约配置",
    TransactionTypes.UPDATE_LOAN               : u"数据写入",
    TransactionTypes.UPDATE_EXPENDITURE        : u"数据写入",
    TransactionTypes.UPDATE_INSTALLMENT        : u"数据写入",
    TransactionTypes.UPDATE_REPAYMENT          : u"数据写入",
    TransactionTypes.SET_USER_LOAN_STORE_ROUTE : u"合约配置",
    TransactionTypes.SET_LOAN_CONTRACT_ROUTE   : u"合约配置",
    TransactionTypes.SET_CONTROLLER_ROUTE      : u"合约配置",
}

map_tx_types_to_template = {
    TransactionTypes.DEPLOY_TX                 : u"{who}部署了一个{contract}",
    TransactionTypes.TRANSFER                  : u"{trans_from}向{trans_to}转账{trans_value}",
    TransactionTypes.UNPAUSE                   : u"{who}解锁了{contract}",
    TransactionTypes.PAUSE                     : u"{who}锁定了{contract}",
    TransactionTypes.ADMIN_ADD_ROLE            : u"{who}更改了{contract}的权限集",
    TransactionTypes.ADMIN_REMOVE_ROLE         : u"{who}更改了{contract}的权限集",
    TransactionTypes.SET_ADDRESS               : u"{who}在{contract}增加了路由规则",
    TransactionTypes.SET_CURRENT_VERSION       : u"{who}更改了{contract}的路由规则",
    TransactionTypes.UPDATE_LOAN               : u"{who}写入了一条授信记录",
    TransactionTypes.UPDATE_EXPENDITURE        : u"{who}写入了一条支用记录",
    TransactionTypes.UPDATE_INSTALLMENT        : u"{who}写入了一条分期计划",
    TransactionTypes.UPDATE_REPAYMENT          : u"{who}写入了一条还款记录",
    TransactionTypes.SET_USER_LOAN_STORE_ROUTE : u"{who}更改了{contract}的路由合约",
    TransactionTypes.SET_LOAN_CONTRACT_ROUTE   : u"{who}更改了{contract}的路由合约",
    TransactionTypes.SET_CONTROLLER_ROUTE      : u"{who}更改了{contract}的路由合约",
}
