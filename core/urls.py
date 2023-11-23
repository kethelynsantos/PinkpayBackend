# core/urls.py
from django.urls import path, include
from rest_framework.routers import SimpleRouter
from .views import (
    CustomUserViewSet, ClientViewSet, AddressViewSet, AccountViewSet, DepositViewSet,
    TransactionListView, CurrentBalanceView, TransferViewSet, CardViewSet
)

router = SimpleRouter()
router.register('customuser', CustomUserViewSet)
router.register('client', ClientViewSet)
router.register(r'address', AddressViewSet, basename='address')
router.register('account', AccountViewSet, basename='account')
router.register('deposit', DepositViewSet, basename='deposit')
router.register('transfer', TransferViewSet, basename='transfer')
router.register('cards', CardViewSet, basename='card')

urlpatterns = [
    path('api/v1/', include(router.urls)),
    path('api/v1/auth/register/', ClientViewSet.as_view({'post': 'register'}), name='create_user'),
    path('api/v1/transactions/', TransactionListView.as_view(), name='transaction-list'),
    path('api/v1/balance/', CurrentBalanceView.as_view(), name='current-balance'),
    path('api/v1/client/request_credit_card/', ClientViewSet.as_view({'post': 'request_credit_card'}),
         name='request_credit_card'),
]
