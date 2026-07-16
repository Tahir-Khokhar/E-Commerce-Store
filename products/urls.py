"""URL patterns for the products app (web pages)."""

# Import path to define URL routes for the application.
from django.urls import path

# Import the views that handle product-related web requests.
from products import views

# Define the URL patterns for the products app.
urlpatterns = [
    # Route to the home page.
    path('', views.home, name='home'),

    # Route to the product listing page.
    path('shop/', views.product_list, name='product_list'),

    # Route to the product detail page using the product slug.
    path('product/<slug:slug>/', views.product_detail, name='product_detail'),
]
