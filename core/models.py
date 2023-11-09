from django.db import models
from django.contrib.auth.models import (
    AbstractBaseUser,
    PermissionsMixin,
    BaseUserManager,
)

# https://dev.to/lyamaa/authenticate-with-djoser-2kf7


# class CustomUserManager(BaseUserManager):
#     def create_user(self, email, username, password=None, **extra_fields):
#         if not email:
#             raise ValueError("User must have an email")
#         email = self.normalize_email(email)
#         user = self.model(email=email, username=username, **extra_fields)
#         user.set_password(password)
#         user.save(using=self._db)
#         return user
#
#     def create_superuser(self, cpf, email, password=None, **extra_fields):
#         user = self.create_user(cpf, email, password=password, **extra_fields)
#         user.is_active = True
#         user.is_staff = True
#         user.is_admin = True
#         user.save(using=self._db)
#         return user


class Endereco(models.Model):
    logradouro = models.CharField(max_length=100)
    bairro = models.CharField(max_length=75)
    cidade = models.CharField(max_length=75)
    uf = models.CharField(max_length=2)
    cep = models.CharField(max_length=10)

    class Meta:
        verbose_name = 'Endereço'
        verbose_name_plural = 'Endereços'

    def __str__(self):
        return f'{self.logradouro}, {self.bairro}, {self.cidade}, {self.uf}'


class Cliente(models.Model):
    id_endereco = models.ForeignKey(Endereco, on_delete=models.CASCADE)
    nome = models.CharField(max_length=100)
    foto = models.CharField(max_length=100)
    data_nascimento = models.DateField()
    telefone = models.CharField(max_length=15)
    email = models.EmailField(max_length=50)
    usuario = models.CharField(max_length=10)
    senha = models.IntegerField()

    class Meta:
        verbose_name = 'Cliente'
        verbose_name_plural = 'Clientes'

    def __str__(self):
        return f'{self.usuario}, {self.nome}'


class ClientePF(models.Model):
    id_cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE, null=True)
    cpf = models.CharField(max_length=15)
    rg = models.CharField(max_length=15)

    class Meta:
        verbose_name = 'ClientePF'
        verbose_name_plural = 'ClientesPF'

    def __str__(self):
        return f'{self.cpf}, {self.rg}'


class ClientePJ(models.Model):
    id_cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE, null=True)
    cnpj = models.CharField(max_length=25)
    razao_social = models.CharField(max_length=100, null=True)

    class Meta:
        verbose_name = 'ClientePJ'
        verbose_name_plural = 'ClientesPJ'

    def __str__(self):
        return f'{self.cnpj}, {self.razao_social}'


class Conta(models.Model):
    id_cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE)
    agencia = models.CharField(max_length=10)
    numero = models.CharField(max_length=25)
    tipo = models.CharField(max_length=20)
    saldo = models.DecimalField(null=True, max_digits=10, decimal_places=2)
    ativa = models.BooleanField()

    class Meta:
        verbose_name = 'Conta'
        verbose_name_plural = 'Contas'

    def __str__(self):
        return f'{self.numero}, {self.ativa}'


class Emprestimo(models.Model):
    id_conta = models.ForeignKey(Conta, on_delete=models.CASCADE)
    data_solicitacao = models.DateField(auto_now_add=True)
    valor_solicitado = models.DecimalField(max_digits=10, decimal_places=2)
    juros = models.FloatField()
    aprovado = models.BooleanField()
    numero_parcela = models.IntegerField()
    data_aprovacao = models.DateField(null=True, blank=True)
    observacao = models.CharField(max_length=200)

    class Meta:
        verbose_name = 'Emprestimo'
        verbose_name_plural = 'Emprestimos'

    def __str__(self):
        return f'{self.valor_solicitado}, {self.aprovado}'


class Cartao(models.Model):
    id_conta = models.ForeignKey(Conta, on_delete=models.CASCADE)
    numero = models.CharField(max_length=30, unique=True)
    cvv = models.CharField(max_length=5)
    validade = models.DateField()
    bandeira = models.CharField(max_length=20)
    situacao = models.CharField(max_length=20)

    class Meta:
        verbose_name = 'Cartao'
        verbose_name_plural = 'Cartoes'

    def __str__(self):
        return f'{self.numero}, {self.situacao}'


class Movimentacao(models.Model):
    id_cartao = models.ForeignKey(Cartao, on_delete=models.CASCADE)
    data_hora = models.DateTimeField(auto_now_add=True)
    operacao = models.CharField(max_length=20)
    valor = models.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        verbose_name = 'Movimentacao'
        verbose_name_plural = 'Movimentacoes'

    def __str__(self):
        return f'{self.operacao}, {self.valor}'
