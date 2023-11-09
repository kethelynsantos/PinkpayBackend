from django.contrib import admin
from .models import Endereco, Cliente, ClientePF, ClientePJ, Contato, Conta, Emprestimo, \
    Cartao, Movimentacao


@admin.register(Endereco)
class EnderecoAdmin(admin.ModelAdmin):
    list_display = ('bairro', 'cidade', 'uf')


@admin.register(Cliente)
class ClienteAdmin(admin.ModelAdmin):
    list_display = ('nome', 'usuario')


@admin.register(ClientePF)
class ClientePFAdmin(admin.ModelAdmin):
    list_display = ('cpf', 'rg')


@admin.register(ClientePJ)
class ClientePJAdmin(admin.ModelAdmin):
    list_display = ('cnpj', 'razao_social')


@admin.register(Contato)
class ContatoAdmin(admin.ModelAdmin):
    list_display = ('numero', 'email')


@admin.register(Conta)
class ContaAdmin(admin.ModelAdmin):
    list_display = ('numero', 'ativa')


@admin.register(Emprestimo)
class EmprestimoAdmin(admin.ModelAdmin):
    list_display = ('valor_solicitado', 'aprovado')


@admin.register(Cartao)
class CartaoAdmin(admin.ModelAdmin):
    list_display = ('numero', 'situacao')


@admin.register(Movimentacao)
class MovimentacaoAdmin(admin.ModelAdmin):
    list_display = ('operacao', 'valor')
