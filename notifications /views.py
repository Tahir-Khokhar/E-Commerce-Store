"""Views and API endpoints for notifications."""

# Import helper functions for object retrieval, redirects, and template rendering.
from django.shortcuts import get_object_or_404, redirect, render

# Import DRF permissions, HTTP status codes, and viewset base classes.
from rest_framework import permissions, status, viewsets

# Import APIView for creating class-based API endpoints.
from rest_framework.views import APIView

# Import Response to return API responses.
from rest_framework.response import Response

# Import the Notification model used by the views.
from notifications.models import Notification

# Import the serializer used to serialize notification objects.
from notifications.serializers import NotificationSerializer

# Import the custom admin permission class.
from core.permissions import IsAdminUserOrDeny


# Read-only API viewset for user notifications.
class NotificationViewSet(viewsets.ReadOnlyModelViewSet):
    """List the current user's notifications."""

    # Specify the serializer used for notification objects.
    serializer_class = NotificationSerializer

    # Require users to be authenticated.
    permission_classes = (permissions.IsAuthenticated,)

    # Return only notifications belonging to the authenticated user.
    def get_queryset(self):
        return Notification.objects.filter(user=self.request.user)

    # Retrieve a notification, mark it as read, and return its updated status.
    def retrieve(self, request, *args, **kwargs):
        # Retrieve the notification or return a 404 if it does not belong to the user.
        notification = get_object_or_404(Notification, pk=kwargs['pk'], user=request.user)

        # Mark the notification as read.
        notification.read = True

        # Save only the updated read field.
        notification.save(update_fields=['read'])

        # Return a simple confirmation response.
        return Response({'id': str(notification.id), 'read': True})


# API endpoint for marking all notifications as read.
class MarkAllReadAPIView(APIView):
    """Mark all of the user's notifications as read."""

    # Require users to be authenticated.
    permission_classes = (permissions.IsAuthenticated,)

    # Handle POST requests.
    def post(self, request):
        # Update all unread notifications for the current user.
        Notification.objects.filter(user=request.user, read=False).update(read=True)

        # Return a success message.
        return Response({'detail': 'All notifications marked as read.'})


# Render the notifications page.
def notifications_view(request):
    """Render the user's notifications."""

    # Redirect unauthenticated users to the login page.
    if not request.user.is_authenticated:
        return redirect('login_page')

    # Retrieve all notifications for the current user.
    notifications = Notification.objects.filter(user=request.user)

    # Count the number of unread notifications.
    unread = notifications.filter(read=False).count()

    # Render the notifications template with the required context.
    return render(
        request, 'notifications/list.html',
        {'notifications': notifications, 'unread': unread},
    )


# Mark a single notification as read.
def mark_read(request, pk):
    """Mark a single notification as read."""

    # Update the matching notification if it belongs to the current user.
    Notification.objects.filter(pk=pk, user=request.user).update(read=True)

    # Redirect back to the notifications page.
    return redirect('notifications_view')


# Mark all notifications as read.
def mark_all_read(request):
    """Mark all notifications as read."""

    # Update all unread notifications for the current user.
    Notification.objects.filter(user=request.user, read=False).update(read=True)

    # Redirect back to the notifications page.
    return redirect('notifications_view')
