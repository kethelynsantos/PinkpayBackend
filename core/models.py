from django.db import models


class Endereco(models.Model):
    id = models.AutoField(primary_key=True)
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
    id = models.AutoField(primary_key=True)
    id_endereco = models.ForeignKey(Endereco, on_delete=models.CASCADE)
    razao_social = models.CharField(max_length=100)
    social_fantasia = models.CharField(max_length=100)
    foto = models.CharField(max_length=100)
    data_nascimento = models.DateField()
    usuario = models.CharField(max_length=10)
    senha = models.IntegerField()

    class Meta:
        verbose_name = 'Cliente'
        verbose_name_plural = 'Clientes'

    def __str__(self):
        return f'{self.razao_social}, {self.social_fantasia}'


class ClientePF(models.Model):
    id_cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE)
    cpf = models.CharField(max_length=15)
    rg = models.CharField(max_length=15)

    class Meta:
        verbose_name = 'ClientePF'
        verbose_name_plural = 'ClientesPF'

    def __str__(self):
        return f'{self.cpf}, {self.rg}'


class ClientePJ(models.Model):
    id_cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE)
    cnpj = models.CharField(max_length=25)
    inscricao_estadual = models.CharField(max_length=30)
    inscricao_municipal = models.CharField(max_length=30)

    class Meta:
        verbose_name = 'ClientePJ'
        verbose_name_plural = 'ClientesPJ'

    def __str__(self):
        return self.cnpj


class Contato(models.Model):
    id = models.AutoField(primary_key=True)
    id_cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE)
    numero = models.CharField(max_length=15)
    ramal = models.CharField(max_length=25)
    email = models.EmailField(max_length=50)
    observacao = models.CharField(max_length=50)

    class Meta:
        verbose_name = 'Contato'
        verbose_name_plural = 'Contatos'

    def __str__(self):
        return f'{self.numero}, {self.email}'


class Conta(models.Model):
    id = models.AutoField(primary_key=True)
    agencia = models.CharField(max_length=10)
    numero = models.CharField(max_length=25)
    tipo = models.CharField(max_length=20)
    limite = models.DecimalField(max_digits=10, decimal_places=2)
    ativa = models.BooleanField()
    id_cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE)

    class Meta:
        verbose_name = 'Conta'
        verbose_name_plural = 'Contas'

    def __str__(self):
        return f'{self.agencia}, {self.ativa}'


class Investimento(models.Model):
    id = models.AutoField(primary_key=True)
    id_conta = models.ForeignKey(Conta, on_delete=models.CASCADE)
    tipo = models.CharField(max_length=30)
    aporte = models.DecimalField(max_digits=10, decimal_places=2)
    taxa_adm = models.FloatField()
    prazo = models.CharField(max_length=20)
    grau_risco = models.CharField(max_length=5)
    rentabilidade = models.DecimalField(max_digits=10, decimal_places=2)
    finalizado = models.BooleanField()

    class Meta:
        verbose_name = 'Investimento'
        verbose_name_plural = 'Investimentos'

    def __str__(self):
        return f'{self.tipo}, {self.rentabilidade}'


class Emprestimo(models.Model):
    id = models.AutoField(primary_key=True)
    id_conta = models.ForeignKey(Conta, on_delete=models.CASCADE)
    data_solicitacao = models.DateField(auto_now=True)
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


class EmprestimoParcela(models.Model):
    id = models.AutoField(primary_key=True)
    id_emprestimo = models.ForeignKey(Emprestimo, on_delete=models.CASCADE)
    numero = models.IntegerField()
    data_vencimento = models.DateField()
    valor_parcela = models.DecimalField(max_digits=10, decimal_places=2)
    data_pagamento = models.DateField(null=True, blank=True)
    valor_pago = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)

    class Meta:
        verbose_name = 'EmprestimoParcela'
        verbose_name_plural = 'EmprestimosParcelas'

    def __str__(self):
        return f'{self.numero}, {self.valor_parcela}'


class Cartao(models.Model):
    id = models.AutoField(primary_key=True)
    id_conta = models.ForeignKey(Conta, on_delete=models.CASCADE)
    numero = models.CharField(max_length=30)
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
    id = models.AutoField(primary_key=True)
    id_cartao = models.ForeignKey(Cartao, on_delete=models.CASCADE)
    data_hora = models.DateTimeField(auto_now=True)
    operacao = models.CharField(max_length=20)
    valor = models.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        verbose_name = 'Movimentacao'
        verbose_name_plural = 'Movimentacoes'

    def __str__(self):
        return f'{self.operacao}, {self.valor}'
