from rest_framework import serializers
from .models import CustomUser, Address, Client, Account, Loan, Card, Transaction


class CustomUserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = CustomUser
        fields = ("cpf", "password")

    def create(self, validated_data):
        password = validated_data.pop("password", None)
        user = CustomUser.objects.create_user(**validated_data, password=password)
        return user


class AddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = Address
        fields = "__all__"


class ClientSerializer(serializers.ModelSerializer):
    # address = serializers.PrimaryKeyRelatedField(queryset=Address.objects.all())
    user = CustomUserSerializer(many=False,read_only = True)

    class Meta:
        model = Client
        fields = "__all__"

    def create(self, validated_data):
        user = self.context['request'].user
        name = validated_data['name']
        # photo = validated_data['photo'
        birth_date = validated_data['birth_date']
        phone = validated_data['phone']
        email = validated_data['email']
        print(user)
        print(user)
        client = Client(
            user = user,
            name = name,
            birth_date = birth_date,
            phone = phone,
            email = email
        )
        client.save()
        return client
        
        
        
        
        
        """
                        address = models.ForeignKey(Address, on_delete=models.CASCADE)
        user = models.OneToOneField(get_user_model(), on_delete=models.CASCADE, blank=True, null=True)
        name = models.CharField(max_length=100)
        photo = models.CharField(max_length=100, null=True)
        birth_date = models.DateField()
        phone = models.CharField(max_length=15)
        email = models.EmailField(max_length=50)

        """


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
    # account = serializers.PrimaryKeyRelatedField(queryset=Account.objects.all())

    class Meta:
        model = Transaction
        fields = "__all__"

    def create(self, validated_data):
        transaction = Transaction.objects.create(**validated_data)
        return transaction
