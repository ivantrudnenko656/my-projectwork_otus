from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login
from django.contrib import messages
from django.db.models import Q
from django.urls import reverse
from .models import Category, Product, Cart, CartItem, Order, OrderItem, UserProfile
from .forms import UserProfileForm, OrderCreateForm


def get_or_create_cart(request):
    """Helper function to get or create a cart based on user login status"""
    if request.user.is_authenticated:
        cart, created = Cart.objects.get_or_create(user=request.user)
    else:
        session_key = request.session.session_key
        if not session_key:
            request.session.save()
            session_key = request.session.session_key

        cart, created = Cart.objects.get_or_create(session_id=session_key)

    return cart


def index(request):
    """View for the home page"""
    latest_products = Product.objects.filter(available=True)[:8]
    featured_categories = Category.objects.all()[:4]

    return render(request, 'store/index.html', {
        'latest_products': latest_products,
        'featured_categories': featured_categories,
    })


def product_list(request, category_slug=None):
    """View for the product listing page"""
    category = None
    categories = Category.objects.all()
    products = Product.objects.filter(available=True)

    if category_slug:
        category = get_object_or_404(Category, slug=category_slug)
        products = products.filter(category=category)

    return render(request, 'store/product_list.html', {
        'category': category,
        'categories': categories,
        'products': products,
    })


def product_detail(request, id, slug):
    """View for the product detail page"""
    product = get_object_or_404(Product, id=id, slug=slug, available=True)
    related_products = Product.objects.filter(category=product.category).exclude(id=id)[:4]

    return render(request, 'store/product_detail.html', {
        'product': product,
        'related_products': related_products,
    })


def search_products(request):
    """View for product search"""
    query = request.GET.get('q', '')
    products = Product.objects.filter(available=True)

    if query:
        products = products.filter(
            Q(name__icontains=query) |
            Q(description__icontains=query) |
            Q(category__name__icontains=query)
        ).distinct()

    return render(request, 'store/search_results.html', {
        'products': products,
        'query': query
    })


def cart_add(request, product_id):
    """Add a product to the cart"""
    product = get_object_or_404(Product, id=product_id)
    cart = get_or_create_cart(request)

    cart_item, created = CartItem.objects.get_or_create(
        cart=cart,
        product=product,
        defaults={'quantity': 1}
    )

    if not created:
        cart_item.quantity += 1
        cart_item.save()

    return redirect('cart_detail')


def cart_remove(request, item_id):
    """Remove an item from the cart"""
    cart_item = get_object_or_404(CartItem, id=item_id)
    cart_item.delete()
    return redirect('cart_detail')


def cart_update(request, item_id):
    """Update the quantity of a cart item"""
    cart_item = get_object_or_404(CartItem, id=item_id)

    quantity = int(request.POST.get('quantity', 1))
    if quantity > 0:
        cart_item.quantity = quantity
        cart_item.save()

    return redirect('cart_detail')


def cart_detail(request):
    """View for the shopping cart page"""
    cart = get_or_create_cart(request)

    return render(request, 'store/cart.html', {
        'cart': cart
    })


@login_required
def checkout(request):
    """View for the checkout process"""
    cart = get_or_create_cart(request)

    # Check if cart is empty
    if cart.items.count() == 0:
        messages.warning(request, 'Your cart is empty')
        return redirect('product_list')

    try:
        profile = request.user.userprofile
    except UserProfile.DoesNotExist:
        profile = UserProfile.objects.create(user=request.user)

    if request.method == 'POST':
        form = OrderCreateForm(request.POST)
        if form.is_valid():
            order = form.save(commit=False)
            order.user = request.user
            order.save()

            # Add items from cart to order
            for item in cart.items.all():
                OrderItem.objects.create(
                    order=order,
                    product=item.product,
                    price=item.product.price,
                    quantity=item.quantity
                )

            # Clear the cart
            cart.items.all().delete()

            # Update order total price
            order.total_price = order.get_total_cost()
            order.save()

            return redirect(reverse('order_confirmation', args=[order.id]))
    else:
        # Pre-fill form with user profile data
        initial_data = {
            'first_name': request.user.first_name,
            'last_name': request.user.last_name,
            'email': request.user.email,
            'address': profile.address,
            'postal_code': profile.postal_code,
            'city': profile.city,
        }
        form = OrderCreateForm(initial=initial_data)

    return render(request, 'store/checkout.html', {
        'cart': cart,
        'form': form,
    })


@login_required
def order_confirmation(request, order_id):
    """View for order confirmation page"""
    order = get_object_or_404(Order, id=order_id, user=request.user)

    return render(request, 'store/order_confirmation.html', {
        'order': order
    })


def register(request):
    """User registration view"""
    if request.method == 'POST':
        user_form = UserCreationForm(request.POST)
        profile_form = UserProfileForm(request.POST)

        if user_form.is_valid() and profile_form.is_valid():
            user = user_form.save()
            profile = profile_form.save(commit=False)
            profile.user = user
            profile.save()

            login(request, user)
            messages.success(request, 'Account created successfully')
            return redirect('home')
    else:
        user_form = UserCreationForm()
        profile_form = UserProfileForm()

    return render(request, 'store/register.html', {
        'user_form': user_form,
        'profile_form': profile_form
    })


@login_required
def profile(request):
    """User profile view"""
    try:
        profile = request.user.userprofile
    except UserProfile.DoesNotExist:
        profile = UserProfile.objects.create(user=request.user)

    if request.method == 'POST':
        form = UserProfileForm(request.POST, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated successfully')
            return redirect('profile')
    else:
        form = UserProfileForm(instance=profile)

    return render(request, 'store/profile.html', {'form': form})


@login_required
def order_history(request):
    """View for user's order history"""
    orders = Order.objects.filter(user=request.user).order_by('-created')

    return render(request, 'store/order_history.html', {
        'orders': orders
    })