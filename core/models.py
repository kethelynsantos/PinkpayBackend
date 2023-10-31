from django.db import models


class Endereco(models.Model):
    id = models.AutoField(primary_key=True)
    logradouro = models.CharField(max_length=100)
    bairro = models.CharField(max_length=75)
    cidade = models.CharField(max_length=75)
    uf = models.CharField(max_length=2)
    cep = models.CharField(max_length=10)


class Cliente(models.Model):
    id = models.AutoField(primary_key=True)
    id_endereco = models.ForeignKey(Endereco, on_delete=models.CASCADE)
    razao_social = models.CharField(max_length=100)
    social_fantasia = models.CharField(max_length=100)
    foto = models.CharField(max_length=100)
    data_nascimento = models.DateField()
    usuario = models.CharField(max_length=10)
    senha = models.IntegerField()


class EmprestimoParcela(models.Model):
    id = models.AutoField(primary_key=True)
    codigoEmprestimo = models.IntegerField()
    numero = models.IntegerField()
    dataVencimento = models.DateField()
    valorParcela = models.DecimalField(max_digits=10, decimal_places=2)
    dataPagamento = models.DateField(null=True, blank=True)
    valorPago = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)


class Emprestimo(models.Model):
    codigo = models.AutoField(primary_key=True)
    codigoConta = models.IntegerField()
    dataSolicitacao = models.DateField()
    valorSolicitado = models.DecimalField(max_digits=10, decimal_places=2)
    juros = models.FloatField()
    aprovado = models.BooleanField()
    numeroParcela = models.IntegerField()
    dataAprovacao = models.DateField(null=True, blank=True)
    observacao = models.CharField(max_length=200)


class Movimentacao(models.Model):
    codigo = models.AutoField(primary_key=True)
    codigoCartao = models.IntegerField()
    dataHora = models.DateTimeField()
    operacao = models.CharField(max_length=20)
    valor = models.DecimalField(max_digits=10, decimal_places=2)


class Investimento(models.Model):
    codigo = models.AutoField(primary_key=True)
    codigoConta = models.IntegerField()
    tipo = models.CharField(max_length=30)
    aporte = models.DecimalField(max_digits=10, decimal_places=2)
    taxaAdministracao = models.FloatField()
    prazo = models.CharField(max_length=20)
    grauRisco = models.CharField(max_length=5)
    rentabilidade = models.DecimalField(max_digits=10, decimal_places=2)
    finalizado = models.BooleanField()


class Cartao(models.Model):
    codigo = models.AutoField(primary_key=True)
    codigoConta = models.IntegerField()
    numero = models.CharField(max_length=30)
    cvv = models.CharField(max_length=5)
    validade = models.DateField()
    bandeira = models.CharField(max_length=20)
    situacao = models.CharField(max_length=20)


class Conta(models.Model):
    codigo = models.AutoField(primary_key=True)
    agencia = models.CharField(max_length=10)
    numero = models.CharField(max_length=25)
    tipo = models.CharField(max_length=20)
    limite = models.DecimalField(max_digits=10, decimal_places=2)
    ativa = models.BooleanField()


class ClientePJ(models.Model):
    codigoCliente = models.AutoField(primary_key=True)
    cnpj = models.CharField(max_length=25)
    inscricaoEstadual = models.CharField(max_length=30)
    inscricaoMunicipal = models.CharField(max_length=30)


class ClienteConta(models.Model):
    codigoCliente = models.ForeignKey(Cliente, on_delete=models.CASCADE)
    codigoConta = models.ForeignKey(Conta, on_delete=models.CASCADE)


class ClientePF(models.Model):
    codigoCliente = models.AutoField(primary_key=True)
    cpf = models.CharField(max_length=15)
    rg = models.CharField(max_length=15)


class Contato(models.Model):
    codigo = models.AutoField(primary_key=True)
    codigoCliente = models.IntegerField()
    numero = models.CharField(max_length=15)
    ramal = models.CharField(max_length=25)
    email = models.EmailField(max_length=50)
    observacao = models.CharField(max_length=50)

