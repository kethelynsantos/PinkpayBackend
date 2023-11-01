from django.contrib import admin
from .models import Endereco, Cliente, ClientePF, ClientePJ, Contato, Conta, Investimento, Emprestimo, \
    EmprestimoParcela, Cartao, Movimentacao


@admin.register(Endereco)
class EnderecoAdmin(admin.ModelAdmin):
    list_display = ('logradouro', 'bairro', 'cidade', 'uf', 'cep')


@admin.register(Cliente)
class ClienteAdmin(admin.ModelAdmin):
    list_display = ('razao_social', 'social_fantasia', 'usuario')


@admin.register(ClientePF)
class ClientePFAdmin(admin.ModelAdmin):
    list_display = ('cpf', 'rg')


@admin.register(ClientePJ)
class ClientePJAdmin(admin.ModelAdmin):
    list_display = ('cnpj', 'inscricao_estadual', 'inscricao_municipal')


@admin.register(Contato)
class ContatoAdmin(admin.ModelAdmin):
    list_display = ('numero', 'email')


@admin.register(Conta)
class ContaAdmin(admin.ModelAdmin):
    list_display = ('agencia', 'numero', 'ativa')


@admin.register(Investimento)
class InvestimentoAdmin(admin.ModelAdmin):
    list_display = ('tipo', 'taxa_adm', 'rentabilidade')


@admin.register(Emprestimo)
class EmprestimoAdmin(admin.ModelAdmin):
    list_display = ('valor_solicitado', 'aprovado')


@admin.register(EmprestimoParcela)
class EmprestimoParcelaAdmin(admin.ModelAdmin):
    list_display = ('numero', 'data_pagamento', 'valor_parcela')


@admin.register(Cartao)
class CartaoAdmin(admin.ModelAdmin):
    list_display = ('numero', 'cvv', 'situacao')


@admin.register(Movimentacao)
class MovimentacaoAdmin(admin.ModelAdmin):
    list_display = ('operacao', 'valor')
