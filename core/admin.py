from django.contrib import admin
from .models import CustomUser, Address, Client, IndividualClient, BusinessClient, Account, Loan, Card, Transaction
from django.contrib.auth.admin import UserAdmin


class CustomUserAdmin(UserAdmin):
    model = CustomUser
    list_display = ['cpf', 'is_staff', 'is_active']
    search_fields = ['cpf']
    ordering = ['cpf']


admin.site.register(CustomUser, CustomUserAdmin)


@admin.register(Address)
class AddressAdmin(admin.ModelAdmin):
    list_display = ('street', 'neighborhood', 'city', 'state')


@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    list_display = ('name', 'phone', 'email')
    search_fields = ['name', 'phone', 'email']


@admin.register(IndividualClient)
class IndividualClientAdmin(admin.ModelAdmin):
    list_display = ('cpf', 'rg')
    search_fields = ['cpf', 'rg']


@admin.register(BusinessClient)
class BusinessClientAdmin(admin.ModelAdmin):
    list_display = ('cnpj', 'corporate_name')
    search_fields = ['cnpj', 'corporate_name']


@admin.register(Account)
class AccountAdmin(admin.ModelAdmin):
    list_display = ('number', 'active')
    search_fields = ['number']


@admin.register(Loan)
class LoanAdmin(admin.ModelAdmin):
    list_display = ('requested_amount', 'approved')
    search_fields = ['requested_amount', 'approved']


@admin.register(Card)
class CardAdmin(admin.ModelAdmin):
    list_display = ('number', 'status')
    search_fields = ['number']


@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ('operation', 'amount')
    search_fields = ['operation', 'amount']
