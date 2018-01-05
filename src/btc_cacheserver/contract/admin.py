#!/usr/bin/env python
#-*- coding: utf-8 -*-

from django.contrib import admin
from btc_cacheserver.contract import models


class UserAdmin(admin.ModelAdmin):
    list_display = ['username', 'phone_no', 'id_no']
    search_fields = ['username', 'phone_no', 'id_no']
    ordering = ['-id']


class PlatFormAdmin(admin.ModelAdmin):
    list_display = ["owner_username", "platform", "credit_ceiling"]
    search_fields = ['platform']
    ordering = ['-id']

    def owner_username(self, obj):
        return "{}".format(obj.owner.username)


class LoanInfoAdmin(admin.ModelAdmin):
    list_display = ["platform_name", "order_number", "apply_amount", "exact_amount", "reason", "apply_time", "interest", "bank_card", "overdue_days"]
    search_fields = ['order_number']
    ordering = ['-id']

    def platform_name(self, obj):
        return "{}".format(obj.platform.platform)


class RepaymentAdmin(admin.ModelAdmin):
    list_display = ["loan_info_id", "order_number", "installment_number", "real_repay_time", "overdue_days", "real_repay_amount", "repay_amount_type"]
    search_fields = ['order_number']
    ordering = ['-id']

    def loan_info_id(self, obj):
        return "{}".format(obj.loan_info.id)


admin.site.register(models.User, UserAdmin)
admin.site.register(models.PlatFormInfo, PlatFormAdmin)
admin.site.register(models.LoanInformation, LoanInfoAdmin)
admin.site.register(models.RepaymentInfo, RepaymentAdmin)

