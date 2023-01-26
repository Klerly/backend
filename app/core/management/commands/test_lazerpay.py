from django.core.management.base import BaseCommand, CommandError


class Command(BaseCommand):
    help = 'Closes the specified poll for voting'

    def handle(self, *args, **options):
        from account.models import User
        from core.modules.payment.crypto.lazerpay import LazerPay
        me = User.objects.get(email="lojetokun@gmail.com")
        l = LazerPay(me)
        print(l.verify('lAlqnSGVqj'))

        x = {
            'id': '6ec6cedd-5f3a-4f62-9952-561821748dca',
            'reference': 'x2Tm7GvqQx',
            'businessName': 'Klerly',
            'businessEmail': 'ojetoks@gmail.com',
            'businessLogo': 'https://res.cloudinary.com/lazer/image/upload/v1637512933/logo-default_ufyz0x.svg',
            'customerName': 'Oja Daddy',
            'customerEmail': 'lojetokun@gmail.com',
            'address': '0x64273Fdf11623d1ec16588dC57e78EF39171390D',
            'coin': 'USDT',
            'cryptoAmount': 1000,
            'currency': 'USD',
            'fiatAmount': 1000,
            'feeInCrypto': 0,
            'network': 'testnet',
            'acceptPartialPayment': False,
            'fiatRate': 1,
            'cryptoRate': 1
        }
