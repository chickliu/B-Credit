#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
created by antimoth at 2018-01-02
"""

from django.db import models
from .user import User


class RepaymentInfo(models.Model):
    REJECT = -3
    DELETED = -2
    TO_BE_COMFIRMED = -1
    PAYING = 0
    REPAYING = 1
    OVERDUE = 2
    DONE = 3
    CHECKING = 4
    PAYED =5
    PASS = 6
    PRE_DONE = 7
    OVERDUE_DONE = 8
    RENEW = 10

    repay_status_type_t = (
        (-3, '拒绝'),
        (-2, '已删除'),
        (-1, '合同待确认'),
        (0, '放款中'),
        (1, '还款中'),
        (2, '逾期'),
        (3, '已完成'),
        (4, '复核中'),
        (5, '已放款'),
        (6, '审核通过'),
        #----后面两个状态仅供InstallmentDetailInfo.repay_status使用
        (7, '待还款'),
        (8, '逾期完成'),
        (9, '提前还款'),
        (10, '续期'),
    )

    strategy_type_t = (
        (1, u'28天一次性'),
        (2, u'21天一次性'),
        (3, u'14天一次性'),
        (4, u'7天一次性'),
        (5, u'28天分期'),
        (6, u'21天分期'),
        (7, u'14天分期'),
        (10, u'21天'),
        (11, u'28天'),
        (12, u'三个月'),
        (13, u'六个月'),
        (14, u'十二个月'),
        (15, u'学生三个月'),
        (19, u'12个月'),
        (20, u'24个月'),
        (21, u'36个月'),
    )

    capital_type_t = (
        (2, u'自有资金'),
    )

    class Meta:
        db_table = u'repaymentinfo'

    def __unicode__(self):
        return u'%d)%s %d %s'%(self.id, self.user.username, self.apply_amount/100, self.get_repay_status_display())

    order_number = models.CharField(max_length=255, help_text='订单号') #订单号，全局唯一
    repay_status = models.IntegerField(choices=repay_status_type_t, help_text='还款状态', blank = True, null = True)
    apply_amount = models.IntegerField(default=0, help_text='申请金额', blank = True, null = True)
    exact_amount = models.IntegerField(default=0, help_text='实际打款金额', blank = True, null = True)
    repay_amount = models.IntegerField(default=0, help_text='需还金额', blank = True, null = True)
    rest_amount = models.IntegerField(default=0, help_text='剩余未还金额', blank = True, null = True)
    user = models.ForeignKey(User, help_text='贷款人')
    capital_channel_id = models.IntegerField(choices=capital_type_t, help_text='资金渠道', blank = True)

    bank_card = models.CharField(max_length=64, help_text='此次交易所属的银行卡', null=True, blank=True)
    reason = models.CharField(max_length=255, blank=True, null=True, help_text='用途')
    apply_time = models.DateTimeField(auto_now_add=True, help_text='申请时间', blank = True, null = True)
    first_repay_day = models.DateTimeField(blank=True, null=True, help_text='打款日 (计息日)')
    next_repay_time = models.DateTimeField(blank=True, null=True, help_text='下次还款日')
    last_time_repay = models.DateTimeField(blank=True, null=True, help_text='最后一次还款日期')

    score = models.IntegerField(default=0, help_text='使用积分', blank = True)
    overdue_days = models.IntegerField(default=0, help_text='当前逾期天数', blank = True)
    overdue_days_total = models.IntegerField(default=0, help_text='总逾期天数', blank = True)

    platform = models.CharField(max_length = 64, blank = True)
    product = models.CharField(max_length = 64, blank = True)

    rest_principle = models.IntegerField(default=0, blank = True)
    balance = models.IntegerField(default=0, blank = True)
    last_calc_overdue_time = models.DateTimeField(blank=True, null=True)

    installment_count = models.IntegerField(default=0, help_text='总共多少期', blank = True, null = True)
    account_day = models.DateTimeField(auto_now_add=True, blank = True, null = True, help_text = '放款到账时间')
    pay_order_number = models.CharField(max_length = 64, null = True, blank = True, help_text = '支付平台放款流水号')
    repay_order_number = models.CharField(max_length = 64, null = True, blank = True, help_text = '支付平台扣款流水号')
    platform_fee = models.IntegerField(default = 0, blank = True, null = True, help_text='砍头息')

    def get_repayments_days(self):
        if self.strategy_id == 1 or self.strategy_id == 5:
            return 28
        elif self.strategy_id == 2 or self.strategy_id == 6:
            return 21
        elif self.strategy_id == 3 or self.strategy_id == 7:
            return 14
        elif self.strategy_id == 4:
            return 7
        else:
            return -1

    def get_repayments_instalments(self):
        if self.strategy_id >= 1 and self.strategy_id <= 4:
            return 1
        elif self.strategy_id == 5:
            return 4
        elif self.strategy_id == 6:
            return 3
        elif self.strategy_id == 7:
            return 2
        else:
            return -1

    def get_strategy_rate(self):
        if self.strategy_id >= 1 and self.strategy_id <= 4:
            return 0.27
        elif self.strategy_id >= 5 and self.strategy_id <= 7:
            return 0.24
        else:
            return -1


    def get_first_installments_amount(self):
        total = self.apply_amount
        return total - total / self.get_repayments_instalments() * (self.get_repayments_instalments() - 1)


class InstallmentDetailInfo(models.Model):

    repay_status_type_t = (
        (-3, u'拒绝'),
        (-2, u'已删除'),
        (-1, u'合同待确认'),
        (0, u'放款中'),
        (1, u'还款中'),
        (2, u'逾期'),
        (3, u'已完成'),
        (4, u'复核中'),
        (5, u'已放款'),
        (6, u'审核通过'),
        #---u-后面两个状态仅供InstallmentDetailInfo.repay_status使用
        (7, u'---'),
        (8, u'逾期完成'),
        (9, u'提前还款'),
        (10, u'续期'),
    )

    REPAY_TYPE_AUTO = 1
    REPAY_TYPE_ALIPAY = 3
    REPAY_TYPE_PUB = 4
    repay_channel_type_t = (
        (0, u'---'),
        (1, u'自动扣款'),
        (2, u'手动扣款'),
        (3, u'支付宝'),
        (4, u'对公还款'),
        (5, u'其他'),
    )

    repay_app_type_t = (
        (1, u'按时还款'),
        (2, u'催收m1'),
        (3, u'催收m2'),
        (4, u'催收m3'),
        (5, u'催收m4'),
        (6, u'催收m5'),
        (7, u'催收m5+')
    )

    class Meta:
        db_table = u'installmentdetailinfo'

    def __unicode__(self):
        #return u'%s)%d-%d '%(self.repayment.user.name, self.repayment, self.installment_number)
        return u'%d)%s: %d-%d '%(self.id, self.repayment.user.username, self.repayment.id, self.installment_number)

    repayment = models.ForeignKey(RepaymentInfo)                                   #所属的交易
    installment_number = models.IntegerField(blank = True, null = True)                                     #第几期
    order_number = models.CharField(max_length=255, help_text='订单号', blank = True, null = True)            #订单号，全局唯一
    should_repay_time = models.DateTimeField(blank = True, null = True)                           #应还日期
    real_repay_time = models.DateTimeField(blank=True, null=True)                  #实际还款日期
    should_repay_amount = models.IntegerField(help_text="期款", blank = True, null = True)        #期款 #应还金额(当前 用户看) = 本金 + 利息 + 服务费 + 银行手续费
    repay_overdue = models.IntegerField(default=0, help_text="罚金", blank = True, null = True)   #罚金 # 应还罚款 = 罚息 + 罚金
    real_repay_amount = models.IntegerField(default=0, help_text="实际还款金额", blank = True, null = True)   #实际还款金额
    reduction_amount = models.IntegerField(default=0, help_text="减免金额", blank = True, null = True)        #减免金额

    repay_status = models.IntegerField(choices=repay_status_type_t, blank = True, null = True)       #归还状态
    repay_channel = models.IntegerField(choices=repay_channel_type_t, default=0, blank = True, null = True)  #还款途径，比如1表示自助扣款，2表示XX方式还款
    repay_channel_description = models.CharField(max_length=255, default='', blank = True, null = True)   #还款途径描述: repay_channel = 其他 类型时使用

    repay_overdue = models.IntegerField(default=0, blank = True, null = True) # 应还罚款 = 罚息 + 罚金
    repay_principle = models.IntegerField(default=0, blank = True, null = True)  #应还本金
    repay_overdue_interest = models.IntegerField(blank = True, default=0)   # 应还罚息
    repay_penalty = models.IntegerField(blank = True, default=0) # 应还罚金
    repay_bank_fee = models.IntegerField(default=0, blank = True, null = True) #应还手续费 (银联)
    repay_interest = models.IntegerField(default=0, blank = True, null = True)#应还利息
    repay_fee = models.IntegerField(default=0, blank = True, null = True)#应还服务费
    overdue_days = models.IntegerField(default=0, blank = True)       # 当前逾期天数

    rest_principle = models.IntegerField(default=0, blank = True)
    ori_should_repay_amount = models.IntegerField(help_text="委案金额", default=0, blank = True, null = True)
    # 应还时间, 对应申请时间. 默认和should_repay_time 相同.
    ori_should_repay_time = models.DateTimeField(blank=True, null=True)
    real_time_should_repay_amount = models.IntegerField(help_text="应还金额(总)", default=0, blank = True, null = True) #应还金额(总) >= should_repay_amount +  repay_overdue
    update_at = models.DateTimeField(auto_now_add=True, blank = True, null = True)
    create_at = models.DateTimeField(auto_now=True, blank = True, null = True)

