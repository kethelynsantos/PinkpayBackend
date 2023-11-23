from django.shortcuts import get_object_or_404
from django_filters import rest_framework as filters
from rest_framework import viewsets, status, generics, permissions
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.authtoken.models import Token
from rest_framework.exceptions import ValidationError
from djoser.views import UserViewSet as DjoserUserViewSet

from decimal import Decimal

from core import serializers, models


# gerencia endereços associados a clientes
class AddressViewSet(viewsets.ModelViewSet):
    serializer_class = serializers.AddressSerializer
    queryset = models.Address.objects.all()

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)

        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)


# realiza o registro personalizado de usuários
class CustomUserViewSet(DjoserUserViewSet):
    @action(detail=False, methods=['post'])
    def register(self, request):
        serializer = serializers.CustomUserSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


# gerencia clientes
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

    # atualiza dados do cliente e do usuário associado
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


# visualiza todas as contas
class AccountViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = serializers.AccountSerializer
    queryset = models.Account.objects.all()


# realiza depósitos em contas
class DepositViewSet(viewsets.ModelViewSet):
    queryset = models.Account.objects.all()
    serializer_class = serializers.AccountSerializer

    # cria um depósito em uma conta, atualizando saldo e registrando transação
    def create(self, request, *args, **kwargs):
        deposit_amount = request.data.get('deposit_amount')
        transaction_type = request.data.get('transaction_type', 'Deposit')
        operation_type = request.data.get('operation_type', 'Credit') or 'Deposit'
        destination_account_id = request.data.get('destination_account')

        deposit_amount = Decimal(request.data.get('deposit_amount', 0))

        if deposit_amount is not None and deposit_amount > 0 and destination_account_id:
            # verifica se a conta de destino existe
            destination_account = get_object_or_404(models.Account, id=destination_account_id)

            # adiciona o valor ao saldo da conta de destino
            destination_account.balance += deposit_amount
            destination_account.save()

            # cria uma nova transação na conta de destino
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


# lista as transações associadas ao cliente autenticado
class TransactionListView(generics.ListAPIView):
    serializer_class = serializers.TransactionSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        return models.Transaction.objects.filter(account__client__user=user)


# obtem o saldo atual do cliente autenticado
class CurrentBalanceView(generics.RetrieveAPIView):
    permission_classes = [IsAuthenticated]

    def retrieve(self, request, *args, **kwargs):
        # obtem a conta associada ao cliente autenticado
        account = models.Account.objects.get(client__user=request.user)

        # serialize o saldo atual
        data = {'current_balance': str(account.balance)}
        return Response(data, status=status.HTTP_200_OK)


# realiza tranferencias entre contas existentes
class TransferViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]

    def create(self, request, *args, **kwargs):
        transfer_amount = Decimal(request.data.get('transfer_amount', 0))
        recipient_cpf = request.data.get('recipient_cpf')
        transfer_type = request.data.get('transfer_type', 'Pix')

        if transfer_amount is not None and transfer_amount > 0 and recipient_cpf:
            # Obtenha a conta do usuário autenticado
            sender_account = get_object_or_404(models.Account, client__user=request.user)

            recipient_user = get_object_or_404(models.CustomUser, cpf=recipient_cpf)
            recipient_account = get_object_or_404(models.Account, client__user=recipient_user)

            # Verifica se o saldo da conta do remetente é suficiente
            if sender_account.balance >= transfer_amount:
                # Deduz o valor do saldo do remetente
                sender_account.balance -= transfer_amount
                sender_account.save()

                # Adiciona o valor ao saldo do destinatário
                recipient_account.balance += transfer_amount
                recipient_account.save()

                # Determina a operação com base no tipo de transferência
                if transfer_type.lower() == 'pix':
                    operation_sender = 'Pix'
                    operation_recipient = 'Pix'
                else:
                    # Ajuste para incluir 'Transação'
                    operation_sender = transfer_type.capitalize()
                    operation_recipient = transfer_type.capitalize()

                # Cria uma nova transação para o remetente
                sender_transaction_data = {
                    'account': sender_account.id,
                    'type': 'Transfer',
                    'operation': operation_sender,
                    'balance': transfer_amount
                }

                sender_transaction_serializer = serializers.TransactionSerializer(data=sender_transaction_data)
                sender_transaction_serializer.is_valid(raise_exception=True)
                sender_transaction_serializer.save()

                # Cria uma nova transação para o destinatário
                recipient_transaction_data = {
                    'account': recipient_account.id,
                    'type': 'Transfer Received',
                    'operation': operation_recipient,
                    'balance': transfer_amount
                }

                recipient_transaction_serializer = serializers.TransactionSerializer(data=recipient_transaction_data)
                recipient_transaction_serializer.is_valid(raise_exception=True)
                recipient_transaction_serializer.save()

                return Response({'success': 'Transferência realizada com sucesso'}, status=status.HTTP_201_CREATED)
            else:
                return Response({'error': 'Saldo insuficiente na conta do remetente'}, status=status.HTTP_400_BAD_REQUEST)

        return Response({'error': 'Valores inválidos para a transferência'}, status=status.HTTP_400_BAD_REQUEST)


class CardViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = models.Card.objects.all()
    serializer_class = serializers.CardSerializer
    permission_classes = [permissions.IsAuthenticated]
