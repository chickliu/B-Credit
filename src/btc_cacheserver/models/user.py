#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
created by antimoth at 2018-01-02
"""


from django.db import models


# 用户信息
class User(models.Model):
    username = models.CharField(max_length=64, null=True, help_text="用户姓名")
    phone_no = models.CharField(max_length=20, help_text="用户电话")
    id_no = models.CharField(max_length=20, blank=True, null=True, help_text="身份证号")

    class Meta:
        db_table = u'users'

    def __unicode__(self):
        return u'%d)%s' % (self.id, self.username)


#平台信息
class PlatFormInfo(models.Model):
    platform = models.CharField(max_length=64, help_text="所属平台")
    credit_ceiling = models.IntegerField(default=0, help_text="授信额度")
    owner = models.ForeignKey(User)

    class Meta:
        db_table = u'platforminfo'


