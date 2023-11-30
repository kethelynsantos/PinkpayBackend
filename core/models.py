import random
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import (
    AbstractBaseUser,
    PermissionsMixin,
    BaseUserManager,
)
from django.contrib.auth import get_user_model
from .utils import generate_card_number, generate_cvv, generate_expiration_date
from django.core.validators import MinValueValidator
from datetime import datetime
import threading


class CustomUserManager(BaseUserManager):
    def create_user(self, cpf, password=None, **extra_fields):
        if not cpf:
            raise ValueError("CPF is required to create a user.")

        user = self.model(cpf=cpf, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, cpf, password=None, **extra_fields):
        user = self.create_user(cpf, password, **extra_fields)
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)
        return user


class CustomUser(AbstractBaseUser, PermissionsMixin):
    cpf = models.CharField(max_length=15, unique=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    objects = CustomUserManager()

    USERNAME_FIELD = 'cpf'

    def __str__(self):
        return self.cpf


# Model to represent addresses
class Address(models.Model):
    objects = None
    street = models.CharField(max_length=100)
    neighborhood = models.CharField(max_length=75)
    city = models.CharField(max_length=75)
    state = models.CharField(max_length=2)
    zip_code = models.CharField(max_length=10)

    class Meta:
        verbose_name = 'Address'
        verbose_name_plural = 'Addresses'

    def __str__(self):
        return f'{self.street}, {self.neighborhood}, {self.city}, {self.state}'


# Model to represent clients
class Client(models.Model):
    STATUS_IN_APPROVAL = 'Em aprovação'
    STATUS_APPROVED = 'Aprovado'
    STATUS_CHOICES = [
        (STATUS_IN_APPROVAL, 'Em aprovação'),
        (STATUS_APPROVED, 'Aprovado'),
    ]

    # Relationship with the Address model
    address = models.ForeignKey(Address, on_delete=models.CASCADE, blank=True, null=True)
    user = models.OneToOneField(get_user_model(), on_delete=models.CASCADE, blank=True, null=True)
    name = models.CharField(max_length=100)
    photo = models.ImageField(upload_to='client_photos/', null=True, blank=True)
    birth_date = models.DateField()
    phone = models.CharField(max_length=15)
    email = models.EmailField(max_length=50)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_IN_APPROVAL)
    approval_date = models.DateTimeField(null=True, blank=True)

    def schedule_action(self, action_function, delay_minutes=3, *args, **kwargs):
        timer = threading.Timer(delay_minutes * 60, action_function, args=args, kwargs=kwargs)
        timer.start()

    def approve(self):
        if self.status == self.STATUS_IN_APPROVAL:
            self.status = self.STATUS_APPROVED
            self.approval_date = datetime.now()
            self.save()

    class Meta:
        verbose_name = 'Client'
        verbose_name_plural = 'Clients'

    def __str__(self):
        return f'Cliente: {self.name}'


# Model to represent accounts
class Account(models.Model):
    objects = None
    client = models.OneToOneField(Client, on_delete=models.CASCADE)
    agency = models.CharField(max_length=10, default='0000')
    number = models.CharField(max_length=25)
    balance = models.DecimalField(null=True, max_digits=10, decimal_places=2, default=0.0)
    active = models.BooleanField(default=True)

    class Meta:
        verbose_name = 'Account'
        verbose_name_plural = 'Accounts'

    def __str__(self):
        return f'{self.number}, {self.active}'

    # sinal que será acionado sempre que um novo cliente for salvo
    @receiver(post_save, sender=Client)
    def create_account(sender, instance, created, **kwargs):
        if created and not hasattr(instance, 'account'):
            # verifica se o cliente já possui uma conta
            if not hasattr(instance, 'account'):
                # gera um número de conta aleatório
                account_number = ''.join(random.choices('0123456789', k=15))

            # cria uma nova conta para o cliente
            account = Account.objects.create(client=instance, number=account_number)

            # define o numero da agencia
            account.agency = '28991'
            account.save()


# Model to represent loans
class Loan(models.Model):
    # Relationship with the Account model
    account = models.ForeignKey(Account, on_delete=models.CASCADE, related_name='loans')
    request_date = models.DateField(auto_now_add=True)
    value = models.DecimalField(max_digits=10, decimal_places=2)
    interest_rate = models.FloatField()
    approved = models.BooleanField()
    installment_number = models.IntegerField()
    approval_date = models.DateField(null=True, blank=True)

    class Meta:
        verbose_name = 'Loan'
        verbose_name_plural = 'Loans'

    def __str__(self):
        return f'{self.value}, {self.approved}'


# Model to represent cards
class Card(models.Model):
    objects = None
    account = models.ForeignKey(Account, on_delete=models.CASCADE, related_name='cards')
    number = models.CharField(max_length=30, unique=True)
    cvv = models.CharField(max_length=5)
    expiration_date = models.DateField()
    flag = models.CharField(max_length=20)
    credit_limit = models.DecimalField(
        max_digits=10, decimal_places=2,
        validators=[MinValueValidator(0)],
        default=0,
        help_text='Limite de crédito do cartão'
    )

    class Meta:
        verbose_name = 'Card'
        verbose_name_plural = 'Cards'

    def __str__(self):
        return f'{self.number}, {self.account}'

    @classmethod
    def create_card_for_account(cls, account):
        card_number = generate_card_number()
        cvv = generate_cvv()
        expiration_date = generate_expiration_date()

        # Cria o novo cartão
        new_card = cls.objects.create(
            account=account,
            number=card_number,
            cvv=cvv,
            expiration_date=expiration_date,
            flag='Mastercard'  # ou qualquer outra lógica para definir a bandeira
        )

        return new_card


# Model to represent transactions
class Transaction(models.Model):
    account = models.ForeignKey(Account, on_delete=models.CASCADE)
    type = models.CharField(max_length=30)
    date_time = models.DateTimeField(auto_now_add=True)
    operation = models.CharField(max_length=20)
    balance = models.DecimalField(max_digits=12, decimal_places=2, null=True)

    class Meta:
        verbose_name = 'Transaction'
        verbose_name_plural = 'Transactions'

    def __str__(self):
        return f'{self.operation}, {self.balance}'
