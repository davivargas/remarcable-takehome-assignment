
from django.test import TestCase

from catalog.filters import filter_products
from catalog.models import Category, Product

class NameOrDescriptionSearchTests(TestCase):
    """
    Test the filter_products function for searching by name or description
    """

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

class CategoryFilterTests(TestCase):
    """
    Test the filter_products function for filtering by category
    """
    @classmethod
    def setUpTestData(cls):
        cls.category1 = Category.objects.create(name="Cables")
        cls.category2 = Category.objects.create(name="Connectors")
        cls.category3 = Category.objects.create(name="Lighting")

        cls.product1 = Product.objects.create(
            name="Copper Cable",
            description="Electrical conductor for panels",
            sku="CAB-001",
            category=cls.category1
        )

        cls.product2 = Product.objects.create(
            name="Industrial Connector",
            description="Connector made from copper",
            sku="CON-001",
            category=cls.category2
        )

        cls.product3 = Product.objects.create(
            name="LED Floodlight",
            description="Outdoor industrial lighting",
            sku="LGT-001",
            category=cls.category3
        )

    def test_filter_by_single_category(self):
        """
        test that filtering by a single category returns only 
        products in that category
        """
        results = filter_products(category_ids=[self.category1.id])
        self.assertCountEqual(results, [self.product1])

    def test_filter_by_multiple_categories(self):
        """
        test that filtering by multiple categories returns products
        in any of those categories
        """
        results = filter_products(
            category_ids=[self.category1.id, self.category2.id]
        )
        self.assertCountEqual(results, [self.product1, self.product2])

    def test_filter_with_no_matching_categories(self):
        """
        test that filtering by a non-existent category returns no products
        """
        results = filter_products(category_ids=[999])
        self.assertFalse(results.exists())

    def test_filter_with_no_categories(self):
        """
        test that an empty category selection returns all products
        """
        results = filter_products(category_ids=[])

        self.assertCountEqual(
            results,
            [self.product1, self.product2, self.product3]
        )

    def test_filter_by_category_and_search(self):
        """
        test that category and text filters are combined using AND
        """
        results = filter_products(
            search_term="copper",
            category_ids=[self.category1.id, self.category3.id]
        )

        self.assertCountEqual(results, [self.product1])