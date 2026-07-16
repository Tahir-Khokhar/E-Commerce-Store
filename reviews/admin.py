"""Admin registration for the reviews app."""

# Import Django's admin module to register and configure models in the admin site.
from django.contrib import admin

# Import the review-related models to be managed through the admin interface.
from reviews.models import Review, ReviewHelpfulVote


# Register the Review model with a custom admin configuration.
@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    """Admin configuration for reviews."""

    # Display these fields in the reviews list page.
    list_display = (
        'product', 'user', 'rating', 'status',
        'is_verified_purchase', 'helpful_votes', 'created_at',
    )

    # Add sidebar filters for quick review filtering.
    list_filter = ('status', 'is_verified_purchase', 'rating')

    # Enable searching by product name, user email, review title, and comment.
    search_fields = ('product__name', 'user__email', 'title', 'comment')

    # Make these fields read-only in the admin form.
    readonly_fields = ('created_at', 'updated_at', 'helpful_votes')

    # Register custom bulk actions.
    actions = ['approve_reviews', 'reject_reviews']

    # Register this method as an admin action with a custom description.
    @admin.action(description='Approve selected reviews')
    def approve_reviews(self, request, queryset):
        # Update all selected reviews to the approved status.
        queryset.update(status='approved')

    # Register this method as an admin action with a custom description.
    @admin.action(description='Reject selected reviews')
    def reject_reviews(self, request, queryset):
        # Update all selected reviews to the rejected status.
        queryset.update(status='rejected')


# Register the ReviewHelpfulVote model with a custom admin configuration.
@admin.register(ReviewHelpfulVote)
class ReviewHelpfulVoteAdmin(admin.ModelAdmin):
    """Admin configuration for helpful votes."""

    # Display these fields in the helpful votes list page.
    list_display = ('review', 'user', 'created_at')

    # Enable searching by user email and review title.
    search_fields = ('user__email', 'review__title')
