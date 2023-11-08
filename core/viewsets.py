from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from core import serializers, models


class ClienteViewSet(viewsets.ModelViewSet):
    serializer_class = serializers.ClienteSerializer
    queryset = models.Cliente.objects.all()


class MovimentacaoViewSet(viewsets.ModelViewSet):
    serializer_class = serializers.MovimentacaoSerializer
    queryset = models.Movimentacao.objects.all()
