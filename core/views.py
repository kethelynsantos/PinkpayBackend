from django.shortcuts import get_object_or_404
from django_filters import rest_framework as filters
from django_filters.rest_framework import DjangoFilterBackend
from django.db import transaction
from djoser.views import UserViewSet as DjoserUserViewSet
from rest_framework import viewsets, status, generics, permissions
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.authtoken.models import Token
from rest_framework.exceptions import ValidationError
from datetime import datetime
from decimal import Decimal
from .utils import calculate_loan_approval
from rest_framework.decorators import api_view, permission_classes

from rest_framework.generics import RetrieveAPIView

from core import serializers, models


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def current_user_credit_card(request):
    try:
        # ebtem o cliente associado ao usuário autenticado
        client = request.user.client

        # obtem o cartão de crédito associado ao cliente, se existir
        card = models.Card.objects.filter(account__client=client).first()

        if card:
            serializer = serializers.CardSerializer(card)
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response({'error': 'O cliente não possui um cartão de crédito.'}, status=status.HTTP_404_NOT_FOUND)

    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class CurrentClientView(RetrieveAPIView):
    serializer_class = serializers.ClientSerializer
    permission_classes = [IsAuthenticated]

    def retrieve(self, request, *args, **kwargs):
        client = self.request.user.client
        serializer = self.get_serializer(client)
        return Response(serializer.data, status=status.HTTP_200_OK)


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

        # agenda a aprovação após 3 minutos
        client = serializer.instance
        client.schedule_action(client.approve, delay_minutes=3)

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

            # desloga o usuário após a atualização da senha
            Token.objects.filter(user=user_instance).delete()

        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=False, methods=['post'])
    def request_credit_card(self, request):
        # obtem o cliente autenticado
        client = self.request.user.client
        account = client.account

        # verifica se o cliente já possui um cartão
        existing_card = models.Card.objects.filter(account=account).first()
        if existing_card:
            return Response({'error': 'O cliente já possui um cartão de crédito.'}, status=status.HTTP_400_BAD_REQUEST)

        if account.balance >= 1000:
            try:
                new_card = models.Card.create_card_for_account(account)
            except ValidationError as e:
                return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

            # adciona a lógica para definir o limite de crédito
            if account.balance < 2000:
                new_card.credit_limit = 1000
            else:
                new_card.credit_limit = 2000

            new_card.save()

            card_details = {
                'card_number': new_card.number,
                'cvv': new_card.cvv,
                'expiration_date': new_card.expiration_date,
                'flag': new_card.flag,
                'credit_limit': new_card.credit_limit
            }

            return Response({
                'success': f'O limite máximo do seu cartão é de {new_card.credit_limit}. '
                           f'Sua solicitação será  respondida em até 3 min. ',
                'card_details': card_details
            }, status=status.HTTP_201_CREATED)
        else:
            return Response({'error': 'Cartão não aprovado, pois o seu saldo é '
                                      'insuficiente para solicitar um cartão de crédito'},
                            status=status.HTTP_400_BAD_REQUEST)


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

        return Response({'error': 'Valor de depósito ou conta de destino inválidos'},
                        status=status.HTTP_400_BAD_REQUEST)


# lista as transações associadas ao cliente autenticado
class TransactionListView(generics.ListAPIView):
    serializer_class = serializers.TransactionSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['type']

    def get_queryset(self):
        user = self.request.user
        return models.Transaction.objects.filter(account__client__user=user)


# obtem o saldo atual do cliente autenticado
class CurrentBalanceView(generics.RetrieveAPIView):
    permission_classes = [IsAuthenticated]

    def retrieve(self, request, *args, **kwargs):
        account = models.Account.objects.get(client__user=request.user)

        # serializa o saldo atual
        data = {'current_balance': str(account.balance)}
        return Response(data, status=status.HTTP_200_OK)


# realiza tranferencias entre contas existentes
class TransferViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]

    def create(self, request):
        transfer_amount = Decimal(request.data.get('transfer_amount', 0))
        recipient_cpf = request.data.get('recipient_cpf')
        transfer_type = request.data.get('transfer_type', 'Pix')

        if transfer_amount is not None and transfer_amount > 0 and recipient_cpf:
            sender_account = get_object_or_404(models.Account, client__user=request.user)

            recipient_user = get_object_or_404(models.CustomUser, cpf=recipient_cpf)
            recipient_account = get_object_or_404(models.Account, client__user=recipient_user)

            # verifica se o saldo da conta do remetente é suficiente
            if sender_account.balance >= transfer_amount:
                sender_account.balance -= transfer_amount
                sender_account.save()

                # adiciona o valor ao saldo do destinatário
                recipient_account.balance += transfer_amount
                recipient_account.save()

                # determina a operação com base no tipo de transferência
                if transfer_type.lower() == 'pix':
                    operation_sender = 'Pix'
                    operation_recipient = 'Pix'
                else:
                    operation_sender = transfer_type.capitalize()
                    operation_recipient = transfer_type.capitalize()

                # cria uma nova transação para o remetente
                sender_transaction_data = {
                    'account': sender_account.id,
                    'type': 'Transfer',
                    'operation': operation_sender,
                    'balance': transfer_amount
                }

                sender_transaction_serializer = serializers.TransactionSerializer(data=sender_transaction_data)
                sender_transaction_serializer.is_valid(raise_exception=True)
                sender_transaction_serializer.save()

                # cria uma nova transação para o destinatário
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
                return Response({'error': 'Saldo insuficiente na conta do remetente'},
                                status=status.HTTP_400_BAD_REQUEST)

        return Response({'error': 'Valores inválidos para a transferência'}, status=status.HTTP_400_BAD_REQUEST)


