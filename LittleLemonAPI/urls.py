from django.urls import path
from . import views

urlpatterns = [
    path('menu-items', views.MenuItemView.as_view()),
    path('categories-items', views.CategoriesView.as_view()),
    path('menu-items/<int:pk>', views.SingleMenuItem.as_view()),
    path('groups/manager/user',views.manager ),
    path('groups/delivery/user', views.delivery),
    path('cart/menu-items', views.CartView.as_view()),
    path('order/', views.OrderView.as_view()),
    path('order/<int:pk>', views.SingleOrderView.as_view())
]