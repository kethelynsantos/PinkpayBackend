from django.urls import path, include
from rest_framework.routers import SimpleRouter
from .views import CustomUserViewSet, ClientViewSet

router = SimpleRouter()
router.register('customuser', CustomUserViewSet)
router.register('client', ClientViewSet)

urlpatterns = [
    path('api/v1/', include(router.urls)),
    # path('api/v1/auth/register/', ClientViewSet.as_view(), name='create_user'),
]
