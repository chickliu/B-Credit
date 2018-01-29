#!/usr/bin/env python
#-*- coding: utf-8 -*-

import logging
import time
import base
from web3 import Web3, RPCProvider

from btc_cacheserver.blockchain.models import BlockNumberRecording


Log = logging.getLogger("scripts")
w3 = base.create_web3_instance()


def add_blocknumber():
    try:
        blocknumber = w3.eth.blockNumber
        now = time.strftime("%Y-%m-%d", time.localtime())

        BlockNumberRecording.objects.create(blocknumber=blocknumber, time=now)
    except Exception as err:
        Log.error(str(err), exc_info=True)


if __name__ == '__main__':
    add_blocknumber()
