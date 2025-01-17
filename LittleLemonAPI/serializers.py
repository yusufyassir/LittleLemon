from rest_framework import serializers
from .models import Cart, Category, MenuItem, Order, OrderItem
from django.contrib.auth import get_user_model

User = get_user_model()

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'title', 'slug']

class MenuItemSerializer(serializers.ModelSerializer):
    category = serializers.PrimaryKeyRelatedField(
        queryset=Category.objects.all()
    )

    class Meta:
        model = MenuItem
        fields = ['id', 'title', 'price', 'featured', 'category']

    

class CartSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(queryset= User.objects.all())
    menuitem = serializers.PrimaryKeyRelatedField(queryset = MenuItem.objects.all())

    unit_price = serializers.DecimalField(max_digits=6, decimal_places=2, read_only=True)
    price = serializers.DecimalField(max_digits=6, decimal_places=2, read_only=True)

    class Meta:
        model = Cart
        fields = ['id', 'user', 'menuitem', 'quantity', 'unit_price', 'price']

    def create(self, validated_data):
        menuitem = validated_data.pop('menuitem')
        user = validated_data['user']
        
        # Price calculation
        unit_price = menuitem.price
        quantity = validated_data['quantity']
        price = unit_price * quantity
        
        # Create and return the cart item
        cart_item = Cart.objects.create(
            menuitem=menuitem,
            # user=user,
            unit_price=unit_price,
            price=price,
            **validated_data
        )
        return cart_item
    
    def update(self, instance, validated_data):
        menuitem = validated_data.pop('menuitem', None)
        if menuitem:
            instance.menuitem = menuitem
            instance.unit_price = menuitem.price
        
        instance.quantity = validated_data.get('quantity', instance.quantity)
        instance.price = instance.unit_price * instance.quantity  # Recalculate price
        
        instance.save()
        return instance
    

class OrderSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())
    delivery_crew = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.filter(groups__name='delivery crew'), required=False
    )

    class Meta:
        model = Order
        fields = ['id', 'user', 'delivery_crew', 'status', 'total', 'date']


class OrderItemSerializer(serializers.ModelSerializer):
    order = serializers.PrimaryKeyRelatedField(queryset=Order.objects.all())
    menuitem = serializers.PrimaryKeyRelatedField(queryset=MenuItem.objects.all())

    class Meta:
        model = OrderItem
        fields = ['id', 'order', 'menuitem', 'quantity', 'unit_price', 'price']