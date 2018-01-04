#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
created by antimoth at 2018-01-02
"""

from django.db import models
from .user import User


class LoanInformation(models.Model):
    user = models.ForeignKey(User, help_text='贷款人')
    order_number = models.CharField(max_length=255, help_text='订单号')
    apply_amount = models.IntegerField(default=0, help_text='申请金额', blank=True,
                                       null=True)
    exact_amount = models.IntegerField(default=0, help_text='实际打款金额',
                                       blank=True, null=True)
    reason = models.CharField(max_length=255, blank=True, null=True,
                              help_text='用途')
    apply_time = models.DateTimeField(auto_now_add=True, help_text='申请时间',
                                      blank=True, null=True)
    interest = models.IntegerField(default=0, help_text='利率')
    bank_card = models.CharField(max_length=64, help_text='此次交易所属的银行卡',
                                 null=True, blank=True)
    overdue_days = models.IntegerField(default=0, help_text='当前逾期天数',
                                       blank=True)

    class Meta:
        db_table = u'loaninformation'


class RepaymentInfo(models.Model):
    repay_amount_type_t = (
        (0, "部分还款"),
        (1, "期款"),
        (2, "提前结清"),
    )
    loan_info = models.ForeignKey(LoanInformation)
    order_number = models.CharField(max_length=255, help_text='订单号')
    installment_number = models.IntegerField(blank=True, null=True)
    real_repay_time = models.DateTimeField(blank=True, null=True, help_text="还款时间")

    overdue_days = models.IntegerField(default=0, help_text='当前逾期天数',
                                       blank=True)
    real_repay_amount = models.IntegerField(default=0, help_text="实际还款金额",
                                            blank=True, null=True)
    repay_amount_type = models.IntegerField(choices=repay_amount_type_t, help_text='还款类型', blank=True)
    repay_plans = models.CharField(max_length=255, help_text="还款计划")

    class Meta:
        db_table = u'repaymentinfo'


