from django.shortcuts import get_object_or_404
from django_filters import rest_framework as filters
from rest_framework import viewsets, status, generics
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.authtoken.models import Token
from djoser.views import UserViewSet as DjoserUserViewSet

from decimal import Decimal

from core import serializers, models


class AddressViewSet(viewsets.ModelViewSet):
    serializer_class = serializers.AddressSerializer
    queryset = models.Address.objects.all()

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)

        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)


class CustomUserViewSet(DjoserUserViewSet):
    @action(detail=False, methods=['post'])
    def register(self, request):
        serializer = serializers.CustomUserSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class ClientViewSet(viewsets.ModelViewSet):
    serializer_class = serializers.ClientSerializer
    queryset = models.Client.objects.all()
    filter_backends = (filters.DjangoFilterBackend, )
    filterset_fields = ('user',)
    search_fields = ('user__username', 'user__email')

    # chamada quando um novo cliente é criado
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()

        # deleta o usuário associado
        if instance.user:
            user_id = instance.user.id
            user = get_object_or_404(models.CustomUser, id=user_id)
            user.delete()

        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)

    def partial_update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        # atualizar dados do usuário
        user_data = request.data.get('user', {})
        if user_data:
            user_instance = instance.user
            user_serializer = serializers.CustomUserSerializer(user_instance, data=user_data, partial=True)
            user_serializer.is_valid(raise_exception=True)
            user_serializer.save()

            # deslogar o usuário após a atualização da senha
            Token.objects.filter(user=user_instance).delete()

        return Response(serializer.data, status=status.HTTP_200_OK)


class AccountViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = serializers.AccountSerializer
    queryset = models.Account.objects.all()


class DepositViewSet(viewsets.ModelViewSet):
    queryset = models.Account.objects.all()
    serializer_class = serializers.AccountSerializer

    def create(self, request, *args, **kwargs):
        deposit_amount = request.data.get('deposit_amount')
        transaction_type = request.data.get('transaction_type', 'Deposit')
        operation_type = request.data.get('operation_type', 'Credit') or 'Deposit'
        destination_account_id = request.data.get('destination_account')

        deposit_amount = Decimal(request.data.get('deposit_amount', 0))

        if deposit_amount is not None and deposit_amount > 0 and destination_account_id:
            # Verifica se a conta de destino existe
            destination_account = get_object_or_404(models.Account, id=destination_account_id)

            # Adiciona o valor ao saldo da conta de destino
            destination_account.balance += deposit_amount
            destination_account.save()

            # Cria uma nova transação na conta de destino
            transaction_data = {
                'account': destination_account.id,
                'type': transaction_type,
                'operation': operation_type,
                'balance': deposit_amount
            }

            transaction_serializer = serializers.TransactionSerializer(data=transaction_data)
            transaction_serializer.is_valid(raise_exception=True)
            transaction_serializer.save()

            return Response(self.get_serializer(destination_account).data, status=status.HTTP_201_CREATED)

        return Response({'error': 'Valor de depósito ou conta de destino inválidos'}, status=status.HTTP_400_BAD_REQUEST)
