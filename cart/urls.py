# URL patterns for the cart app (web pages).

from django.urls import path  # Used to define URL routes.

# Import view functions for the cart app.
from cart import views

# List of URL patterns for the cart app.
urlpatterns = [

    # Display the shopping cart page.
    path('', views.cart_detail, name='cart_detail'),

    # Add a product to the cart.
    # <slug:slug> captures the product slug from the URL.
    path('add/<slug:slug>/', views.add_to_cart, name='add_to_cart'),

    # Update the quantity of a cart item.
    # <uuid:item_id> captures the cart item's UUID.
    path('update/<uuid:item_id>/', views.update_cart_item, name='update_cart_item'),

    # Remove a cart item from the cart.
    # <uuid:item_id> captures the cart item's UUID.
    path('remove/<uuid:item_id>/', views.remove_cart_item, name='remove_cart_item'),
]
