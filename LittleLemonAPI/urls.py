from django.urls import path
from . import views

urlpatterns = [
    path('menu-items', views.MenuItemView.as_view()),
    path('categories-items', views.CategoriesView.as_view()),
    path('menu-items/<int:pk>', views.SingleMenuItem.as_view()),
    path('manager/user',views.manager )
]