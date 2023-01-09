
from rest_framework.views import APIView
from wallet.models import WalletModel
from core.response import SuccessResponse
from wallet.serializers.balance import WalletBalanceSerializer


class WalletBalanceAPI(APIView):
    def get(self, request):
        wallet: WalletModel = request.user.wallet
        serializer = WalletBalanceSerializer(wallet)
        return SuccessResponse(serializer.data)
