from django.shortcuts import render
from .serializers import MenuItemSerializer, CategorySerializer, CartSerializer, OrderSerializer, OrderItemSerializer
from .models import MenuItem, Category, Cart, Order, OrderItem
from rest_framework import generics, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAdminUser, AllowAny, IsAuthenticated
from django.shortcuts import get_object_or_404
from django.contrib.auth.models import User, Group
from rest_framework.response import Response
from .permissions import IsManager
# Create your views here.

class CategoriesView(generics.ListCreateAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [IsAdminUser]
    def get_permissions(self):
        permission_classes =[]
        if self.request.method != 'GET':
            permission_classes = [IsAdminUser]
            return [permission() for permission in permission_classes]
        else:
            permission_classes = [IsAuthenticated]
            return [permission() for permission in permission_classes]
    
    

class MenuItemView(generics.ListCreateAPIView):
    queryset = MenuItem.objects.all()
    serializer_class = MenuItemSerializer
    search_fields = ['category__title']
    ordering_fields = ['price']

    def get_permissions(self):
        permission_classes =[]
        if self.request.method != 'GET':
            permission_classes = [IsAdminUser]
            return [permission() for permission in permission_classes]
        elif self.request.method == 'PATCH':
            permission_classes = [IsAdminUser | IsManager]
            return [permission() for permission in permission_classes]
        else:
            permission_classes = [IsAuthenticated]
            return [permission() for permission in permission_classes]


class SingleMenuItem(generics.RetrieveUpdateDestroyAPIView):
    queryset = MenuItem.objects.all()
    serializer_class = MenuItemSerializer
    def get_permissions(self):
        permission_classes =[]
        if self.request.method != 'GET':
            permission_classes = [IsAdminUser | IsManager]
        return [permission() for permission in permission_classes]
    
class CartView(generics.ListCreateAPIView):
    queryset = Cart.objects.all() 
    serializer_class = CartSerializer

    def create(self, request, *args, **kwargs):
        cart_items = Cart.objects.filter(user=self.request.user)
        if cart_items.count() == 0:
            return Response({"mesaage" : "no item in the cart"})

    def get_queryset(self):
        return Cart.objects.all().filter(user=self.request.user)
    
    def delete(self, request, *args, **kwargs):
        Cart.objects.all().filter(user=self.request.user).delete()
        return Response("ok")
    
class OrderView(generics.ListCreateAPIView):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    #check user and reurn the queryset appropriate with that user
    def get_queryset(self):
        user = self.request.user
        if user.is_superuser:
            return Order.objects.all()
        if user.groups.filter(name = 'delivery crew').exists():
            return Order.objects.filter(delivery_crew=user)
        if user.groups.count() == 0:
            return Order.objects.filter(user=user)
        else:
            return Order.objects.all()
        
    #avorride the create method to add items of the user to the cart
    def create(self, request, *args, **kwargs):
        cart_items = Cart.objects.filter(user=self.request.user)
        if cart_items.count() == 0:
            return Response({"mesaage" : "no item in the cart"})
        
        data = request.data.copy()
        total = self.get_total_price(self.request.user)
        data['total'] = total
        data['user'] = self.request.user.id
        order_serializer = OrderSerializer(data = data)

        if not order_serializer.is_valid():
            return Response(order_serializer.errors, status=400)

        order = order_serializer.save()
        order_items = [
            OrderItem(
                order=order,
                menuitem_id = item.menuitem.id,
                price= item.price,
                quantity= item.quantity,
            )
            for item in cart_items
        ]
        OrderItem.objects.bulk_create(order_items)
        cart_items.delete()
        result = order_serializer.data.copy()
        result['total'] = total
        return Response(result)
        
    def get_total_price(self, user):
        total = 0
        items = Cart.objects.all().filter(user=user).all()
        for item in items.values():
            total += item['price']
        return total

class SingleOrderView(generics.RetrieveUpdateAPIView):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]

    def update(self, request, *args, **kwargs):
        if self.request.user.groups.count()==0: # Normal user, not belonging to any group = Customer
            return Response({"error":"not authorized"}, status=status.HTTP_403_FORBIDDEN)
        else: #everyone else - Super Admin, Manager and Delivery Crew
            return super().update(request, *args, **kwargs)

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


@api_view(['POST', 'DELETE', 'GET'])
@permission_classes([IsAdminUser])
def delivery(request):
    if request.method == 'POST':
        username = request.data['username']
        if username:
            user = get_object_or_404(User, username=username)
            delivery = Group.objects.get(name= "delivery crew")
        # addes user to amanger group
            delivery.user_set.add(user)
            return Response({"message":"user has been added to the delivery"})
        #lists alll users in the group
    if request.method == 'GET':
        delivery = Group.objects.get(name= "delivery crew")
        users = delivery.user_set.all()
        user_list = [{"id": user.id, "username":user.username, "email":user.email} for user in users]
        return Response({"group" :"delivery", "users": user_list})
        # elif request.method == 'DELETE':
            # managers.user_set.remove(user)
            # return Response({"message":"user has been removed from managers"})

    return Response({"message":"error"}, status.HTTP_400_BAD_REQUEST)
