from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from djoser.views import UserViewSet as DjoserUserViewSet
from django_filters import rest_framework as filters
from core import serializers, models


class CustomUserViewSet(DjoserUserViewSet):
    # /api/v1/customuser/register/
    # Custom action for user registration
    @action(detail=False, methods=['post'])
    def register(self, request):
        """
        Register a new user.
        Expects a POST request with client data.
        """
        serializer = serializers.CustomUserSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class ClientViewSet(viewsets.ModelViewSet):
    serializer_class = serializers.ClientSerializer
    queryset = models.Client.objects.all()
    filter_backends = (filters.DjangoFilterBackend, )
    filterset_fields = ('user',)
    search_fields = ('user') 
    

    # http://127.0.0.1:8000/api/v1/client?user=1

    # Custom action for client registration
    # @action(detail=False, methods=['post'])
    # def register(self, request):
    #     """
    #     Register a new client.
    #     Expects a POST request with client data.
    #     """
    #     serializer = serializers.ClientSerializer(data=request.data)
    #     serializer.is_valid(raise_exception=True)
    #     self.perform_create(serializer)
    #     return Response(serializer.data, status=status.HTTP_201_CREATED)

    # # Custom action to retrieve transactions for a specific client
    # @action(detail=True, methods=['get'])
    # def transactions(self, request, pk=None):
    #     """
    #     Retrieve transactions for a specific client.
    #     Expects a GET request.
    #     """
    #     client = self.get_object()
    #     serializer = serializers.TransactionSerializer(client.transactions.all(), many=True)
    #     return Response(serializer.data)

    # actions = {'get': 'list', 'post': 'create'}
