# URL patterns for the accounts web interface.

from django.urls import path  # Used to define URL routes.

# Import view functions for each page.
from accounts import views

# List of URL patterns for the accounts app.
urlpatterns = [

    # Registration page.
    path('register/', views.register_page, name='register'),

    # User login page.
    path('login/', views.login_page, name='login_page'),

    # User logout page.
    path('logout/', views.web_logout, name='web_logout'),

    # User profile page.
    path('profile/', views.profile_page, name='profile_page'),

    # Display all user addresses.
    path('addresses/', views.addresses_page, name='addresses_page'),

    # Delete an address using its UUID.
    # <uuid:pk> captures a UUID from the URL and passes it as "pk".
    path('addresses/delete/<uuid:pk>/', views.delete_address, name='delete_address'),

    # User dashboard page.
    path('dashboard/', views.dashboard_home, name='dashboard_home'),

    # Verify user email using the verification token.
    # <str:token> captures a string value from the URL.
    path('verify-email/<str:token>/', views.verify_email_page, name='verify_email'),

    # Forgot password page.
    path('forgot-password/', views.forgot_password_page, name='forgot_password'),

    # Reset password using the reset token.
    path('reset-password/<str:token>/', views.reset_password_page, name='reset_password'),
]
