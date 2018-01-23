from ethereum.abi import (
    decode_abi,
    normalize_name as normalize_abi_method_name,
    method_id as get_abi_method_id)
from ethereum.utils import encode_int, zpad, decode_hex
import os
from solc import compile_source
import json
from btc_cacheserver import settings

def decode_contract_call(contract_abi: list, call_data: str):
    call_data_bin = decode_hex(call_data)
    method_signature = call_data_bin[:4]
    for description in contract_abi:
        if description.get('type') != 'function':
            continue
        method_name = normalize_abi_method_name(description['name'])
        arg_types = [item['type'] for item in description['inputs']]
        method_id = get_abi_method_id(method_name, arg_types)
        if zpad(encode_int(method_id), 4) == method_signature:
            try:
                myargs = decode_abi(arg_types, call_data_bin[4:])
            except AssertionError:
                # Invalid args
                continue
            return method_name, myargs


def decode_input(str_input):
    with open(settings.INTERFACE_ABI_FILE, "r") as fo:
        compiled_sol = json.loads(fo.read())
    contract_interface = compiled_sol['<stdin>:UserMapsContract']
    method_name, args = decode_contract_call(contract_interface['abi'], str_input)
    return method_name, args

