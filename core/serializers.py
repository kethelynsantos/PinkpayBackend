from rest_framework import serializers
from .models import CustomUser, Address, Client, Account, Loan, Card, Transaction


class AddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = Address
        fields = '__all__'


class CustomUserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=False)

    class Meta:
        model = CustomUser
        fields = ("cpf", "password")

    def create(self, validated_data):
        password = validated_data.pop("password", None)
        user = CustomUser.objects.create_user(**validated_data, password=password)
        return user

    def update(self, instance, validated_data):
        password = validated_data.pop('password', None)
        instance = super().update(instance, validated_data)

        if password:
            instance.set_password(password)
            instance.save()

        return instance


class ClientSerializer(serializers.ModelSerializer):
    user = CustomUserSerializer(many=False, read_only=True)

    class Meta:
        model = Client
        fields = "__all__"

    def create(self, validated_data):
        user = self.context['request'].user

        # verifica se já existe um cliente para este usuário
        client = Client.objects.filter(user=user).first()
        if client:
            raise serializers.ValidationError("Cliente já existe para este usuário.")

        # campos obrigatórios
        name = validated_data['name']
        birth_date = validated_data['birth_date']
        phone = validated_data['phone']
        email = validated_data['email']

        # campo opcional
        photo = validated_data.get('photo', None)

        # criação do cliente
        client = Client(
            user=user,
            name=name,
            photo=photo,
            birth_date=birth_date,
            phone=phone,
            email=email
        )

        # Verifica se há dados para o endereço
        address_data = validated_data.get('address', None)
        if address_data:
            address_serializer = AddressSerializer(data=address_data)
            address_serializer.is_valid(raise_exception=True)
            address = address_serializer.save()
            client.address = address

        client.save()
        return client


class AccountSerializer(serializers.ModelSerializer):
    client = serializers.PrimaryKeyRelatedField(queryset=Client.objects.all())

    class Meta:
        model = Account
        fields = "__all__"


class LoanSerializer(serializers.ModelSerializer):
    account = serializers.PrimaryKeyRelatedField(queryset=Account.objects.all())

    class Meta:
        model = Loan
        fields = "__all__"


class CardSerializer(serializers.ModelSerializer):
    account = serializers.PrimaryKeyRelatedField(queryset=Account.objects.all())
    number = serializers.SerializerMethodField()
    cvv = serializers.SerializerMethodField()

    class Meta:
        model = Card
        fields = "__all__"

    @staticmethod
    def get_number(obj):
        return "****************"

    @staticmethod
    def get_cvv(obj):
        return "***"


class TransactionSerializer(serializers.ModelSerializer):

    class Meta:
        model = Transaction
        fields = "__all__"

    def create(self, validated_data):
        transaction = Transaction.objects.create(**validated_data)
        return transaction
