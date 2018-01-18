import json
from django.test import TestCase, Client, RequestFactory
from socketIO_client import SocketIO

from btc_cacheserver.contract.models import User, PlatFormInfo, LoanInformation, RepaymentInfo, InstallmentInfo

# Create your tests here.

class TestContract(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user_obj = None
        self.platforminfo_obj = None
        self.loaninformation_obj = None
        self.repaymentinfo_obj = None
        self.installmentinfo_obj = None

    def tearDown(self):
        pass
        # User.objects.all().delete()
        # PlatFormInfo.objects.all().delete()
        # LoanInformation.objects.all().delete()
        # RepaymentInfo.objects.all().delete()
        # InstallmentInfo.objects.all().delete()

    def test_views_update_load_data(self):
        body = {"data": [
                    {
                        "user": {
                            "username": "ccl",
                            "phone_no": "1212",
                            "id_no": "11112",
                            "platform": "test",
                            "credit_ceiling": 100
                        },
                        "loans": [{
                            "order_number": "121221212",
                            "apply_amount": 22,
                            "exact_amount": 10,
                            "reason": "drunk",
                            "apply_time": "2017-3-3 00:00:00",
                            "interest": 2,
                            "bank_card": "121231",
                            "overdue_days": 20
                        }]
                    }
                    ]
                }
        req = self.factory.post("bc/loan/update/", json.dumps(body))
        user = User.objects.filter(username="ccl")



    def test_views_update_repayment_data(self):
        pass

    def test_views_get_user_data(self):
        pass
