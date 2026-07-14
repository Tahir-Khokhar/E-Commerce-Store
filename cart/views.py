from django.shortcuts import render, redirect, get_object_or_404
from store.models import Product, Variant
from .cart import Cart


def cart_add(request, product_id):
    """Add product to cart (variant-agnostic legacy)."""
    cart = Cart(request)
    product = get_object_or_404(Product, id=product_id)
    cart.add(product=product, quantity=1)
    return redirect('cart:cart_detail')


def cart_add_variant(request, product_id, variant_id):
    """Add product variant (size+color) to cart."""
    cart = Cart(request)
    product = get_object_or_404(Product, id=product_id)
    variant = get_object_or_404(Variant, id=variant_id)
    cart.add_variant(product=product, variant=variant, quantity=1)
    return redirect('cart:cart_detail')


def cart_remove(request, product_id):
    """Remove product from cart (legacy: removes all variants for that product)."""
    cart = Cart(request)
    product = get_object_or_404(Product, id=product_id)
    cart.remove(product)
    return redirect('cart:cart_detail')


def cart_detail(request):
    """Show cart page"""
    cart = Cart(request)
    return render(request, 'cart/cart_details.html', {'cart': cart})

