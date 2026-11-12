
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from catalog.models import Product, Category, Tag


# Testing custom admin behavior here, not Django's built-in functionality.
# Verify that related data displays correctly and products can be created
class ProductAdminTests(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.admin_user = get_user_model().objects.create_superuser(
            username="admin",
            email="admin@example.com",
            password="testpassword123"
        )

        cls.category = Category.objects.create(name="Cables")
        cls.tag1 = Tag.objects.create(name="Copper")
        cls.tag2 = Tag.objects.create(name="Outdoor")

        cls.product = Product.objects.create(
            name="Copper Cable",
            description="Copper cable for electrical installations",
            sku="CAB-001",
            category=cls.category
        )
        cls.product.tags.add(cls.tag1, cls.tag2)

    def setUp(self):
        self.client.force_login(self.admin_user)

    def test_product_list_displays_related_data(self):
        """
        test that the admin product list displays product details,
        category, and associated tags
        """
        url = reverse("admin:catalog_product_changelist")
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Copper Cable")
        self.assertContains(response, "CAB-001")
        self.assertContains(response, "Cables")
        self.assertContains(response, "Copper, Outdoor")

    def test_product_can_be_created_through_admin(self):
        """
        test that the admin can create a product with a category
        and multiple tags
        """
        url = reverse("admin:catalog_product_add")

        data = {
            "name": "Outdoor Wire",
            "description": "Electrical wire for outdoor installations",
            "sku": "CAB-002",
            "category": str(self.category.pk),
            "tags": [str(self.tag1.pk), str(self.tag2.pk)],
            "_save": "Save",
        }

        response = self.client.post(url, data)

        self.assertEqual(response.status_code, 302)

        product = Product.objects.get(sku="CAB-002")
        self.assertEqual(product.category, self.category)
        self.assertCountEqual(
            product.tags.all(),
            [self.tag1, self.tag2]
        )
