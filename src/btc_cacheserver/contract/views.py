#!/usr/bin/env python
#-*- coding: utf-8 -*-

import json
import logging

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.db.models import Q

from btc_cacheserver.contract.models import User, PlatFormInfo, LoanInformation, RepaymentInfo

Log = logging.getLogger("scripts")


def _check_model_data(d_model, query):
    qs = d_model.objects.filter(query)

    if qs.count() > 0:
        return qs.first()

    return None


def _save_user_and_platform_info(user):
    if not user:
        Log.warn("")
        return None
    else:
        name = user.get("username", "")
        phone = user.get("phone_no", "")
        id_num = user.get("id_no", "")
        user_obj = _check_model_data(User, Q(username=name,
                                             phone_no=phone,
                                             id_no=id_num))
        if not user_obj:
            user_obj = User.objects.create(username=name, phone_no=phone,
                                           id_no=id_num)

        platform = user.get("platform", "")
        ceiling = user.get("credit_ceiling", 0)
        platform_obj = _check_model_data(PlatFormInfo, Q(platform=platform,
                                                         owner=user_obj))

        if not platform_obj:
            platform_obj = PlatFormInfo.objects.create(platform=platform,
                                                       credit_ceiling=ceiling,
                                                       owner=user_obj)
        return platform_obj


@require_http_methods(['POST'])
@csrf_exempt
def update_load_data(request):
    msg_body = json.loads(request.body.decode("utf-8"))
    datas = msg_body.get("data", [])

    if len(datas) == 0:
        Log.warn("Missing data can not be updated.")
        return JsonResponse({
            'code': -1,
            'msg': "Missing data can not be updated.",
        })

    try:
        for data in datas:
            user = data.get("user")
            platform_obj = _save_user_and_platform_info(user)

            loan_datas = data.get("loans", [])

            if len(loan_datas) == 0:
                Log.warn("not loan data update.")
            else:
                for loan in loan_datas:
                    order_number = loan.get("order_number", "")
                    loan_id = _check_model_data(LoanInformation, Q(order_number=order_number,
                                                                   platform=platform_obj))

                    if not loan_id:
                        apply_amount = loan.get("apply_amount", 0)
                        exact_amount = loan.get("exact_amount", 0)
                        reason = loan.get("reason", "")
                        apply_time = loan.get("apply_time", "")
                        interest = loan.get("interest", 0)
                        bank_card = loan.get("bank_card", "")
                        overdue_days = loan.get("overdue_days", 0)

                        LoanInformation.objects.create(platform=platform_obj,
                                                       order_number=order_number,
                                                       apply_amount=apply_amount,
                                                       exact_amount=exact_amount,
                                                       reason=reason,
                                                       apply_time=apply_time,
                                                       interest=interest,
                                                       bank_card=bank_card,
                                                       overdue_days=overdue_days)

    except Exception as err:
        Log.error(str(err), exc_info=True)
        return JsonResponse({
            'code': -1,
            'msg': str(err)
        })

    return JsonResponse({"code": 0, "msg": "update loan data success."})


@require_http_methods(['POST'])
@csrf_exempt
def update_repayment_data(request):
    msg_body = json.loads(request.body.decode('utf-8'))
    datas = msg_body.get("data", [])

    if len(datas) == 0:
        Log.warn("Missing data can not be updated")
        return JsonResponse({
            'code': -1,
            'msg': "Missing data can not be updated"
        })

    try:
        for data in datas:
            user = data.get("user")
            _save_user_and_platform_info(user)

            repayments = data.get("repayments", [])

            if len(repayments) == 0:
                Log.warn("Not repayment update.")
            else:
                for repayment in repayments:
                    order_number = repayment.get("order_number", "")
                    loan_info = LoanInformation.objects.filter(order_number=order_number).first()
                    if not loan_info:
                        Log.warn("Order number is error,can't find loan information.")
                        continue
                    installment_number = repayment.get("installment_number", 0)
                    real_repay_time = repayment.get("real_repay_time", "")
                    overdue_days = repayment.get("overdue_days", 0)
                    real_repay_amount = repayment.get("real_repay_amount", 0)
                    repay_amount_type = repayment.get("repay_amount_type", 0)
                    repay_plans = repayment.get("repay_plans", "")

                    RepaymentInfo.objects.create(
                        loan_info=loan_info,
                        order_number=order_number,
                        installment_number=installment_number,
                        real_repay_time=real_repay_time,
                        overdue_days=overdue_days,
                        real_repay_amount=real_repay_amount,
                        repay_amount_type=repay_amount_type,
                        repay_plans=repay_plans)

    except Exception as err:
        Log.error(str(err), exc_info=True)
        return JsonResponse({
            'code': -1,
            'msg': str(err)
        })

    return JsonResponse({"code": 0, "msg": "update repayment success"})


@require_http_methods(['GET'])
@csrf_exempt
def get_user_data(request):
    phone_no = request.GET.get('phone', '')
    id_no = request.GET.get('id', '')

    Log.info("phone is {}, id is {}".format(phone_no, id_no))
    if not (phone_no or id_no):
        return JsonResponse({"code": -1, "msg": "error:phone or id is null."})

    try:
        user_obj = User.objects.filter(phone_no=phone_no, id_no=id_no)

        if not user_obj:
            return JsonResponse({"code": -1, "msg": "error:can't find user."})

        user = user_obj.first()
        user_data = {
                "username": user.username,
                "phone_no": user.phone_no,
                "id_no": user.id_no,
            }

        platforminfos = PlatFormInfo.objects.filter(owner=user)
        list_platform = list()
        for platform in platforminfos:
            dt_platform = {
                    "platform": platform.platform,
                    "ceiling": platform.credit_ceiling,
                }
            loaninfos = LoanInformation.objects.filter(platform=platform)

            list_loaninfo = list()
            for loan in loaninfos:
                dt_loan = {
                        "order_number": loan.order_number,
                        "apply_amount": loan.apply_amount,
                        "exact_amount": loan.exact_amount,
                        "reason": loan.reason,
                        "apply_time": loan.apply_time,
                        "interest":loan.interest,
                        "bank_card": loan.bank_card,
                        "overdue_days": loan.overdue_days,
                    }
                repaymentinfo = RepaymentInfo.objects.filter(loan_info=loan)
                list_repayment = list()
                for repayment in repaymentinfo:
                    dt_repayment = {
                        "installment_number": repayment.installment_number,
                        "real_repay_time": repayment.real_repay_time,
                        "overdue_days": repayment.overdue_days,
                        "real_repay_amount": repayment.real_repay_amount,
                        "repay_amount_type": repayment.repay_amount_type,
                        "repay_plans": repayment.repay_plans
                    }
                    list_repayment.append(dt_repayment)

                dt_loan["repayment_data"] = list_repayment
                list_loaninfo.append(dt_loan)

            dt_platform["loan_data"] = list_loaninfo
            list_platform.append(dt_platform)
        user_data["platform_data"] = list_platform
        return JsonResponse({'code': 0, "msg": user_data})
    except Exception as err:
        Log.error(str(err), exc_info=True)
        return JsonResponse({
            'code': -1,
            'msg': str(err)
        })








