#!/usr/bin/env python
# -*- coding: utf-8 -*-

import time

from channels.asgi import get_channel_layer

import base

cl = get_channel_layer()
cl.send("check_filter", {"check_filter": 1})
time.sleep(300)
exit(1)
