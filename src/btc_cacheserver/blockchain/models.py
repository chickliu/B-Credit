#!/usr/bin/env python
# -*- coding: utf-8 -*-

from django.db import models


class BlockNumberRecording(models.Model):
    blocknumber = models.IntegerField(default=0, help_text="区块数量")
    time = models.DateTimeField(help_text='记录时间', blank=True, null=True)

    class Meta:
        db_table = u'blocknumberrecording'
