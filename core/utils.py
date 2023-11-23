import random
from datetime import timedelta
from django.utils import timezone
from django.core.exceptions import ValidationError
from decimal import Decimal, ROUND_DOWN
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
    max_loan_multiplier = 3  # múltiplo máximo do saldo para aprovação
    max_installments = 12  # número máximo de parcelas permitidas
    min_requested_amount = 100  # valor mínimo permitido para empréstimo
    max_installment_value_ratio = Decimal('0.2')  # limite para o valor de cada parcela

    # verifica se o valor solicitado e as parcelas são válidos
    if requested_amount < min_requested_amount:
        raise ValidationError('O valor solicitado é muito baixo.')

    if installments > max_installments:
        raise ValidationError('Número de parcelas excede o máximo permitido.')

    # calcula o valor máximo do empréstimo com base no saldo e no múltiplo definido
    max_loan_amount = client_balance * max_loan_multiplier

    if requested_amount > max_loan_amount:
        raise ValidationError('O valor solicitado excede o limite máximo permitido.')

    total_loan_amount = calculate_total_loan_amount(requested_amount, installments, interest_rate)

    # verifica se o valor de cada parcela é menor ou igual ao saldo da conta
    max_installment_value = max_installment_value_ratio * client_balance
    if requested_amount / installments <= max_installment_value:
        return True
    else:
        raise ValidationError('O valor de cada parcela excede o limite permitido.')


def calculate_total_loan_amount(requested_amount, installments, interest_rate):
    # calcula o valor total do empréstimo com base no número de parcelas e taxa de juros
    total_loan_amount = Decimal(requested_amount) * (1 + Decimal(interest_rate)) * installments

    return total_loan_amount.quantize(Decimal('0.01'), rounding=ROUND_DOWN)