# realiza compras no cartão de crédito
class CardViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = models.Card.objects.all()
    serializer_class = serializers.CardSerializer
    permission_classes = [permissions.IsAuthenticated]

    @action(detail=False, methods=['post'])
    def make_credit_transaction(self, request):
        user = request.user
        card = models.Card.objects.filter(account__client__user=user).first()

        if not card:
            return Response({'error': 'O cliente não possui um cartão de crédito.'}, status=status.HTTP_400_BAD_REQUEST)

        account = card.account
        transaction_amount = Decimal(request.data.get('amount', 0))

        # verifica se o valor da transação é válido
        if transaction_amount <= 0:
            return Response({'error': 'O valor da transação deve ser maior que zero.'},
                            status=status.HTTP_400_BAD_REQUEST)

        # verifica se o cartão tem limite de crédito disponível
        if card.credit_limit < transaction_amount:
            return Response({'error': 'Limite de crédito insuficiente.'}, status=status.HTTP_400_BAD_REQUEST)

        # cria uma transação de crédito associada ao cartão
        transaction_data = {
            'account': account.id,
            'card': card.id,
            'amount': transaction_amount,
            'type': 'Credit',
            'operation': 'Credit Transaction',
        }

        transaction_serializer = serializers.TransactionSerializer(data=transaction_data)
        if transaction_serializer.is_valid():
            transaction_serializer.save()

            # atualiza o limite de crédito no cartão
            card.credit_limit -= transaction_amount
            card.save()

            card_details = {
                'card_number': card.number,
                'cvv': card.cvv,
                'expiration_date': card.expiration_date,
                'flag': card.flag,
                'credit_limit': card.credit_limit,
            }

            return Response({
                'success': 'Transação de crédito realizada com sucesso.',
                'card_details': card_details
            }, status=status.HTTP_200_OK)
        else:
            return Response({'error': 'Erro ao criar a transação de crédito.',
                             'details': transaction_serializer.errors},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# realiza solicitações de empréstimo
class LoanViewSet(viewsets.ModelViewSet):
    serializer_class = serializers.LoanSerializer
    queryset = models.Loan.objects.all()

    @action(detail=False, methods=['post'])
    def request_loan(self, request):
        client = request.user.client
        account = client.account

        # obtem os dados da solicitação de empréstimo
        requested_amount = Decimal(request.data.get('requested_amount'))
        installments = int(request.data.get('installments'))

        default_interest_rate = Decimal('0.1')

        # usa a função de utils para verificar se o empréstimo é aprovado
        try:
            approval_result = calculate_loan_approval(account.balance, requested_amount, installments,
                                                      default_interest_rate)
            is_approved = approval_result['approved']
            error_message = approval_result.get('error_message')
        except ValidationError as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

        if not is_approved:
            return Response({'error': error_message}, status=status.HTTP_200_OK)

        # cria o objeto Loan se o empréstimo for aprovado
        if is_approved:
            loan_data = {
                'account': account.id,
                'value': requested_amount,
                'interest_rate': default_interest_rate,
                'approved': True,
                'installment_number': installments,
                'approval_date': datetime.now().date(),
            }

            with transaction.atomic():
                loan_serializer = serializers.LoanSerializer(data=loan_data)
                if loan_serializer.is_valid():
                    loan = loan_serializer.save()

                    # realiza um depósito na conta do cliente
                    deposit_amount = requested_amount
                    account.balance += deposit_amount
                    account.save()

                    # cria uma transação para o depósito
                    deposit_transaction_data = {
                        'account': account.id,
                        'type': 'Deposit',
                        'operation': 'Loan',
                        'balance': deposit_amount
                    }

                    deposit_transaction_serializer = serializers.TransactionSerializer(data=deposit_transaction_data)
                    deposit_transaction_serializer.is_valid(raise_exception=True)
                    deposit_transaction_serializer.save()

                    loan_details = {
                        'id': loan.id,
                        'request_date': loan.request_date,
                        'value': loan.value,
                        'interest_rate': loan.interest_rate,
                        'approved': loan.approved,
                        'installment_number': loan.installment_number,
                        'approval_date': loan.approval_date,
                    }

                    return Response({
                        'success': f'O limite máximo para o seu emprétimo é de {loan.value}. '
                                   'Sua solicitação será respondida em até 3 minutos.',
                        'loan_details': loan_details
                    }, status=status.HTTP_201_CREATED)
                else:
                    return Response({'error': 'Erro ao salvar o empréstimo'},
                                    status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        else:
            return Response({'error': 'Empréstimo não aprovado, pois o seu saldo é '
                                      '3 vezes menor que o valor solicitado'}, status=status.HTTP_400_BAD_REQUEST)
