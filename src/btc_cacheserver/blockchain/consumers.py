#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import logging
import json
from web3 import Web3, RPCProvider
from channels import Group
from btc_cacheserver import settings
from btc_cacheserver.blockchain.decode_contract import decode_input, is_create_user_tx

METHOD_TYPE_MAP = {"getLoanByIndex":1, "updateLoan":2,
                   "getExpendByIndex":1, "updateExpenditure":2,
                   "getInstallmentByIndex":1, "updateInstallment":2,
                   "getRepaymentByIndex":1, "updateRepayment":2 }

METHOD_SHOW_MAP = {"none":u"", "getLoanByIndex":u"授信", "updateLoan":u"授信",
                   "getExpendByIndex":u"支用", "updateExpenditure":u"支用",
                   "getInstallmentByIndex":u"分期", "updateInstallment":u"分期",
                   "getRepaymentByIndex":u"还款", "updateRepayment":u"还款" }

TYPE_SHOW_MAP = {-1:u"创建用户", 0:u"转账", 1:u"查询", 2:u"写入"}

Log = logging.getLogger("websocket")
provider = RPCProvider(host=settings.BLOCKCHAIN_RPC_HOST, port=settings.BLOCKCHAIN_RPC_PORT)
w3 = Web3(provider)

def ws_connect(message, account_hash=None):
    global new_block_filter, new_transaction_filter
    new_block_filter = w3.eth.filter('latest')
    new_transaction_filter = w3.eth.filter('latest')
    message.reply_channel.send({"accept": True})
    Group("chain").add(message.reply_channel)

    def new_block_callback(block_hash):
        data_list = []
        block_num = w3.eth.getBlock(block_hash).number
        for i in range(10):
            block_info = w3.eth.getBlock(block_num - i)
            data = {
                    "blocknumber": block_info['number'],
                    "miner": block_info['miner'],
                    "time": block_info['timestamp'],
                    "tx_count": len(block_info['transactions'])
            }
            data_list.append(data)
            #Log.warn("block_number:{},miner:{}".format(data['blocknumber'],data['miner']))
        datas = {"blockchain":data_list}
        json_data = json.dumps(datas)
        Group("chain").send({"text": json_data})

    def new_transaction_callback(block_hash):
        data_list = []
        #block_num = w3.eth.getTransaction(tx_hash).blockNumber
        block_num = w3.eth.getBlock(block_hash).number
        #block_num = w3.eth.blockNumber
        for i in range(100):
            block = w3.eth.getBlock(block_num - i)
            bt_list = block.transactions
            bt_list.reverse()
            for th in bt_list:
                tx_info = w3.eth.getTransaction(th)
                #print('acc_hash:{},tx_from:{}'.format(account_hash,tx_info['from'][2:]))
                if account_hash and tx_info['from'][2:] != account_hash:
                    continue
                if tx_info['to']:
                    method_name, args = decode_input(tx_info['input'])
                    if method_name in METHOD_TYPE_MAP:
                        tx_type = METHOD_TYPE_MAP[method_name]
                    elif tx_info['input'] == '0x':
                        tx_type = 0
                    else:
                        #Log.warn("tx has to and input is not empty.tx_hash:{}".format(th))
                        continue
                else:
                    if is_create_user_tx(tx_info['input']):
                        tx_type = -1
                    else:
                        #Log.warn("tx has no to and not create_user_tx.tx_hash:{}".format(th))
                        continue

                if tx_type in [1,2]:
                    tx_message = u'{}向{}{}一笔{}信息'.format(tx_info['from'][:10], tx_info['to'][:10], TYPE_SHOW_MAP[tx_type],  METHOD_SHOW_MAP[method_name])
                elif tx_type == 0:
                    tx_message = u'{}向{}转入{}'.format(tx_info['from'][:10], tx_info['to'][:10], tx_info['value'])
                elif tx_type == -1:
                    tx_message = u'{}新增一个用户'.format(tx_info['from'][:10])
                data = {
                        "tx_hash": th,
                        "from": tx_info['from'],
                        "to": tx_info['to'],
                        "type": TYPE_SHOW_MAP[tx_type],
                        "fee": tx_info['value'],
                        "info": tx_message,
                        "time": block.timestamp
                }
                data_list.append(data)
                #Log.warn("tx_hash:{},info message:{}".format(data['tx_hash'],data['info']))
                if len(data_list) > 9:
                    break
            else:
                continue
            break
        datas = {"transactions":data_list}
        json_data = json.dumps(datas)
        Group("chain").send({"text": json_data})

    if not account_hash and not new_block_filter.running:
        new_block_filter.watch(new_block_callback)
    if not new_transaction_filter.running:
        new_transaction_filter.watch(new_transaction_callback)

def ws_disconnect(message, account_hash=None):
    while not new_block_filter.stopped:
        try:
            new_block_filter.stop_watching()
        except RuntimeError:
            #print('RuntimeError')
            pass
    while not new_transaction_filter.stopped:
        try:
            new_transaction_filter.stop_watching()
        except RuntimeError:
            #print('RuntimeError')
            pass
    #print('stopped')
    Group("chain").discard(message.reply_channel)
