#!/usr/bin/env python
#-*- coding: utf-8 -*-

import json
import logging
#import user

import sha3

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.db.models import Q
from django.conf import settings

from btc_cacheserver.contract.models import User, PlatFormInfo, LoanInformation, RepaymentInfo, InstallmentInfo
from btc_cacheserver.util import common
from btc_cacheserver.defines import ContractNames, LoanMethods

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


def _get_installmentinfo_with_loan(user_contract, user_tag, l_index, ex_index, count):

    if count > 0:
        list_info = []
        for index in range(count):
            installment_infos = common.pure_get_exec(user_contract,
                                                     LoanMethods.GET_INSTALLMENT_BY_INDEX,
                                                     ContractNames.LOAN_CONTROLLER,
                                                     user_tag, l_index, ex_index,
                                                     index)
            data = {
                "installment_number": installment_infos[1],
                "repay_time": installment_infos[2],
                "repay_amount": installment_infos[3]
           }
            list_info.append(data)
        return json.dumps(list_info)
    else:
        return ""


def _create_user_tag(username, phone, id):
    user_tag = sha3.keccak_256()
    user_tag.update(username)
    user_tag.update(id)
    user_tag.update(phone)
    return user_tag.hexdigest()

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

                        loan_obj = LoanInformation.objects.create(platform=platform_obj,
                                                               order_number=order_number,
                                                               apply_amount=apply_amount,
                                                               exact_amount=exact_amount,
                                                               reason=reason,
                                                               apply_time=apply_time,
                                                               interest=interest,
                                                               bank_card=bank_card,
                                                               overdue_days=overdue_days)
                        repay_plans = loan.get("repay_plans", "")

                        if repay_plans:
                            plan_data = json.loads(repay_plans)
                            for plan in plan_data:
                                InstallmentInfo.objects.create(loan_info=loan_obj,
                                                               installment_number=plan.get("installment_number"),
                                                               repay_time=plan.get("repay_time"),
                                                               repay_amount=plan.get("repay_amount"))

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

                    RepaymentInfo.objects.create(
                        loan_info=loan_info,
                        installment_number=installment_number,
                        real_repay_time=real_repay_time,
                        overdue_days=overdue_days,
                        real_repay_amount=real_repay_amount,
                        repay_amount_type=repay_amount_type)

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
    username = request.GET.get('name', '')
    phone = request.GET.get('phone', '')
    id_no = request.GET.get('id', '')

    Log.info("id is {}".format(id_no))
    if not (username or phone or id_no):
        return JsonResponse({"code": -1, "msg": "error:phone is null."})

    try:
        user_tag = _create_user_tag(username, phone, id_no)
        contract = common.get_contract_instance(settings.INTERFACE_ADDRESS,
                                                common.get_abi_path(ContractNames.INTERFACE))
        user_data = {
                "username": username,
                "phone_no": phone,
                "id_no": id_no,
            }

        platform_count = common.pure_get_exec(contract, LoanMethods.GET_LOAN_TIMES,
                                              ContractNames.LOAN_CONTROLLER, user_tag)
        list_platform = list()

        for loan_index in range(platform_count):
            loaninfos = common.pure_get_exec(contract, LoanMethods.GET_LOAN_BY_INDEX,
                                             ContractNames.LOAN_CONTROLLER,
                                             user_tag, loan_index)
            dt_platform = {
                "platform": loaninfos[1],
                "ceiling": loaninfos[3],
            }
            loan_count = loaninfos[2]
            list_loaninfo = list()

            for expend_index in range(loan_count):
                expendinfos = common.pure_get_exec(contract,
                                                   LoanMethods.GET_EXPEND_BY_INDEX,
                                                   ContractNames.LOAN_CONTROLLER,
                                                   user_tag, loan_index,
                                                   expend_index)
                installment_count = expendinfos[4]
                repayment_count = expendinfos[5]
                repay_plans = _get_installmentinfo_with_loan(contract,
                                                             user_tag,
                                                             loan_index,
                                                             expend_index,
                                                             installment_count)
                dt_loan = {
                    "order_number": expendinfos[0],
                    "apply_amount": expendinfos[7],
                    "exact_amount": expendinfos[8],
                    "reason": expendinfos[3],
                    "apply_time": expendinfos[9],
                    "interest": expendinfos[10],
                    "bank_card": expendinfos[2],
                    "overdue_days": expendinfos[6],
                    "repay_plans": repay_plans
                }

                list_repayment = list()

                for repay_index in range(repayment_count):
                    repaymentinfos = common.pure_get_exec(contract,
                                                          LoanMethods.GET_REPAYMENT_BY_INDEX,
                                                          ContractNames.LOAN_CONTROLLER,
                                                          user_tag, loan_index,
                                                          expend_index)
                    dt_repayment = {
                        "installment_number": expendinfos[0],
                        "real_repay_time": repaymentinfos[5],
                        "overdue_days": repaymentinfos[2],
                        "real_repay_amount": repaymentinfos[4],
                        "repay_amount_type": repaymentinfos[3]
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

