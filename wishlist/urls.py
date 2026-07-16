"""URL patterns for the wishlist app."""

# Import path to define URL routes for the application.
from django.urls import path

# Import the views that handle wishlist requests.
from wishlist import views

# Define the URL patterns for the wishlist app.
urlpatterns = [
    # Route to the user's wishlist page.
    path('', views.wishlist_view, name='wishlist_view'),

    # Route to add or remove a product from the wishlist using its slug.
    path('toggle/<slug:slug>/', views.toggle_wishlist, name='toggle_wishlist'),

    # Route to move a wishlist item to the shopping cart using its UUID.
    path('move/<uuid:pk>/', views.move_to_cart, name='move_to_cart'),
]
