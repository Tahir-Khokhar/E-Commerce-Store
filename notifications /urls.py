"""URL patterns for the notifications app."""

# Import path to define URL routes for the application.
from django.urls import path

# Import the views that handle notification-related requests.
from notifications import views

# Define the URL patterns for the notifications app.
urlpatterns = [
    # Route to display the user's notifications.
    path('', views.notifications_view, name='notifications_view'),

    # Route to mark a specific notification as read using its UUID.
    path('read/<uuid:pk>/', views.mark_read, name='mark_notification_read'),

    # Route to mark all notifications as read.
    path('read-all/', views.mark_all_read, name='mark_all_read'),
]
