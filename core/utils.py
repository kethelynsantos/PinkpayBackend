import random
from datetime import timedelta
from django.utils import timezone
from django.core.exceptions import ValidationError

from core import models


def generate_card_number():
    existing_card_numbers = models.Card.objects.values_list('number', flat=True)

    while True:
        # gera um número de cartão aleatório de 16 dígitos
        new_card_number = ''.join(random.choices('0123456789', k=16))

        # verifica se o número do cartão é único
        if new_card_number not in existing_card_numbers:
            return new_card_number


def generate_cvv():
    # gera um CVV aleatório de 3 dígitos
    return ''.join(random.choices('0123456789', k=3))


def generate_expiration_date():
    # gera uma data de expiração fixa
    return timezone.now() + timedelta(days=365 * 5)


def calculate_loan_approval(client_balance, requested_amount, installments, interest_rate):
    max_loan_multiplier = 3  # Múltiplo máximo do saldo para aprovação
    max_installments = 12  # Número máximo de parcelas permitidas
    min_requested_amount = 100  # Valor mínimo permitido para empréstimo

    # verifica se o valor solicitado e as parcelas são válidos
    if requested_amount < min_requested_amount:
        raise ValidationError('O valor solicitado é muito baixo.')

    if installments > max_installments:
        raise ValidationError('Número de parcelas excede o máximo permitido.')

    # Calcula o valor máximo do empréstimo com base no saldo e no múltiplo definido
    max_loan_amount = client_balance * max_loan_multiplier

    # Verifica se o valor solicitado não excede o máximo permitido
    if requested_amount > max_loan_amount:
        raise ValidationError('O valor solicitado excede o limite máximo permitido.')

    # Lógica de aprovação com base nas condições
    approval_threshold = 0.2  # Limiar de aprovação como uma porcentagem do saldo
    approval_amount = client_balance * approval_threshold

    if requested_amount <= approval_amount:
        return True
    else:
        return False
