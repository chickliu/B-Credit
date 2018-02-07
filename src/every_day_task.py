#!/usr/bin/env python
#-*- coding: utf-8 -*-

import logging
import pytz
import base

from datetime import datetime

from btc_cacheserver.blockchain.models import BlockNumberRecording

Log = logging.getLogger("scripts")
w3 = base.create_web3_instance()


def add_blocknumber():
    try:
        blocknumber = w3.eth.blockNumber

        utc_tz = pytz.timezone("UTC")
        now = utc_tz.localize(datetime.strptime(datetime.utcnow().strftime("%Y%m%d%H"), "%Y%m%d%H"))

        exists = BlockNumberRecording.objects.filter(time=now)
        if not exists:
            BlockNumberRecording.objects.create(blocknumber=blocknumber, time=now)
        else:
            _record = exists[0]
            _record.blocknumber = blocknumber
            _record.save()
        Log.info("daily record block_number(%s) at %s", blocknumber, now)
    except Exception as err:
        Log.error(str(err), exc_info=True)


if __name__ == '__main__':
    add_blocknumber()
