#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
created by antimoth at 2018-01-02
"""

from django.db import models


# 用户信息
class User(models.Model):
    loan_counter  = models.IntegerField(default=0, blank=True, help_text="借贷次数")
    latest_update = models.BigIntegerField(default=0, blank=True, help_text="最后更新时间戳")

    phone_no      = models.CharField(max_length=32, blank=True, null=True, help_text="用户电话")
    id_no         = models.CharField(max_length=32, blank=True, null=True, help_text="身份证号")
    username      = models.CharField(max_length=64, blank=True, null=True, help_text="用户姓名")
    tag           = models.CharField(max_length=64, unique=True, help_text="区块链中的唯一标识")

    class Meta:
        db_table = u'users'

    def __unicode__(self):
        return u'%d)%s' % (self.id, self.username)


#平台信息
class LoanInfo(models.Model):
    owner          = models.ForeignKey(User, on_delete=models.CASCADE)

    credit_ceiling = models.IntegerField(default=0, help_text="授信额度")
    expend_counter = models.IntegerField(default=0, blank=True, help_text="支用次数")

    platform       = models.CharField(max_length=32, help_text="所属平台")
    creator        = models.CharField(max_length=64, blank=True, null=True, help_text='创建记录的account')
    tag            = models.CharField(max_length=64, unique=True, help_text="区块链中的唯一标识")

    class Meta:
        db_table = u'loaninfo'

class ExpendInfo(models.Model):
    loaninfo           = models.ForeignKey(LoanInfo, on_delete=models.CASCADE)

    apply_amount        = models.IntegerField(default=0, help_text='申请金额')
    exact_amount        = models.IntegerField(default=0, help_text='实际打款金额')
    interest            = models.IntegerField(default=0, help_text='利率')
    overdue_days        = models.IntegerField(default=0, help_text='当前逾期天数')
    installment_counter = models.IntegerField(default=0, blank=True, help_text="分期数")
    repayment_counter   = models.IntegerField(default=0, blank=True, help_text="还款次数")

    apply_time          = models.DateTimeField(help_text='申请时间')

    order_number        = models.CharField(max_length=32, help_text='订单号')
    reason              = models.CharField(max_length=32, default="", help_text='用途')
    bank_card           = models.CharField(max_length=32, default="", help_text='此次交易所属的银行卡')
    creator             = models.CharField(max_length=64, blank=True, null=True, help_text='创建记录的account')
    tag                 = models.CharField(max_length=64, unique=True, help_text="区块链中的唯一标识")

    class Meta:
        db_table = u'expendinfo'

class InstallmentInfo(models.Model):
    expendinfo        = models.ForeignKey(ExpendInfo, on_delete=models.CASCADE)

    installment_number = models.IntegerField(default=0, blank=True)
    repay_amount       = models.IntegerField(default=0, help_text="应还金额")

    repay_time         = models.DateTimeField(help_text="应还时间")

    creator            = models.CharField(max_length=64, blank=True, null=True, help_text='创建记录的account')
    tag                = models.CharField(max_length=64, unique=True, help_text="区块链中的唯一标识")

    class Meta:
        db_table = u'installmentinfo'

class RepaymentInfo(models.Model):
    repay_amount_type_t = (
        (0, "部分还款"),
        (1, "期款"),
        (2, "提前结清"),
    )
    expendinfo        = models.ForeignKey(ExpendInfo, on_delete=models.CASCADE)

    installment_number = models.IntegerField(blank=True, null=True)
    overdue_days       = models.IntegerField(default=0, help_text='当前逾期天数')
    real_repay_amount  = models.IntegerField(default=0, help_text="实际还款金额")
    repay_amount_type  = models.IntegerField(choices=repay_amount_type_t, help_text='还款类型', blank=True)

    real_repay_time    = models.DateTimeField(blank=True, null=True, help_text="还款时间")

    creator            = models.CharField(max_length=64, blank=True, null=True, help_text='创建记录的account')
    tag                = models.CharField(max_length=64, unique=True, help_text="区块链中的唯一标识")

    class Meta:
        db_table = u'repaymentinfo'


class TransactionInfo(models.Model):
    loan              = models.ForeignKey(LoanInfo, blank=True, null=True, on_delete=models.SET_NULL)
    expend            = models.ForeignKey(ExpendInfo, blank=True, null=True, on_delete=models.SET_NULL)
    repayment         = models.ForeignKey(RepaymentInfo, blank=True, null=True, on_delete=models.SET_NULL)
    installment       = models.ForeignKey(InstallmentInfo, blank=True, null=True, on_delete=models.SET_NULL)

    method            = models.CharField(max_length=64, blank=True, default="", help_text='合约函数名')
    transactionHash   = models.CharField(max_length=128, unique=True, help_text='交易的hash')

    class Meta:
        db_table = u'transactioninfo'

class ContractDeployInfo(models.Model):
    address = models.CharField(max_length=64, unique=True, help_text="合约地址")
    name    = models.CharField(max_length=64, default="",  help_text="合约名称")
    tx      = models.CharField(max_length=128, unique=True, help_text="交易hash")

    class Meta:
        db_table = u'deployinfo'


