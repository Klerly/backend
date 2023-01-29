# from wallet.models import WalletModel, TransactionModel
# from django.test import RequestFactory, TestCase
# from unittest.mock import patch
# from django.test import TestCase
# from wallet.models import WalletModel, TransactionModel, CardModel
# from rest_framework.test import APIClient
# from account.models import User
# from django.urls import reverse
# from wallet.apis.payment.fiat import PaymentWebhookAPI
# import json
# import hmac
# import hashlib


# class PaymentInitializeAPITestCase(TestCase):
#     def setUp(self):
#         self.client = APIClient()
#         self.user = User.objects.create_user(  # type: ignore
#             username='testuser',
#             password='password',
#             is_verified=True
#         )
#         self.wallet = WalletModel.objects.create(user=self.user)
#         self.url = reverse('wallet:payment-initialize')
#         self.data = {'amount': 100}

#     @patch('wallet.modules.payment.fiat.FiatWalletPayment.initialize')
#     def test_initialize_payment(self, mock_initialize):
#         mock_initialize.return_value = {'status': 'success'}
#         self.client.force_authenticate(user=self.user)  # type: ignore
#         response = self.client.post(self.url, self.data)

#         self.assertEqual(response.status_code, 200)
#         self.assertEqual(response.data, {'status': 'success'})  # type: ignore
#         mock_initialize.assert_called_once_with(100)

#     def test_initialize_payment_unauthenticated(self):
#         response = self.client.post(self.url, self.data)
#         self.assertEqual(response.status_code, 401)

#     def test_initialize_payment_invalid_data(self):
#         self.data = {'amount': 'invalid'}  # type: ignore
#         self.client.force_authenticate(user=self.user)  # type: ignore
#         response = self.client.post(self.url, self.data)

#         self.assertEqual(response.status_code, 400)


# class PaymentVerifyAPITestCase(TestCase):
#     def setUp(self):
#         self.factory = RequestFactory()
#         self.client = APIClient()
#         self.user = User.objects.create_user(  # type: ignore
#             username='testuser',
#             password='password',
#             is_verified=True
#         )
#         self.wallet = WalletModel.objects.create(user=self.user)
#         self.transaction = TransactionModel.objects.create(
#             user=self.user,
#             reference='123',
#             status=TransactionModel.Status.PENDING,
#             amount=100
#         )
#         self.url = reverse('wallet:payment-verify',
#                            args=[self.transaction.reference])

#     @patch('wallet.modules.payment.fiat.FiatWalletPayment.verify')
#     def test_verify_payment_success(self, mock_verify):
#         mock_verify.return_value = {'status': 'success'}
#         self.client.force_authenticate(user=self.user)  # type: ignore
#         response = self.client.get(self.url)

#         self.assertEqual(response.status_code, 200)
#         self.assertEqual(response.data, {'status': 'success'})  # type: ignore
#         mock_verify.assert_called_once_with(self.transaction)

#     def test_verify_payment_not_found(self):
#         self.transaction.delete()
#         self.client.force_authenticate(user=self.user)  # type: ignore
#         response = self.client.get(self.url)

#         self.assertEqual(response.status_code, 400)
#         self.assertEqual(
#             response.data,  # type: ignore
#             {'non_field_errors': ['Transaction not found']}
#         )

#     def test_verify_payment_already_completed(self):
#         self.transaction.status = TransactionModel.Status.SUCCESS
#         self.transaction.save()
#         self.client.force_authenticate(user=self.user)  # type: ignore
#         response = self.client.get(self.url)

#         self.assertEqual(response.status_code, 400)
#         self.assertEqual(
#             response.data,  # type: ignore
#             {'non_field_errors': ['Transaction already completed']}
#         )

#     def test_verify_payment_unauthenticated(self):
#         response = self.client.get(self.url)
#         self.assertEqual(response.status_code, 401)


# class PaymentChargeAPITestCase(TestCase):
#     card_data = {
#         "keep": False,
#         "type": 'Visa',
#         "last_four": '1234',
#         "exp_month": '01',
#         "exp_year": '2022',
#         "authorization_code": 'authcode',
#         "data": {'last4': '1234', 'exp_month': '01', 'exp_year': '2022',
#                      'authorization_code': 'authcode', 'signature': 'signature'}
#     }

