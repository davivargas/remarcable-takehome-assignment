
from django.http import QueryDict
from django.test import TestCase

from catalog.forms import ProductFilterForm
from catalog.models import Category, Tag


class ProductFilterFormTests(TestCase):
    """
    Test validation of product search and filter inputs
    """

    @classmethod
    def setUpTestData(cls):
        cls.category_cables = Category.objects.create(name="Cables")
        cls.category_lighting = Category.objects.create(name="Lighting")

        cls.tag_copper = Tag.objects.create(name="Copper")
        cls.tag_outdoor = Tag.objects.create(name="Outdoor")

    def test_empty_form_is_valid(self):
        """
        test that all search filters are optional
        """
        form = ProductFilterForm({})

        self.assertTrue(form.is_valid())
        self.assertEqual(form.cleaned_data["search"], "")
        self.assertFalse(form.cleaned_data["categories"].exists())
        self.assertFalse(form.cleaned_data["tags"].exists())

    def test_valid_multiple_categories_and_tags(self):
        """
        test that multiple valid category and tag IDs are accepted
        """
        data = QueryDict(mutable=True)
        data["search"] = "copper"
        data.setlist("categories", [
            str(self.category_cables.id),
            str(self.category_lighting.id)
        ])
        data.setlist("tags", [
            str(self.tag_copper.id),
            str(self.tag_outdoor.id)
        ])

        form = ProductFilterForm(data)

        self.assertTrue(form.is_valid())
        self.assertEqual(form.cleaned_data["search"], "copper")
        self.assertCountEqual(
            form.cleaned_data["categories"],
            [self.category_cables, self.category_lighting]
        )
        self.assertCountEqual(
            form.cleaned_data["tags"],
            [self.tag_copper, self.tag_outdoor]
        )

    def test_invalid_category_ids_are_rejected(self):
        """
        test that malformed and nonexistent category IDs are rejected
        """
        for invalid_id in ["abc", "999999"]:
            with self.subTest(category_id=invalid_id):
                form = ProductFilterForm({
                    "categories": [invalid_id]
                })

                self.assertFalse(form.is_valid())
                self.assertIn("categories", form.errors)

    def test_invalid_tag_ids_are_rejected(self):
        """
        test that malformed and nonexistent tag IDs are rejected
        """
        for invalid_id in ["abc", "999999"]:
            with self.subTest(tag_id=invalid_id):
                form = ProductFilterForm({
                    "tags": [invalid_id]
                })

                self.assertFalse(form.is_valid())
                self.assertIn("tags", form.errors)

    def test_search_exceeding_max_length_is_rejected(self):
        """
        test that search terms longer than 200 characters are rejected
        """
        form = ProductFilterForm({
            "search": "a" * 201
        })

        self.assertFalse(form.is_valid())
        self.assertIn("search", form.errors)

    def test_sql_like_search_input_is_accepted_as_text(self):
        """
        test that SQL-looking input is accepted as ordinary search text
        """
        search_term = "' OR 1=1 --"

        form = ProductFilterForm({
            "search": search_term
        })

        self.assertTrue(form.is_valid())
        self.assertEqual(
            form.cleaned_data["search"],
            search_term
        )
