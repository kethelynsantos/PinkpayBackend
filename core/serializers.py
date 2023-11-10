from rest_framework import serializers
from .models import CustomUser, Address, Client, IndividualClient, BusinessClient, Account, \
    Loan, Card, Transaction


class CustomUserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = CustomUser
        fields = ('cpf', 'password')

    def create(self, validated_data):
        password = validated_data.pop('password', None)
        user = CustomUser.objects.create_user(**validated_data, password=password)
        return user


class AddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = Address
        fields = '__all__'


class ClientSerializer(serializers.ModelSerializer):
    # address = serializers.PrimaryKeyRelatedField(queryset=Address.objects.all())

    class Meta:
        model = Client
        fields = '__all__'


class IndividualClientSerializer(serializers.ModelSerializer):
    client = serializers.PrimaryKeyRelatedField(queryset=Client.objects.all())

    class Meta:
        extra_kwargs = {
            'cpf': {'write_only': True},
            'rg': {'write_only': True}
        }
        model = IndividualClient
        fields = '__all__'


class BusinessClientSerializer(serializers.ModelSerializer):
    client = serializers.PrimaryKeyRelatedField(queryset=Client.objects.all())

    class Meta:
        extra_kwargs = {
            'state_registration': {'write_only': True},
            'municipal_registration': {'write_only': True}
        }
        model = BusinessClient
        fields = '__all__'


class AccountSerializer(serializers.ModelSerializer):
    client = serializers.PrimaryKeyRelatedField(queryset=Client.objects.all())

    class Meta:
        model = Account
        fields = '__all__'


class LoanSerializer(serializers.ModelSerializer):
    account = serializers.PrimaryKeyRelatedField(queryset=Account.objects.all())

    class Meta:
        model = Loan
        fields = '__all__'


class CardSerializer(serializers.ModelSerializer):
    account = serializers.PrimaryKeyRelatedField(queryset=Account.objects.all())
    number = serializers.SerializerMethodField()
    cvv = serializers.SerializerMethodField()

    class Meta:
        model = Card
        fields = '__all__'

    @staticmethod
    def get_number(obj):
        return "****************"

    @staticmethod
    def get_cvv(obj):
        return "***"


class TransactionSerializer(serializers.ModelSerializer):
    # account = serializers.PrimaryKeyRelatedField(queryset=Account.objects.all())

    class Meta:
        model = Transaction
        fields = '__all__'

    def create(self, validated_data):
        transaction = Transaction.objects.create(**validated_data)
        return transaction
