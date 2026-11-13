from django.test import TestCase
from django.urls import reverse

from catalog.models import Category, Product, Tag


class ProductListViewTests(TestCase):
    """
    Test the public catalog search page and HTTP filtering behavior.
    """

    @classmethod
    def setUpTestData(cls):
        cls.category_cables = Category.objects.create(name="Cables")
        cls.category_connectors = Category.objects.create(name="Connectors")
        cls.category_lighting = Category.objects.create(name="Lighting")

        cls.tag_copper = Tag.objects.create(name="Copper")
        cls.tag_outdoor = Tag.objects.create(name="Outdoor")
        cls.tag_indoor = Tag.objects.create(name="Indoor")

        cls.product1 = Product.objects.create(
            name="Copper Cable",
            description="Electrical conductor for panels",
            sku="CAB-001",
            category=cls.category_cables
        )
        cls.product1.tags.add(cls.tag_copper, cls.tag_outdoor)

        cls.product2 = Product.objects.create(
            name="Industrial Connector",
            description="Copper terminal for wiring",
            sku="CON-001",
            category=cls.category_connectors
        )
        cls.product2.tags.add(cls.tag_outdoor)

        cls.product3 = Product.objects.create(
            name="Outdoor Connector",
            description="Steel electrical fitting",
            sku="CON-002",
            category=cls.category_connectors
        )
        cls.product3.tags.add(cls.tag_outdoor)

        cls.product4 = Product.objects.create(
            name="Copper Floodlight",
            description="LED lighting fixture",
            sku="LGT-001",
            category=cls.category_lighting
        )
        cls.product4.tags.add(cls.tag_outdoor)

        cls.product5 = Product.objects.create(
            name="Copper Tester",
            description="Electrical testing tool",
            sku="TOL-001",
            category=cls.category_cables
        )
        cls.product5.tags.add(cls.tag_indoor)

        cls.product6 = Product.objects.create(
            name="Basic Cable",
            description="General purpose electrical cable",
            sku="CAB-002",
            category=cls.category_cables
        )

    def setUp(self):
        self.url = reverse("catalog:product_list")

    def test_initial_page_displays_all_products(self):
        """
        test that the initial catalog page renders all products
        """
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "catalog/product_list.html")
        self.assertCountEqual(
            response.context["products"],
            [
                self.product1, self.product2, self.product3,
                self.product4, self.product5, self.product6
            ]
        )

    def test_search_matches_name_or_description(self):
        """
        test that the public search finds name and description matches
        """
        response = self.client.get(
            self.url,
            {"search": "copper"}
        )

        self.assertEqual(response.status_code, 200)
        self.assertCountEqual(
            response.context["products"],
            [
                self.product1, self.product2,
                self.product4, self.product5
            ]
        )

    def test_combined_filters_with_multiple_selections(self):
        """
        test that repeated category and tag parameters combine
        with text search: any selected category, every selected tag
        """
        response = self.client.get(
            self.url,
            {
                "search": "copper",
                "categories": [
                    str(self.category_cables.pk),
                    str(self.category_connectors.pk)
                ],
                "tags": [
                    str(self.tag_copper.pk),
                    str(self.tag_outdoor.pk)
                ]
            }
        )

        self.assertEqual(response.status_code, 200)
        self.assertCountEqual(
            response.context["products"],
            [self.product1]
        )

    def test_invalid_category_does_not_show_all_products(self):
        """
        test that invalid category input displays form errors
        without returning the unrestricted catalog
        """
        response = self.client.get(
            self.url,
            {"categories": "abc"}
        )

        self.assertEqual(response.status_code, 200)
        self.assertIn("categories", response.context["form"].errors)
        self.assertFalse(response.context["products"].exists())

    def test_invalid_tag_does_not_show_all_products(self):
        """
        test that invalid tag input displays form errors
        without returning the unrestricted catalog
        """
        response = self.client.get(
            self.url,
            {"tags": "999999"}
        )

        self.assertEqual(response.status_code, 200)
        self.assertIn("tags", response.context["form"].errors)
        self.assertFalse(response.context["products"].exists())

    def test_no_results_displays_message(self):
        """
        test that searches without matches display an empty state
        """
        response = self.client.get(
            self.url,
            {"search": "nonexistent"}
        )

        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.context["products"].exists())
        self.assertContains(response, "No products found.")

    def test_selected_filters_are_preserved(self):
        """
        test that submitted search and checkbox values remain selected
        """
        response = self.client.get(
            self.url,
            {
                "search": "copper",
                "categories": [
                    str(self.category_cables.pk),
                    str(self.category_connectors.pk)
                ],
                "tags": [str(self.tag_outdoor.pk)]
            }
        )

        form = response.context["form"]

        self.assertTrue(form.is_bound)
        self.assertEqual(form["search"].value(), "copper")
        self.assertCountEqual(
            form["categories"].value(),
            [
                str(self.category_cables.pk),
                str(self.category_connectors.pk)
            ]
        )
        self.assertEqual(
            form["tags"].value(),
            [str(self.tag_outdoor.pk)]
        )

    def test_sql_like_search_does_not_bypass_filtering(self):
        """
        test that SQL-looking search text cannot return unrelated products
        """
        response = self.client.get(
            self.url,
            {"search": "' OR 1=1 --"}
        )

        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.context["products"].exists())
