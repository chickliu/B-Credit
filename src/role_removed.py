#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
created by antimoth at 2018-01-04
"""

import sys
import traceback

import base


if __name__ == '__main__':
    try:
        _role_dest_address = sys.argv[1]
        _dest_contract_name = sys.argv[2]
        _dest_contract_address = sys.argv[3]
        _role = sys.argv[4]
        tx_receipt = base.role_removed(_role_dest_address, _dest_contract_name, _dest_contract_address, _role)
        print(tx_receipt)
    except Exception as e:
        traceback.print_exc()
        print("Usage: python3 role_removed.py {_contract_address_to_remove_role} {role_contained_contract_name} {role_contained_contract_address} {role_string}")

