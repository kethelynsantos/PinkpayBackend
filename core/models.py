from django.db import models
from django.contrib.auth.models import (
    AbstractBaseUser,
    PermissionsMixin,
    BaseUserManager,
)


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
    # Relationship with the Address model
    address = models.ForeignKey(Address, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    photo = models.ImageField(upload_to='client_photos/', null=True)
    birth_date = models.DateField()
    phone = models.CharField(max_length=15)
    email = models.EmailField(max_length=50)

    class Meta:
        verbose_name = 'Client'
        verbose_name_plural = 'Clients'

    def __str__(self):
        return f'{self.name}'


# Model to represent individual clients (pf)
class IndividualClient(models.Model):
    # Relationship with the Client model
    client = models.OneToOneField(Client, on_delete=models.CASCADE)
    cpf = models.CharField(max_length=15)
    rg = models.CharField(max_length=15)

    class Meta:
        verbose_name = 'Individual Client'
        verbose_name_plural = 'Individual Clients'

    def __str__(self):
        return f'{self.client.name} - {self.cpf}, {self.rg}'


# Model to represent business clients (pj)
class BusinessClient(models.Model):
    # Relationship with the Client model
    client = models.OneToOneField(Client, on_delete=models.CASCADE)
    cnpj = models.CharField(max_length=25)
    corporate_name = models.CharField(max_length=100, null=True)

    class Meta:
        verbose_name = 'Business Client'
        verbose_name_plural = 'Business Clients'

    def __str__(self):
        return f'{self.client.name} - {self.cnpj}, {self.corporate_name}'


# Model to represent accounts
class Account(models.Model):
    # Relationship with the Client model
    client = models.ForeignKey(Client, on_delete=models.CASCADE)
    agency = models.CharField(max_length=10)
    number = models.CharField(max_length=25)
    type = models.CharField(max_length=20)
    balance = models.DecimalField(null=True, max_digits=10, decimal_places=2)
    active = models.BooleanField()

    class Meta:
        verbose_name = 'Account'
        verbose_name_plural = 'Accounts'

    def __str__(self):
        return f'{self.number}, {self.active}'


# Model to represent loans
class Loan(models.Model):
    # Relationship with the Account model
    account = models.ForeignKey(Account, on_delete=models.CASCADE, related_name='loans')
    request_date = models.DateField(auto_now_add=True)
    requested_amount = models.DecimalField(max_digits=10, decimal_places=2)
    interest_rate = models.FloatField()
    approved = models.BooleanField()
    installment_number = models.IntegerField()
    approval_date = models.DateField(null=True, blank=True)
    note = models.CharField(max_length=200)

    class Meta:
        verbose_name = 'Loan'
        verbose_name_plural = 'Loans'

    def __str__(self):
        return f'{self.requested_amount}, {self.approved}'


# Model to represent cards
class Card(models.Model):
    # Relationship with the Account model
    account = models.ForeignKey(Account, on_delete=models.CASCADE, related_name='cards')
    number = models.CharField(max_length=30, unique=True)
    cvv = models.CharField(max_length=5)
    expiration_date = models.DateField()
    brand = models.CharField(max_length=20)
    status = models.CharField(max_length=20)

    class Meta:
        verbose_name = 'Card'
        verbose_name_plural = 'Cards'

    def __str__(self):
        return f'{self.number}, {self.status}'


# Model to represent transactions
class Transaction(models.Model):
    # Relationship with the Card model
    card = models.ForeignKey(Card, on_delete=models.CASCADE)
    date_time = models.DateTimeField(auto_now_add=True)
    operation = models.CharField(max_length=20)
    amount = models.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        verbose_name = 'Transaction'
        verbose_name_plural = 'Transactions'

    def __str__(self):
        return f'{self.operation}, {self.amount}'
