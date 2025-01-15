from django.shortcuts import render
from .serializers import MenuItemSerializer, CategorySerializer
from .models import MenuItem, Category
from rest_framework import generics, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAdminUser
from django.shortcuts import get_object_or_404
from django.contrib.auth.models import User, Group
from rest_framework.response import Response
# Create your views here.

class CategoriesView(generics.ListCreateAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer


class MenuItemView(generics.ListCreateAPIView):
    queryset = MenuItem.objects.all()
    serializer_class = MenuItemSerializer

@api_view(['POST', 'DELETE', 'GET'])
@permission_classes([IsAdminUser])
def manager(request):
    username = request.data['username']
    if username:
        user = get_object_or_404(User, username=username)
        managers = Group.objects.get(name= "Manager")
        # addes user to amanger group
        if request.method == 'POST':
            managers.user_set.add(user)
            return Response({"message":"user has been added to managers"})
        #lists alll users in the group
        if request.method == 'GET':
            users = managers.user_set.all()
            user_list = [{"id": user.id, "username":user.username, "email":user.email} for user in users]
            return Response({"group" :"manager", "users": user_list})
        # elif request.method == 'DELETE':
            # managers.user_set.remove(user)
            # return Response({"message":"user has been removed from managers"})

    return Response({"message":"error"}, status.HTTP_400_BAD_REQUEST)