#     def setUp(self):
#         self.factory = RequestFactory()
#         self.client = APIClient()
#         self.user = User.objects.create_user(  # type: ignore
#             username='testuser', password='password',
#             is_verified=True
#         )
#         self.wallet = WalletModel.objects.create(user=self.user, balance=1000)
#         self.card = CardModel.objects.create(
#             user=self.user,
#             signature='signature',
#             **self.card_data
#         )
#         self.url = reverse('wallet:payment-charge')
#         self.client.force_authenticate(user=self.user)

#     @patch('wallet.modules.payment.fiat.FiatWalletPayment.charge')
#     def test_valid_charge(self, mock_charge):
#         mock_charge.return_value = {'status': 'success'}
#         data = {'amount': 100, 'signature': 'signature'}
#         response = self.client.post(self.url, data)
#         self.assertEqual(response.status_code, 200)
#         self.assertEqual(response.data['status'], 'success')  # type: ignore
#         mock_charge.assert_called_with(self.card, 100)


# class PaymentWebhookAPITest(TestCase):
#     def setUp(self):
#         self.factory = RequestFactory()
#         self.view = PaymentWebhookAPI.as_view()
#         self.url = reverse('wallet:payment-webhook')
#         self.request_data = {
#             'event': 'charge.success',
#             'data': {
#                 'status': 'success',
#                 'reference': 'txn_123'
#             }
#         }
#         self.paystack_signature = hmac.new(
#             b'secret_key', json.dumps(self.request_data).encode('utf-8'),
#             hashlib.sha512).hexdigest()
#         self.transaction = TransactionModel.objects.create(
#             user=User.objects.create_user(  # type: ignore
#                 username='testuser', password='password'),
#             reference='txn_123',
#             status=TransactionModel.Status.PENDING,
#             amount=100
#         )

#     @patch('wallet.modules.payment.fiat.FiatWalletPayment.success')
#     def test_valid_request(self, mock_success):
#         with self.settings(
#             PAYSTACK_WHITELISTED_IPS=['127.0.0.1'],
#             PAYSTACK_SECRET_KEY='secret_key'
#         ):
#             request = self.factory.post(self.url, json.dumps(
#                 self.request_data), content_type='application/json')
#             request.META['HTTP_X_FORWARDED_FOR'] = '127.0.0.1'
#             request.META['HTTP_X_PAYSTACK_SIGNATURE'] = self.paystack_signature

#             response = self.view(request)
#             mock_success.assert_called_once_with(
#                 self.transaction,
#                 self.request_data['data']
#             )
#             self.assertEqual(response.status_code, 200)

#     def test_invalid_ip(self):
#         with self.settings(PAYSTACK_WHITELISTED_IPS=['192.168.1.1']):
#             request = self.factory.post(self.url, json.dumps(
#                 self.request_data), content_type='application/json')
#             request.META['HTTP_X_FORWARDED_FOR'] = '127.0.0.1'
#             request.META['HTTP_X_PAYSTACK_SIGNATURE'] = self.paystack_signature

#             response = self.view(request)
#             self.assertEqual(response.status_code, 403)

#     def test_invalid_hash(self):
#         with self.settings(PAYSTACK_SECRET_KEY='secret_key'):
#             request = self.factory.post(self.url, json.dumps(
#                 self.request_data), content_type='application/json')
#             request.META['HTTP_X_FORWARDED_FOR'] = '192.168.1.1'
#             request.META['HTTP_X_PAYSTACK_SIGNATURE'] = "fake-hash"

#             response = self.view(request)
#             self.assertEqual(response.status_code, 403)

#     # test that a logging error is raised when the transaction is not found

#     @patch('logging.error')
#     def test_transaction_not_found(self, mock_error):
#         self.request_data['data']['reference'] = 'txn_456'
#         self.paystack_signature = hmac.new(
#             b'secret_key', json.dumps(self.request_data).encode('utf-8'),
#             hashlib.sha512).hexdigest()

#         with self.settings(
#             PAYSTACK_WHITELISTED_IPS=['127.0.0.1'],
#             PAYSTACK_SECRET_KEY='secret_key'
#         ):
#             request = self.factory.post(self.url, json.dumps(
#                 self.request_data), content_type='application/json')
#             request.META['HTTP_X_FORWARDED_FOR'] = '127.0.0.1'
#             request.META['HTTP_X_PAYSTACK_SIGNATURE'] = self.paystack_signature

#             response = self.view(request)
#             mock_error.assert_called_once()
#             self.assertEqual(response.status_code, 200)
