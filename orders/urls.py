# URL patterns for the categories app (web pages).

from django.urls import path  # Used to define URL routes.

# Import view functions for the categories app.
from categories import views

# List of URL patterns.
urlpatterns = [

    # Display the list of all categories.
    path(
        'categories/',
        views.category_list,
        name='category_list'
    ),

    # Display details for a single category.
    # <slug:slug> captures the category slug from the URL.
    path(
        'category/<slug:slug>/',
        views.category_detail,
        name='category_detail'
    ),
]
