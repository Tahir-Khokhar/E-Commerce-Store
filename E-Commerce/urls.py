urlpatterns = [
    path('admin/', admin.site.urls),
    
    # Store App
    path('', include('store.urls')),
    
    # Cart App
    path('cart/', include('cart.urls')),
    
    # Orders & Payment
    path('orders/', include('orders.urls')),
    
    # Accounts app (register)
    path('accounts/', include('accounts.urls', namespace='accounts')),

