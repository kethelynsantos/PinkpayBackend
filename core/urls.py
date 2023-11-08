from django.urls import path

from rest_framework.routers import SimpleRouter

from .viewsets import (
    ClienteViewSet,
    MovimentacaoViewSet)


router = SimpleRouter()
router.register('cliente', ClienteViewSet)
router.register('movimentacao', MovimentacaoViewSet)
