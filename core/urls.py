# core/urls.py
from django.urls import path, include
from rest_framework.routers import SimpleRouter
from .views import CustomUserViewSet, ClientViewSet, AddressViewSet, AccountViewSet, DepositViewSet

router = SimpleRouter()
router.register('customuser', CustomUserViewSet)
router.register('client', ClientViewSet)
router.register(r'address', AddressViewSet, basename='address')
router.register('account', AccountViewSet, basename='account')
router.register('deposit', DepositViewSet, basename='deposit')

urlpatterns = [
    path('api/v1/', include(router.urls)),
    path('api/v1/auth/register/', ClientViewSet.as_view({'post': 'register'}), name='create_user'),
]
