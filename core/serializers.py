from rest_framework import serializers
from .models import Endereco, Cliente, ClientePF, ClientePJ, Contato, Conta, Investimento, \
    Emprestimo, EmprestimoParcela, Cartao, Movimentacao


class EnderecoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Endereco
        fields = '__all__'


class ClienteSerializer(serializers.ModelSerializer):
    endereco = serializers.PrimaryKeyRelatedField(queryset=Endereco.objects.all())
    senha = serializers.SerializerMethodField()

    class Meta:
        model = Cliente
        fields = '__all__'

    @staticmethod
    def get_senha(obj):
        return "********"


class ClientePFSerializer(serializers.ModelSerializer):
    cliente = serializers.PrimaryKeyRelatedField(queryset=Cliente.objects.all())

    class Meta:
        extra_kwargs = {
            'cpf': {'write_only': True},
            'rg': {'write_only': True}
        }
        model = ClientePF
        fields = '__all__'


class ClientePJSerializer(serializers.ModelSerializer):
    cliente = serializers.PrimaryKeyRelatedField(queryset=Cliente.objects.all())

    class Meta:
        extra_kwargs = {
            'cnpj': {'write_only': True},
            'inscricao_estadual': {'write_only': True},
            'inscricao_municipal': {'write_only': True}
        }
        model = ClientePJ
        fields = '__all__'


class ContatoSerializer(serializers.ModelSerializer):
    cliente = serializers.PrimaryKeyRelatedField(queryset=Cliente.objects.all())

    class Meta:
        extra_kwargs = {
            'email': {'write_only': True}
        }
        model = Contato
        fields = '__all__'


class ContaSerializer(serializers.ModelSerializer):
    cliente = serializers.PrimaryKeyRelatedField(queryset=Cliente.objects.all())

    class Meta:
        model = Conta
        fields = '__all__'


class InvestimentoSerializer(serializers.ModelSerializer):
    conta = serializers.PrimaryKeyRelatedField(queryset=Conta.objects.all())

    class Meta:
        model = Investimento
        fields = '__all__'


class EmprestimoSerializer(serializers.ModelSerializer):
    conta = serializers.PrimaryKeyRelatedField(queryset=Conta.objects.all())

    class Meta:
        model = Emprestimo
        fields = '__all__'


class EmprestimoParcelaSerializer(serializers.ModelSerializer):
    emprestimo = serializers.PrimaryKeyRelatedField(queryset=Emprestimo.objects.all())

    class Meta:
        model = EmprestimoParcela
        fields = '__all__'


class CartaoSerializer(serializers.ModelSerializer):
    conta = serializers.PrimaryKeyRelatedField(queryset=Conta.objects.all())
    numero = serializers.SerializerMethodField()
    cvv = serializers.SerializerMethodField()

    class Meta:
        model = Cartao
        fields = '__all__'

    @staticmethod
    def get_numero(obj):
        return "****************"

    @staticmethod
    def get_cvv(obj):
        return "***"


class MovimentacaoSerializer(serializers.ModelSerializer):
    conta = serializers.PrimaryKeyRelatedField(queryset=Conta.objects.all())

    class Meta:
        model = Movimentacao
        fields = '__all__'

    def create(self, validated_data):
        # Aqui você pode criar uma nova instância de Movimentacao
        movimentacao = Movimentacao.objects.create(**validated_data)
        return movimentacao
