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
    contract = models.CharField(max_length=66, blank=True, null=True, help_text="合约地址")
    loan_counter = models.IntegerField(default=0, help_text="借贷次数")
    latest_update = models.BigIntegerField(default=0, help_text="最后更新时间戳")

    class Meta:
        db_table = u'users'

    def __unicode__(self):
        return u'%d)%s' % (self.id, self.username)


#平台信息
class PlatFormInfo(models.Model):
    platform = models.CharField(max_length=64, help_text="所属平台")
    credit_ceiling = models.IntegerField(default=0, help_text="授信额度")
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    expend_counter = models.IntegerField(default=0, help_text="支用次数")
    tag = models.BinaryField(max_length=66,blank=True, null=True, help_text="区块链中的唯一标识")

    class Meta:
        db_table = u'platforminfo'

class LoanInformation(models.Model):
    platform = models.ForeignKey(PlatFormInfo, on_delete=models.CASCADE)
    order_number = models.CharField(max_length=255, help_text='订单号')
    apply_amount = models.IntegerField(default=0, help_text='申请金额')
    exact_amount = models.IntegerField(default=0, help_text='实际打款金额')
    reason = models.CharField(max_length=255, default="", help_text='用途')
    apply_time = models.DateTimeField(help_text='申请时间', blank=True, null=True)
    interest = models.IntegerField(default=0, help_text='利率')
    bank_card = models.CharField(max_length=64, help_text='此次交易所属的银行卡', null=True, blank=True)
    overdue_days = models.IntegerField(default=0, help_text='当前逾期天数')
    tag = models.BinaryField(max_length=66,blank=True, null=True, help_text="区块链中的唯一标识")
    installment_counter = models.IntegerField(default=0, help_text="分期数")
    repayment_counter = models.IntegerField(default=0, help_text="还款次数")

    class Meta:
        db_table = u'loaninformation'

class InstallmentInfo(models.Model):
    loan_info = models.ForeignKey(LoanInformation, on_delete=models.CASCADE)
    installment_number = models.IntegerField(blank=True)
    repay_time = models.DateTimeField(blank=True, help_text="应还时间")
    repay_amount = models.IntegerField(default=0, help_text="应还金额")
    tag = models.BinaryField(max_length=66,blank=True, null=True, help_text="区块链中的唯一标识")
    class Meta:
        db_table = u'installmentinfo'

class RepaymentInfo(models.Model):
    repay_amount_type_t = (
        (0, "部分还款"),
        (1, "期款"),
        (2, "提前结清"),
    )
    loan_info = models.ForeignKey(LoanInformation, on_delete=models.CASCADE)
    installment_number = models.IntegerField(blank=True, null=True)
    real_repay_time = models.DateTimeField(blank=True, null=True, help_text="还款时间")
    overdue_days = models.IntegerField(default=0, help_text='当前逾期天数')
    real_repay_amount = models.IntegerField(default=0, help_text="实际还款金额")
    repay_amount_type = models.IntegerField(choices=repay_amount_type_t, help_text='还款类型', blank=True)
    tag = models.BinaryField(max_length=66,blank=True, null=True, help_text="区块链中的唯一标识")

    class Meta:
        db_table = u'repaymentinfo'


class TransactionInfo(models.Model):
    cumulativeGasUsed = models.IntegerField(default=0, help_text="累计gas消耗")
    gasUsed = models.IntegerField(default=0, help_text="gas消耗")
    blockNumber = models.IntegerField(default=-1, help_text="区块号")
    transactionIndex = models.IntegerField(default=-1, help_text="区块号")
    call_from = models.CharField(max_length=64, help_text='合约调用account')
    call_to = models.CharField(max_length=64, help_text='合约地址')
    transactionHash = models.CharField(max_length=70, help_text='交易的hash')
    types = models.CharField(max_length=32, help_text='此次交易所更改的数据类型')
    user = models.ForeignKey(User, blank=True, null=True, on_delete=models.SET_NULL)
    loan = models.ForeignKey(LoanInformation, blank=True, null=True, on_delete=models.SET_NULL)
    platform = models.ForeignKey(PlatFormInfo, blank=True, null=True, on_delete=models.SET_NULL)
    repayment = models.ForeignKey(RepaymentInfo, blank=True, null=True, on_delete=models.SET_NULL)
    installment = models.ForeignKey(InstallmentInfo, blank=True, null=True, on_delete=models.SET_NULL)

    class Meta:
        db_table = u'transactioninfo'
