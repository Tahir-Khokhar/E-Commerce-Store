# API-specific permissions.

# Import custom permission classes from the core app.
from core.permissions import (
    IsOwnerOrReadOnly,
    IsAdminOrReadOnly,
    IsAdminUserOrDeny,
)

# __all__ specifies which permission classes are exported
# when using: from module import *
__all__ = [
    'IsOwnerOrReadOnly',
    'IsAdminOrReadOnly',
    'IsAdminUserOrDeny',
]
