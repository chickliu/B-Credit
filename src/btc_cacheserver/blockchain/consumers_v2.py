#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
import json

from channels import Group
from channels.sessions import channel_session
from channels.generic import BaseConsumer

import base

from btc_cacheserver import settings
from btc_cacheserver.defines import ContractNames
from btc_cacheserver.contract.models import ContractDeployInfo
from btc_cacheserver.blockchain import defines, decode_base


contract_bin_map_name = {}
for _contract_name in defines.contract_names:
    with open(base.get_compile_path(_contract_name), "r") as fo:
        compile_json = json.loads(fo.read())
    contract_bin_map_name[compile_json["bin"][:257]] = _contract_name

contract_addresses_map_names = {
    settings.CONTROLLER_ROUTE_ADDRESS: ContractNames.CONTROLLER_ROUTE,
    settings.INTERFACE_ADDRESS: ContractNames.INTERFACE,
    settings.LOAN_CONTRACT_ROUTE_ADDRESS: ContractNames.LOAN_CONTRACT_ROUTE,
    settings.USER_LOAN_STORE_ROUTE_ADDRESS: ContractNames.USER_LOAN_STORE_ROUTE,
}


Log = logging.getLogger("scripts")

w3 = base.create_web3_instance(100000)
block_filter = w3.eth.filter('latest')


class CheckFilterConsumer(BaseConsumer):

    method_mapping = {
        "check_filter": "check_block_filter",
    }

    def check_block_filter(self, message, **kwargs):
        Log.info("before, is filter running: %s ", block_filter.running)
        if not block_filter.running:
            block_filter.watch(new_block_callback)
        Log.info("after, is filter running: %s ", block_filter.running)


def get_channel_group(group_identifier):
    return Group("chain_group_%s" % group_identifier)


def create_deploy_tx_response(tx_data):
    tx_type = defines.TransactionTypes.DEPLOY_TX

    contract_name = contract_bin_map_name.get(tx_data.input[2:259], "")
    msg_kwargs = {
        "who": tx_data["from"][:10],
        "contract": defines.map_contract_show_names.get(contract_name, u"合约"),
    }
    msg = defines.map_tx_types_to_template.get(tx_type, "").format(**msg_kwargs)
    # print("deploy contract msg: ", msg)

    return  {
            "tx_hash": tx_data["hash"],
            "from": tx_data['from'],
            "to": tx_data['to'],
            "type": defines.map_tx_types_to_show_names.get(tx_type, ""),
            "fee": tx_data["value"],
            "info": msg,
            "method": tx_type,
    }


def create_transfer_tx_response(tx_data):

    tx_type = defines.TransactionTypes.TRANSFER
    tx_value = tx_data["value"]

    msg_kwargs = {
        "trans_from": tx_data["from"][:10],
        "trans_to": tx_data["to"][:10],
        "trans_value": tx_value,
    }
    msg = defines.map_tx_types_to_template.get(tx_type, "").format(**msg_kwargs)
    # print("transfer msg: ", msg)

    return {
            "tx_hash": tx_data["hash"],
            "from": tx_data['from'],
            "to": tx_data['to'],
            "type": defines.map_tx_types_to_show_names.get(tx_type, ""),
            "fee": tx_value,
            "info": msg,
            "method": tx_type, 
    }


def create_contract_tx_msg(contract_name, tx_data, tx_type, args):
    _types_def = defines.TransactionTypes

    if tx_type == _types_def.PAUSE:
        msg_kwargs = {
            "who": tx_data["from"][:10],
            "contract": defines.map_contract_show_names.get(contract_name, u"合约"),
        }

    elif tx_type == _types_def.UNPAUSE:
        msg_kwargs = {
            "who": tx_data["from"][:10],
            "contract": defines.map_contract_show_names.get(contract_name, u"合约"),
        }

    elif tx_type == _types_def.ADMIN_ADD_ROLE:
        msg_kwargs = {
            "who": tx_data["from"][:10],
            "contract": defines.map_contract_show_names.get(contract_name, u"合约"),
        }

    elif tx_type == _types_def.ADMIN_REMOVE_ROLE:
        msg_kwargs = {
            "who": tx_data["from"][:10],
            "contract": defines.map_contract_show_names.get(contract_name, u"合约"),
        }

    elif tx_type == _types_def.SET_ADDRESS:
        msg_kwargs = {
            "who": tx_data["from"][:10],
            "contract": defines.map_contract_show_names.get(contract_name, u"合约"),
        }

    elif tx_type == _types_def.SET_CURRENT_VERSION:
        msg_kwargs = {
            "who": tx_data["from"][:10],
            "contract": defines.map_contract_show_names.get(contract_name, u"合约"),
        }
    elif tx_type == _types_def.UPDATE_LOAN:
        msg_kwargs = {
            "who": tx_data["from"][:10],
        }

    elif tx_type == _types_def.UPDATE_EXPENDITURE:
        msg_kwargs = {
            "who": tx_data["from"][:10],
        }

    elif tx_type == _types_def.UPDATE_INSTALLMENT:
        msg_kwargs = {
            "who": tx_data["from"][:10],
        }

    elif tx_type == _types_def.UPDATE_REPAYMENT:
        msg_kwargs = {
            "who": tx_data["from"][:10],
        }

    elif tx_type == _types_def.SET_CONTROLLER_ROUTE:
        msg_kwargs = {
            "who": tx_data["from"][:10],
            "contract": defines.map_contract_show_names.get(contract_name, u"合约"),
        }

    elif tx_type == _types_def.SET_LOAN_CONTRACT_ROUTE:
        msg_kwargs = {
            "who": tx_data["from"][:10],
            "contract": defines.map_contract_show_names.get(contract_name, u"合约"),
        }

    elif tx_type == _types_def.SET_USER_LOAN_STORE_ROUTE:
        msg_kwargs = {
            "who": tx_data["from"][:10],
            "contract": defines.map_contract_show_names.get(contract_name, u"合约"),
        }
    
    return defines.map_tx_types_to_template.get(tx_type, "").format(**msg_kwargs)


