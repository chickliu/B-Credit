#!/usr/bin/env python
# -*- coding: utf-8 


from web3 import Web3
from ethereum.abi import decode_abi, normalize_name as normalize_abi_method_name, method_id as get_abi_method_id
from ethereum.utils import encode_int, zpad, decode_hex

import base


def decode_contract_call(contract_abi, call_data):
    call_data_bin = decode_hex(call_data)
    method_signature = call_data_bin[:4]
    for description in contract_abi:
        if description.get('type') != 'function' or description.get('inputs') == []:
            continue
        method_name = normalize_abi_method_name(description['name'])
        arg_types = [item['type'] for item in description['inputs']]
        arg_names = [item['name'] for item in description['inputs']]
        method_id = get_abi_method_id(method_name, arg_types)
        if zpad(encode_int(method_id), 4) == method_signature:
            try:
                myargs = decode_abi(arg_types, call_data_bin[4:])
                encode_args = {}
                for arg_type, arg_name, arg in zip(arg_types, arg_names, myargs):
                    if arg_type == "address":
                        try:
                            arg = Web3.toText(arg).strip("\0")
                        except:
                            arg = Web3.toHex(arg).strip("\0")
                        arg = Web3.toChecksumAddress(arg)

                    elif arg_type == "bytes32" or arg_type == "string":
                        try:
                            arg = Web3.toText(arg).strip("\0")
                        except:
                            arg = Web3.toHex(arg).strip("\0")[2:]
                    encode_args[arg_name] = arg

            except AssertionError:
                # Invalid args
                continue
            return method_name, encode_args
    else:
        return "", {}


def decode_input(str_input, contract_name):
    if str_input[0:2]=="0x":
        str_input = str_input[2:]
    dict_abi = base.get_abi(contract_name)
    return decode_contract_call(dict_abi, str_input)
