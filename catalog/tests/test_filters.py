
from django.test import TestCase

from catalog.filters import filter_products
from catalog.models import Category, Product, Tag


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
        cls.category_cables = Category.objects.create(name="Cables")
        cls.category_connectors = Category.objects.create(name="Connectors")
        cls.category_lighting = Category.objects.create(name="Lighting")

        cls.product1 = Product.objects.create(
            name="Copper Cable",
            description="Electrical conductor for panels",
            sku="CAB-001",
            category=cls.category_cables
        )

        cls.product2 = Product.objects.create(
            name="Industrial Connector",
            description="Connector made from copper",
            sku="CON-001",
            category=cls.category_connectors
        )

        cls.product3 = Product.objects.create(
            name="LED Floodlight",
            description="Outdoor industrial lighting",
            sku="LGT-001",
            category=cls.category_lighting
        )

    def test_filter_by_single_category(self):
        """
        test that filtering by a single category returns only
        products in that category
        """
        results = filter_products(category_ids=[self.category_cables.id])
        self.assertCountEqual(results, [self.product1])

    def test_filter_by_multiple_categories(self):
        """
        test that filtering by multiple categories returns products
        in any of those categories
        """
        results = filter_products(
            category_ids=[self.category_cables.id, self.category_connectors.id]
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


class TagFilterTests(TestCase):
    """
    Test the filter_products function for filtering by tags
    """

    @classmethod
    def setUpTestData(cls):
        cls.category = Category.objects.create(name="Cables")

        cls.tag_copper = Tag.objects.create(name="Copper")
        cls.tag_outdoor = Tag.objects.create(name="Outdoor")
        cls.tag_indoor = Tag.objects.create(name="Indoor")

        cls.product1 = Product.objects.create(
            name="Copper Cable",
            description="Electrical conductor for panels",
            sku="CAB-001",
            category=cls.category
        )
        cls.product1.tags.add(cls.tag_copper, cls.tag_outdoor)

        cls.product2 = Product.objects.create(
            name="Outdoor Cable",
            description="Weather-resistant cable",
            sku="CAB-002",
            category=cls.category
        )
        cls.product2.tags.add(cls.tag_outdoor)

        cls.product3 = Product.objects.create(
            name="Indoor Cable",
            description="Cable for indoor use",
            sku="CAB-003",
            category=cls.category
        )
        cls.product3.tags.add(cls.tag_indoor)

        cls.product4 = Product.objects.create(
            name="Basic Cable",
            description="General purpose cable",
            sku="CAB-004",
            category=cls.category
        )

    def test_filter_by_single_tag(self):
        """
        test that filtering by a single tag returns only
        products with that tag
        """
        results = filter_products(tag_ids=[self.tag_copper.id])
        self.assertCountEqual(results, [self.product1])

    def test_filter_by_multiple_tags(self):
        """
        test that filtering by multiple tags returns products
        with any of those tags (OR logic)
        """
        results = filter_products(
            tag_ids=[self.tag_copper.id, self.tag_outdoor.id]
        )
        self.assertCountEqual(results, [self.product1, self.product2])

    def test_filter_with_no_tags(self):
        """
        test that an empty tag selection returns all products
        """
        results = filter_products(tag_ids=[])
        self.assertCountEqual(
            results,
            [self.product1, self.product2, self.product3, self.product4]
        )

    def test_filter_with_no_matching_tags(self):
        """
        test that filtering by a non-existent tag returns no products
        """
        results = filter_products(tag_ids=[999])
        self.assertFalse(results.exists())


class CombinedFiltersTests(TestCase):
    """
    Test combined filtering, edge cases, and result ordering
    """

    @classmethod
    def setUpTestData(cls):
        cls.category_cables = Category.objects.create(name="Cables")
        cls.category_connectors = Category.objects.create(name="Connectors")
        cls.category_lighting = Category.objects.create(name="Lighting")

        cls.tag_copper = Tag.objects.create(name="Copper")
        cls.tag_outdoor = Tag.objects.create(name="Outdoor")
        cls.tag_indoor = Tag.objects.create(name="Indoor")

        # Matches text, category, and both selected tags
        cls.product1 = Product.objects.create(
            name="Copper Cable",
            description="Flexible electrical conductor",
            sku="CAB-001",
            category=cls.category_cables
        )
        cls.product1.tags.add(cls.tag_copper, cls.tag_outdoor)

        # Matches text through description and has the Outdoor tag
        cls.product2 = Product.objects.create(
            name="Industrial Connector",
            description="Copper terminal for wiring",
            sku="CON-001",
            category=cls.category_connectors
        )
        cls.product2.tags.add(cls.tag_outdoor)

        # Matches category and tag, but not text
        cls.product3 = Product.objects.create(
            name="Outdoor Connector",
            description="Steel electrical fitting",
            sku="CON-002",
            category=cls.category_connectors
        )
        cls.product3.tags.add(cls.tag_outdoor)

        # Matches text and tag, but not selected categories
        cls.product4 = Product.objects.create(
            name="Copper Floodlight",
            description="LED lighting fixture",
            sku="LGT-001",
            category=cls.category_lighting
        )
        cls.product4.tags.add(cls.tag_outdoor)

        # Matches text and category, but not selected tags
        cls.product5 = Product.objects.create(
            name="Copper Tester",
            description="Electrical testing tool",
            sku="TOL-001",
            category=cls.category_cables
        )
        cls.product5.tags.add(cls.tag_indoor)

        # Matches text through description, category, and tag
        cls.product6 = Product.objects.create(
            name="Industrial Cable",
            description="Copper electrical conductor",
            sku="CAB-002",
            category=cls.category_cables
        )
        cls.product6.tags.add(cls.tag_copper)

        # Has no tags and does not match text
        cls.product7 = Product.objects.create(
            name="Basic Cable",
            description="General purpose electrical cable",
            sku="CAB-003",
            category=cls.category_cables
        )

    def test_filter_by_category_and_search(self):
        """
        test that category and text filters are combined using AND
        """
        results = filter_products(
            search_term="copper",
            category_ids=[
                self.category_cables.id,
                self.category_lighting.id
            ]
        )

        self.assertCountEqual(
            results,
            [self.product1, self.product4, self.product5, self.product6]
        )

    def test_filter_by_search_and_tags(self):
        """
        test that text search and tag filters are combined using AND
        """
        results = filter_products(
            search_term="copper",
            tag_ids=[self.tag_outdoor.id]
        )

        self.assertCountEqual(
            results,
            [self.product1, self.product2, self.product4]
        )

    def test_filter_by_category_and_tags(self):
        """
        test that category and tag filters are combined using AND,
        with OR within each group
        """
        results = filter_products(
            category_ids=[
                self.category_cables.id,
                self.category_connectors.id
            ],
            tag_ids=[
                self.tag_copper.id,
                self.tag_outdoor.id
            ]
        )

        self.assertCountEqual(
            results,
            [self.product1, self.product2, self.product3, self.product6]
        )

    def test_filter_by_all_three_groups(self):
        """
        test that text, category, and tag filters combine using AND,
        without duplicate products
        """
        results = filter_products(
            search_term="copper",
            category_ids=[
                self.category_cables.id,
                self.category_connectors.id
            ],
            tag_ids=[
                self.tag_copper.id,
                self.tag_outdoor.id
            ]
        )

        self.assertCountEqual(
            results,
            [self.product1, self.product2, self.product6]
        )

    def test_combined_filters_with_no_matches(self):
        """
        test that incompatible filter combinations return no products
        """
        results = filter_products(
            search_term="copper",
            category_ids=[self.category_lighting.id],
            tag_ids=[self.tag_copper.id]
        )

        self.assertFalse(results.exists())

    def test_no_filters_returns_all_products(self):
        """
        test that omitting all filters returns every product
        """
        results = filter_products()

        self.assertCountEqual(
            results,
            [
                self.product1, self.product2, self.product3,
                self.product4, self.product5, self.product6,
                self.product7
            ]
        )

    def test_results_have_deterministic_ordering(self):
        """
        test that results are ordered by name, then primary key
        """
        duplicate_name = Product.objects.create(
            name="Copper Cable",
            description="Alternative electrical cable",
            sku="CAB-004",
            category=self.category_cables
        )
        duplicate_name.tags.add(self.tag_copper)

        results = list(filter_products(
            tag_ids=[self.tag_copper.id, self.tag_outdoor.id]
        ))

        expected = sorted(
            [
                self.product1, self.product2, self.product3,
                self.product4, self.product6, duplicate_name
            ],
            key=lambda product: (product.name, product.pk)
        )

        self.assertEqual(results, expected)
