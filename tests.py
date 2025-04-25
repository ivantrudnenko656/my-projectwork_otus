from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User
from .models import Category, Product, Cart, CartItem


class CategoryModelTest(TestCase):
    def test_category_creation(self):
        category = Category.objects.create(name='Electronics', slug='electronics')
        self.assertEqual(str(category), 'Electronics')


class ProductModelTest(TestCase):
    def setUp(self):
        self.category = Category.objects.create(name='Electronics', slug='electronics')

    def test_product_creation(self):
        product = Product.objects.create(
            category=self.category,
            name='Test Product',
            slug='test-product',
            description='Test description',
            price=99.99,
            stock=10
        )
        self.assertEqual(str(product), 'Test Product')
        self.assertEqual(product.price, 99.99)


class CartModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='12345')
        self.category = Category.objects.create(name='Electronics', slug='electronics')
        self.product = Product.objects.create(
            category=self.category,
            name='Test Product',
            slug='test-product',
            description='Test description',
            price=99.99,
            stock=10
        )

    def test_cart_creation(self):
        cart = Cart.objects.create(user=self.user)
        cart_item = CartItem.objects.create(cart=cart, product=self.product, quantity=2)

        self.assertEqual(cart.items.count(), 1)
        self.assertEqual(cart.get_total_price(), 199.98)


class HomePageViewTest(TestCase):
    def test_view_url_exists_at_desired_location(self):
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)

    def test_view_uses_correct_template(self):
        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'store/index.html')