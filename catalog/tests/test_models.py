
from django.db import IntegrityError, transaction
from django.db.models import ProtectedError
from django.test import TestCase

from catalog.models import Product, Tag, Category


class ProductModelTests(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.category = Category.objects.create(
            name="Electronics",
            description="Electronic devices"
        )
        cls.tag1 = Tag.objects.create(name="Smartphone")
        cls.tag2 = Tag.objects.create(name="Gadget")
        cls.product = Product.objects.create(
            name="iPhone 13",
            description="Apple smartphone",
            sku="IP13-001",
            category=cls.category
        )
        cls.product.tags.add(cls.tag1, cls.tag2)

    def test_product_creation_and_relationships(self):
        """
        test that a product is saved correctly with its category and tags
        """
        product = Product.objects.get(pk=self.product.pk)

        self.assertEqual(product.name, "iPhone 13")
        self.assertEqual(product.description, "Apple smartphone")
        self.assertEqual(product.sku, "IP13-001")
        self.assertEqual(product.category, self.category)
        self.assertCountEqual(
            product.tags.all(),
            [self.tag1, self.tag2]
        )

    def test_product_can_have_no_tags(self):
        """
        test that a product can be created without any tags
        """
        product = Product.objects.create(
            name="Basic Cable",
            description="Standard cable",
            sku="CAB-001",
            category=self.category
        )

        self.assertFalse(product.tags.exists())

    def test_tag_can_be_shared_between_products(self):
        """
        test that the same tag can belong to multiple products
        """
        second_product = Product.objects.create(
            name="iPhone 14",
            description="Apple smartphone",
            sku="IP14-001",
            category=self.category
        )
        second_product.tags.add(self.tag1)

        self.assertCountEqual(
            self.tag1.products.all(),
            [self.product, second_product]
        )

    def test_duplicate_sku_is_rejected(self):
        """
        test that two products cannot have the same SKU
        """
        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                Product.objects.create(
                    name="Another Phone",
                    description="Another smartphone",
                    sku="IP13-001",
                    category=self.category
                )

    def test_duplicate_product_name_is_allowed(self):
        """
        test that products can share a name when their SKUs are different
        """
        product = Product.objects.create(
            name="iPhone 13",
            description="Different variant",
            sku="IP13-002",
            category=self.category
        )

        self.assertNotEqual(product.pk, self.product.pk)

    def test_product_str_method(self):
        """
        test that the product string representation returns its name
        """
        self.assertEqual(str(self.product), "iPhone 13")


class CategoryModelTests(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.category = Category.objects.create(
            name="Electronics",
            description="Electronic devices"
        )

    def test_category_creation_and_retrieval(self):
        """
        test that a category can be created and retrieved from the database
        """
        category = Category.objects.get(name="Electronics")

        self.assertEqual(category.pk, self.category.pk)
        self.assertEqual(category.description, "Electronic devices")

    def test_duplicate_category_name_is_rejected(self):
        """
        test that two categories cannot have the same name
        """
        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                Category.objects.create(name="Electronics")

    def test_category_with_products_cannot_be_deleted(self):
        """
        test that a category cannot be deleted while products reference it
        """
        Product.objects.create(
            name="iPhone 13",
            description="Apple smartphone",
            sku="IP13-001",
            category=self.category
        )

        with self.assertRaises(ProtectedError):
            self.category.delete()

        self.assertTrue(
            Category.objects.filter(pk=self.category.pk).exists()
        )

    def test_category_str_method(self):
        """
        test that the category string representation returns its name
        """
        self.assertEqual(str(self.category), "Electronics")


class TagModelTests(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.tag = Tag.objects.create(name="Smartphone")

    def test_tag_creation(self):
        """
        test that a tag can be created and retrieved from the database
        """
        tag = Tag.objects.get(name="Smartphone")

        self.assertEqual(tag.pk, self.tag.pk)

    def test_duplicate_tag_name_is_rejected(self):
        """
        test that two tags cannot have the same name
        """
        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                Tag.objects.create(name="Smartphone")

    def test_tag_str_method(self):
        """
        test that the tag string representation returns its name
        """
        self.assertEqual(str(self.tag), "Smartphone")
