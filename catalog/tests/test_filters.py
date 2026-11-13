
from django.test import TestCase

from catalog.filters import filter_products
from catalog.models import Category, Product


class ProductFilterTests(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.category = Category.objects.create(name="Cables")

        cls.name_only = Product.objects.create(
            name="Copper Cable",
            description="Electrical conductor for panels",
            sku="CAB-001",
            category=cls.category
        )

        cls.description_only = Product.objects.create(
            name="Industrial Connector",
            description="Connector made from copper",
            sku="CON-001",
            category=cls.category
        )

        cls.both_fields = Product.objects.create(
            name="Copper Wire",
            description="Copper conductors for installations",
            sku="CAB-002",
            category=cls.category
        )

        cls.no_match = Product.objects.create(
            name="LED Floodlight",
            description="Outdoor lighting fixture",
            sku="LGT-001",
            category=cls.category
        )

    def test_search_matches_product_name(self):
        """
        test that search finds products with the term in their name
        """
        results = filter_products("copper")
        self.assertIn(self.name_only, results)

    def test_search_matches_product_description(self):
        """
        test that search finds products with the term in their description
        """
        results = filter_products("copper")
        self.assertIn(self.description_only, results)

    def test_search_matches_both_fields_without_duplicates(self):
        """
        test that products matching both fields appear only once
        """
        results = filter_products("copper")
        self.assertCountEqual(
            results,
            [self.name_only, self.description_only, self.both_fields]
        )

    def test_search_is_case_insensitive(self):
        """
        test that uppercase and lowercase searches return the same products
        """
        lower_results = filter_products("copper")
        upper_results = filter_products("COPPER")
        self.assertCountEqual(lower_results, upper_results)

    def test_search_with_no_matches(self):
        """
        test that an unmatched search term returns no products
        """
        results = filter_products("nonexistent")
        self.assertFalse(results.exists())

    def test_empty_search_returns_all_products(self):
        """
        test that an empty search term does not filter out products
        """
        results = filter_products("")
        self.assertCountEqual(results, Product.objects.all())
