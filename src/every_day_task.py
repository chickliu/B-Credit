#!/usr/bin/env python
#-*- coding: utf-8 -*-

import logging
import time
from web3 import Web3, RPCProvider

from btc_cacheserver import settings
from btc_cacheserver.blockchain.models import BlockNumberRecording


Log = logging.getLogger("scripts")
provider = RPCProvider(host=settings.BLOCKCHAIN_RPC_HOST, port=settings.BLOCKCHAIN_RPC_PORT)
w3 = Web3(provider)


def add_blocknumber():
    try:
        blocknumber = w3.eth.blockNumber
        now = time.strftime("%Y-%m-%d", time.localtime())

        BlockNumberRecording.objects.create(blocknumber=blocknumber, time=now)
    except Exception as err:
        Log.error(str(err), exc_info=True)


if __name__ == '__main__':
    add_blocknumber()
