"""Custom Django REST Framework permission classes."""

from rest_framework import permissions


class IsOwnerOrReadOnly(permissions.BasePermission):
    """Allow safe methods for anyone; writes only for the owner."""

    def has_object_permission(self, request, view, obj):

        # Allow read-only methods for all users.
        if request.method in permissions.SAFE_METHODS:
            return True

        # Get the object owner from user or owner field.
        owner = getattr(obj, 'user', None)

        # Check the alternative owner field if user is missing.
        if owner is None:
            owner = getattr(obj, 'owner', None)

        # Allow access only to the object owner.
        return owner is not None and owner == request.user


class IsAdminOrReadOnly(permissions.BasePermission):
    """Allow read access to all; writes only to staff/superusers."""

    def has_permission(self, request, view):

        # Allow safe methods without permission checks.
        if request.method in permissions.SAFE_METHODS:
            return True

        # Allow write access only for staff users.
        return bool(request.user and request.user.is_staff)


class IsAdminUserOrDeny(permissions.BasePermission):
    """Only staff/superusers may access the view."""

    def has_permission(self, request, view):

        # Allow access only to staff users.
        return bool(request.user and request.user.is_staff)
