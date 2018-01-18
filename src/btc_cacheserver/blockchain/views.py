from django.shortcuts import render

import json
import logging
import time

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from web3 import Web3, RPCProvider

from btc_cacheserver import settings
from btc_cacheserver.blockchain.models import BlockNumberRecording

Log = logging.getLogger("scripts")
provider = RPCProvider(host=settings.BLOCKCHAIN_RPC_HOST, port=settings.BLOCKCHAIN_RPC_PORT)
w3 = Web3(provider)


@require_http_methods(['GET'])
@csrf_exempt
def get_block_detail_info(request, number):
    if not str(number).isdigit():
        Log.warn("block number is error.")
        return JsonResponse({"msg": "block number is error.", "code": -1})

    try:
        block_info = w3.eth.getBlock(int(number))
        transactions = block_info.transactions

        trans_info = []
        for tx_hash in transactions:
            transaction = w3.eth.getTransaction(tx_hash)
            tx_data = {
                "tx_hash": transaction.hash,
                "type": "",
                "from": transaction["from"],
                "to": transaction.to,
                "value": transaction.value
            }
            trans_info.append(tx_data)

        data = {"msg": "",
                "code": 0,
                "blockchain": {
                    "hash": block_info.hash,
                    "difficulty": block_info.difficulty,
                    "miner": block_info.miner,
                    "tx_count": len(block_info.transactions),
                    "gas_limit": block_info.gasLimit,
                    "gas_used": block_info.gasUsed,
                    "time": time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(block_info.timestamp)),
                    "size": block_info.size,
                    "extra_data": block_info.extraData,
                    "transactions": trans_info
                    }
                }
        return JsonResponse(data)

    except Exception as err:
        Log.error(str(err), exc_info=True)
        return JsonResponse({
            'code': -1,
            'msg': str(err)
        })


@require_http_methods(['GET'])
@csrf_exempt
def get_transaction_detail_info(request, txhash):
    if not txhash:
        Log.warn("Transaction hash is error.")
        return JsonResponse({"msg": "Transaction hash is error.", "code": -1})

    try:
        _txhash = "0x" + txhash
        transaction_info = w3.eth.getTransaction(_txhash)
        transaction_receipt = w3.eth.getTransactionReceipt(_txhash)
        block_info = w3.eth.getBlock(transaction_info.blockNumber)

        data = {"msg": "",
                "code": 0,
                "transactions": {
                    "hash": transaction_info.hash,
                    "block_number": transaction_info.blockNumber,
                    "time": time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(block_info.timestamp)),
                    "from": transaction_info["from"],
                    "to": transaction_info.to,
                    "value": transaction_info.value,
                    "gas_limit": block_info.gasLimit,
                    "gas_used": transaction_receipt.gasUsed
                    }
                }

        return JsonResponse(data)

    except Exception as err:
        Log.error(str(err), exc_info=True)
        return JsonResponse({
            'code': -1,
            'msg': str(err)
        })


@require_http_methods(['GET'])
@csrf_exempt
def get_blocknumber_recording(request):
    phone_no = request.GET.get('start_time', '')
    id_no = request.GET.get('end_time', '')

    if phone_no and id_no:
        pass

    try:
        block_recording = BlockNumberRecording.objects.all()

        number_list = [block.blocknumber for block in block_recording]
        time_list = [block.time for block in block_recording]

        data = {
            "msg": "",
            "code": 0,
            "blockchain": {
                "blocknumber": number_list,
                "time": time_list
            }
        }

        return JsonResponse(data)
    except Exception as err:
        Log.error(str(err), exc_info=True)
        return JsonResponse({
            'code': -1,
            'msg': str(err)
        })
