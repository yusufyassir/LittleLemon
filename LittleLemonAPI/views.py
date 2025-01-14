from django.shortcuts import render
from .serializers import MenuItemSerializer, CategorySerializer
from .models import MenuItem, Category
from rest_framework import response , generics
# Create your views here.

class CategoriesView(generics.ListCreateAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer


class MenuItemView(generics.ListCreateAPIView):
    queryset = MenuItem.objects.all()
    serializer_class = MenuItemSerializer
