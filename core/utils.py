import random
from datetime import timedelta
from django.utils import timezone
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
