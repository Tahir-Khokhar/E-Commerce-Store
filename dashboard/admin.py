# Import Django admin tools.
from django.contrib import admin
# Import the dashboard snapshot model.
from .models import DashboardSnapshot


# Register the dashboard snapshot model in admin panel.
@admin.register(DashboardSnapshot)
class DashboardSnapshotAdmin(admin.ModelAdmin):
    # Display these fields in the admin list view.
    list_display = ["id", "key", "created_at"]

    # Enable searching by snapshot key.
    search_fields = ["key"]