def create_contract_tx_response(tx_data):

    contract_name = contract_addresses_map_names.get(tx_data.to)
    if not contract_name:
        record = ContractDeployInfo.objects.filter(address=tx_data.to)
        if not record:
            Log.warn("*!*!*unresolved contract address*!*!*")
            return
        else:
            contract_name = record[0].name

    tx_type, args = decode_base.decode_input(tx_data.input, contract_name)
    # print(contract_name, tx_type)

    msg = create_contract_tx_msg(contract_name, tx_data, tx_type, args)

    return {
            "tx_hash": tx_data["hash"],
            "from": tx_data['from'],
            "to": tx_data['to'],
            "type": defines.map_tx_types_to_show_names.get(tx_type, ""),
            "fee": tx_data["value"],
            "info": msg,
            "method": tx_type,
    }


def push_transaction_info(tx_data, timestamp, group_identifier=defines.CHANNEL_GROUP_MAIN):
    
    if tx_data.to is None:
        rsp_info = create_deploy_tx_response(tx_data)

    elif tx_data["value"]:
        rsp_info = create_transfer_tx_response(tx_data)

    else:
        rsp_info = create_contract_tx_response(tx_data)

    if not rsp_info:
        return 

    rsp_info["identifier"] = "txinfo"
    rsp_info["time"] = timestamp
    rsp_info["sort"] = tx_data.blockNumber * 1000 + tx_data.transactionIndex

    json_data = json.dumps(rsp_info)

    if group_identifier == defines.CHANNEL_GROUP_MAIN:
        get_channel_group(defines.CHANNEL_GROUP_MAIN).send({"text": json_data, })
        get_channel_group(tx_data["from"]).send({"text": json_data, })

    elif group_identifier == tx_data["from"]:
        get_channel_group(tx_data["from"]).send({"text": json_data, })


def push_block_info(block_identifier, bool_push_tx=True, group_identifier=defines.CHANNEL_GROUP_MAIN):
    block_info = w3.eth.getBlock(block_identifier, full_transactions=True)
    transactions = block_info["transactions"]
    timestamp = block_info["timestamp"]
    tx_count = len(transactions)

    if defines.CHANNEL_GROUP_MAIN == group_identifier:
        data = {
                "blocknumber": block_info['number'],
                "miner": block_info['miner'],
                "time": timestamp,
                "tx_count": tx_count,
                "identifier": "blockinfo",
                "method": "blockCreate",
                "sort": block_info["number"] ,
        }
        json_data = json.dumps(data)
        get_channel_group(defines.CHANNEL_GROUP_MAIN).send({"text": json_data, })

    if not bool_push_tx:
        return tx_count

    for tx_data in transactions:
        push_transaction_info(tx_data, timestamp, group_identifier)

    return tx_count


def new_block_callback(block_hash):
    Log.info("on block create!")

    push_block_info(block_hash)

    if not block_filter.running:
        block_filter.watch(new_block_callback)


@channel_session
def ws_connect_v2(message, account=None):

    message.reply_channel.send({"accept": True})
    
    group_identifier = "0x" + account if account is not None else defines.CHANNEL_GROUP_MAIN
    message.channel_session["group_identifier"] = group_identifier
    get_channel_group(group_identifier).add(message.reply_channel)

    Log.info("ws connected to group(%s)!", group_identifier)

    if not block_filter.running:
        block_filter.watch(new_block_callback)


@channel_session
def ws_receive_v2(message, account=None):

    group_identifier = message.channel_session["group_identifier"]
    msg_info = message.content
    Log.info("group(%s) received ws content: %s", group_identifier, msg_info)

    data = json.loads(msg_info.get("text", ""))
    msg_type = data.get("type")
    if not msg_type:
        return

    if msg_type == "change_group":
        group_to = data.get("to", defines.CHANNEL_GROUP_MAIN)

        get_channel_group(group_identifier).discard(message.reply_channel)
        get_channel_group(group_to).add(message.reply_channel)

        message.channel_session["group_identifier"] = group_to

        Log.info("group changed from %s to %s!", group_identifier, group_to)

    elif msg_type == "preblock":
        Log.info("preblock!!")
        current_block_number = w3.eth.blockNumber
        pre_count = data.get("count", 10)
        pushed_tx_count = 0
        for i in range(pre_count):
            bool_push_tx = True if pushed_tx_count  < 10 else False
            pushed_tx_count += push_block_info(current_block_number - i, bool_push_tx, group_identifier=group_identifier)

    if not block_filter.running:
        block_filter.watch(new_block_callback)


@channel_session
def ws_disconnect_v2(message, account=None):

    group_identifier = message.channel_session["group_identifier"]
    get_channel_group(group_identifier).discard(message.reply_channel)

    Log.info("ws disconnected from group(%s)!", group_identifier)

