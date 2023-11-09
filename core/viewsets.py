from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from core import serializers, models


class ClienteViewSet(viewsets.ModelViewSet):
    serializer_class = serializers.ClienteSerializer
    queryset = models.Cliente.objects.all()

    @action(detail=True, methods=['get'])
    def movimentacoes(self, request, pk=None):
        movimentacao = self.get_object()
        serializer = serializers.MovimentacaoSerializer(movimentacao.movimentacoes.all(), many=True)
        return Response(serializer.data)


class MovimentacaoViewSet(viewsets.ModelViewSet):
    serializer_class = serializers.MovimentacaoSerializer
    queryset = models.Movimentacao.objects.all()
