from django.conf import settings
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponseBadRequest
from cart.cart import Cart
from .models import Order


@login_required
def checkout(request):
    cart = Cart(request)
    if len(cart) == 0:
        return redirect('store:home')

    if request.method == 'POST':
        # Create Order in DB (new schema stores shipping in Address)
        address = request.POST.get('address', '').strip()
        city = request.POST.get('city', '').strip()

        addr_obj = None
        if address or city:
            addr_obj = Order.objects.model._meta.get_field('user')  # no-op placeholder

        # Create (or attach) Address
        from .models import Address
        addr_obj = Address.objects.create(
            user=request.user,
            first_name=request.POST.get('first_name', '').strip(),
            last_name=request.POST.get('last_name', '').strip(),
            phone=request.POST.get('phone', '').strip() or '0000000000',
            line1=address,
            line2='',
            city=city,
            area='',
            postal_code='',
            is_default=True,
        )

        order = Order.objects.create(
            user=request.user,
            billing_address=addr_obj,
            total_amount=cart.get_total_price(),
        )

        # Get or create a default Size and Color to build a fallback Variant
        from store.models import Size, Color, Variant
        size, _ = Size.objects.get_or_create(label='Default')
        color, _ = Color.objects.get_or_create(name='Default', hex_code='#000000')
        default_variant, _ = Variant.objects.get_or_create(size=size, color=color)

        # Save Order Items
        from .models import OrderItem
        for item in cart:
            OrderItem.objects.create(
                order=order,
                product=item['product'],
                variant_size=default_variant,
                quantity=item['quantity'],
                unit_price=item['price'],
                line_total=item['total_price']
            )

        order.save()

        # Mark as paid using a Pakistan/offline method selected by user.
        payment_method = request.POST.get('payment_method', 'cash_on_delivery')
        order.paid = (payment_method in ['cash_on_delivery', 'bank_transfer', 'easypaisa', 'jazzcash'])
        order.save()

        # Clear cart upon successful order placement
        cart.clear()

        # Render success immediately for offline methods.
        return render(request, 'orders/payment_success.html', {'order': order})

    return render(request, 'orders/check_out.html', {'cart': cart})


@csrf_exempt
def paymenthandler(request):
    """Offline/International payment confirmation endpoint."""
    if request.method != "POST":
        return HttpResponseBadRequest("Invalid request")

    # In a real integration, this endpoint would be called by a payment gateway.
    # For this project, accept a simple status update.
    order_id = request.POST.get('order_id')
    status = request.POST.get('status', 'failed')  # paid / failed

    if not order_id:
        return HttpResponseBadRequest("Missing order_id")

    try:
        order = Order.objects.get(id=order_id)
    except Order.DoesNotExist:
        return HttpResponseBadRequest("Order not found")

    if status == 'paid':
        order.paid = True
        order.save()
        Cart(request).clear()
        return render(request, 'orders/payment_success.html', {'order': order})

    return HttpResponseBadRequest("Payment failed")

@login_required
def my_orders(request):
    orders = Order.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'orders/my_orders.html', {'orders': orders})


@login_required
def order_detail(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    return render(request, 'orders/order_detail.html', {'order': order})
