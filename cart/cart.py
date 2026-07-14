from decimal import Decimal
from django.conf import settings

class Cart:
    def __init__(self, request):
        """Initialize the cart"""
        self.session = request.session
        cart = self.session.get(settings.CART_SESSION_ID)
        if not cart:
            cart = self.session[settings.CART_SESSION_ID] = {}
        self.cart = cart

    # ---------------- Legacy product-only cart ----------------
    def add(self, product, quantity=1, override_quantity=False):
        """Add product to cart or update quantity (variant-agnostic)."""
        product_id = str(product.id)
        if product_id not in self.cart:
            self.cart[product_id] = {
                'quantity': 0,
                'price': str(product.price),
            }

        if override_quantity:
            self.cart[product_id]['quantity'] = quantity
        else:
            self.cart[product_id]['quantity'] += quantity

        self.save()

    def remove(self, product):
        """Remove product from cart (legacy: removes all variants for that product)."""
        product_id = str(product.id)
        if product_id in self.cart:
            del self.cart[product_id]
            self.save()

    # ---------------- Variant-aware cart ----------------
    def add_variant(self, product, variant, quantity=1, override_quantity=False):
        """Add a specific variant (size+color) to cart."""
        cart_key = f"{product.id}:{variant.id}"

        if cart_key not in self.cart:
            self.cart[cart_key] = {
                'quantity': 0,
                'price': str(product.price),
                'product_id': str(product.id),
                'variant_id': str(variant.id),
            }

        if override_quantity:
            self.cart[cart_key]['quantity'] = quantity
        else:
            self.cart[cart_key]['quantity'] += quantity

        self.save()

    def save(self):
        """Mark session as modified"""
        self.session.modified = True

    # ---------------- Iteration helpers ----------------
    def __iter__(self):
        """Iterate over items in cart"""
        from store.models import Product, Variant

        keys = list(self.cart.keys())
        product_ids = set()
        variant_ids = set()
        for k in keys:
            if ':' in k:
                _, variant_id = k.split(':', 1)
                pid, _vid = k.split(':', 1)
                product_ids.add(pid)
                variant_ids.add(variant_id)
            else:
                product_ids.add(k)

        products = Product.objects.filter(id__in=product_ids)
        variants = Variant.objects.filter(id__in=variant_ids) if variant_ids else Variant.objects.none()

        product_map = {str(p.id): p for p in products}
        variant_map = {str(v.id): v for v in variants}

        cart = self.cart.copy()

        for k, item in cart.items():
            pid = item.get('product_id') or (k.split(':', 1)[0] if ':' in k else k)
            vid = item.get('variant_id') or (k.split(':', 1)[1] if ':' in k else None)

            item['product'] = product_map.get(str(pid))
            item['variant'] = variant_map.get(str(vid)) if vid else None

            item['price'] = Decimal(item['price'])
            item['total_price'] = item['price'] * item['quantity']

        for item in cart.values():
            yield item

    def __len__(self):
        """Count total items in cart"""
        return sum(item['quantity'] for item in self.cart.values())

    def get_total_price(self):
        """Calculate total price"""
        return sum(Decimal(item['price']) * item['quantity'] for item in self.cart.values())

    def clear(self):
        """Clear the cart"""
        del self.session[settings.CART_SESSION_ID]
        self.save()

