from django.urls import path
from . import views

app_name = 'cart'

urlpatterns = [
    path('', views.cart_detail, name='cart_detail'),
    path('add/<int:product_id>/', views.cart_add, name='cart_add'),
    # Variant-aware add (size+color)
    path('add/<int:product_id>/<int:variant_id>/', views.cart_add_variant, name='cart_add_variant'),
    path('remove/<int:product_id>/', views.cart_remove, name='cart_remove'),
]

