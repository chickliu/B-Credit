#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
created by antimoth at 2018-01-02
"""


from django.db import models


# 用户信息
class User(models.Model):
    register_type_t = {
        (-2, u'注销资料'),
        (-1, u'已注销'),
        (0, u'已注册'),
        (1, u'未激活'),
    }

    username = models.CharField(max_length=64, null=True, help_text="用户姓名")
    password = models.CharField(max_length=64, help_text='登录密码')
    phone_no = models.CharField(max_length=20, help_text="用户电话")
    id_no = models.CharField(max_length=20, blank=True, null=True, help_text="身份证号")
    channel = models.CharField(max_length=255, blank=True, null=True, help_text="渠道来源")
    sub_channel = models.ForeignKey("SubChannel", blank=True, null=True, help_text="二级渠道来源")
    #payment_password = models.CharField(max_length=64, blank=True, null=True, help_text='支付密码')
    create_time = models.DateTimeField(auto_now_add=True, help_text="注册时间")

    #device_name = models.CharField(max_length=255, blank=True, null=True, help_text="设备名称")
    wechat_openid = models.CharField(max_length=255, blank=True, null=True, default="", help_text="微信id")
    bind_wechat_time = models.DateTimeField(blank=True, null=True, auto_now_add = False, help_text="微信绑定时间")

    #last_contract_id = models.CharField(max_length=255, blank=True, null=True)
    device_id = models.BigIntegerField(max_length=20, blank=True, null=True)

    invitation = models.ForeignKey("self", blank=True, null=True)

    imei = models.CharField(max_length=64, blank=True, null=True, help_text="imei")
    imsi = models.CharField(max_length=64, blank=True, null=True, help_text="imsi")
    #android_id = models.CharField(max_length=64, blank=True, null=True, help_text="安卓id")
    local_phone_no = models.CharField(max_length=20, blank=True, null=True, help_text="本机号码")

    submit_modules_state = models.CharField(max_length=256, default="")
    is_closed = models.IntegerField(blank=True, null=True)
    which_step = models.IntegerField(blank=True, null=True)
    first_step_module = models.IntegerField(blank=True, null=True)
    device_token = models.CharField(max_length=128, blank=True)
    market_score = models.IntegerField(blank = True, null=True, default=0)
    is_report_location = models.SmallIntegerField(blank = True, null=True, default=0)
    platform = models.CharField(max_length = 64, blank = True, null = True, help_text = "所属平台")
    credit_ceiling = models.IntegerField(default = 0, blank = True, null = True, help_text = "授信额度")
    current_credit_loan = models.IntegerField(default = 0, blank = True, null = True, help_text = '当前已使用额度')
    reviewed_at = models.DateTimeField(auto_now=True, blank = True, null = True)
    failed_reason = models.CharField(max_length=64, default = '', blank = True, null = True)
    #sub_channel = models.ForeignKey(Subchannel, blank=True, null=True)
    loop_money = models.IntegerField(u'循环金额', default=0, blank = True, null = True)
    is_deleted = models.IntegerField(u'是否注销', default=0, choices=((0, u'未注销'), (1, '已注销')), blank = True, null = True)
    should_repay_day = models.IntegerField(default=0, help_text="到款日", blank = True, null = True)
    trlc_username = models.CharField(max_length = 64, default = '', blank = True, null = True)
    bi_count = models.IntegerField(default = 0, blank = True, null = True)
    tl_user_id = models.CharField(max_length = 256, default = '', blank = True, null = True)

    class Meta:
        db_table = u'users'
        ordering = ['-id']

    def __unicode__(self):
        return u'%d)%s'%(self.id,self.username)

    def get_status(self):
        return ""

