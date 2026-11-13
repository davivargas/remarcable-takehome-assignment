# Electrical Product Catalog

A Django take-home project for Remarcable. It lets users search electrical products by name or description and filter by categories and tags. Products are managed through Django admin.

## Stack

Python 3.13, Django 6.1.3, SQLite, and Django templates. SQLite keeps setup simple and is sufficient for this small, local catalog. No database server is needed.

## Run locally

Requires Python 3.13 and Git.

```bash
git clone https://github.com/davivargas/remarcable-takehome-assignment.git
cd remarcable-takehome-assignment
python -m venv .venv
```

Activate the virtual environment:

```powershell
# Windows PowerShell
.\.venv\Scripts\Activate.ps1
```

```bash
# macOS / Linux
source .venv/bin/activate
```

Then install dependencies, apply the migrations, load the sample catalog, and start the server:

```bash
python -m pip install -r requirements.txt
python manage.py migrate
python manage.py loaddata sample_data
python manage.py runserver
```

Open [http://127.0.0.1:8000/](http://127.0.0.1:8000/).

## Admin and sample data

To add or edit data, create an admin account with `python manage.py createsuperuser`, then visit [http://127.0.0.1:8000/admin/](http://127.0.0.1:8000/admin/).

The included fixture has **5 categories, 10 tags, and 20 products**. These records were entered through Django admin and exported to `catalog/fixtures/sample_data.json`, so you can load the same data without entering it manually.

Each product has one required category, optional multiple tags, and a unique SKU (Stock Keeping Unit). The SKU provides a stable identifier for each product, even when products share the same name. It also reflects how products are identified in inventory systems and external integrations. Enforcing uniqueness prevents duplicate SKUs in the catalog.

Categories and tags can be shared across products. Deleting a category that is in use is prevented.

## Search behavior

All filters are optional. When several are used, the rules are:

- **Text:** case-insensitive match in the product **name OR description**.
- **Categories:** match **any** selected category.
- **Tags:** match **all** selected tags.
- **Between groups**: When text, category, and tag filters are combined, a product must match each selected filter group (AND) to appear in the results.

For example, searching for `copper`, selecting _Cables & Wires_ and _Connectors_, and selecting _Outdoor_ and _Copper_ returns products matching the text, either category, and both selected tags.

Categories use "any" because a product has exactly one category, so requiring several at once would never match. Tags use "all" because they describe independent properties (location, material, rating), so each extra tag should narrow the results rather than widen them.

Multiple selections are supported because they make the filters more useful without adding much complexity. Results are unique and ordered by name, then ID. With no filters, all products are shown.

## Validation and query design

A Django form validates category and tag IDs and limits the search term to 100 characters. Invalid input shows a form error instead of returning an unfiltered catalog. SQL-like search text is treated as plain text.

Filtering uses Django QuerySets (`Q`, `__in`, and one chained `filter()` per selected tag), not raw SQL. ORM parameterization protects against SQL injection; `select_related()` and `prefetch_related()` reduce extra database queries when rendering results.

This is a local development project, not a production deployment. The settings use Django's development configuration (`DEBUG=True` and a development secret key).

## Tests

```bash
python manage.py test catalog
```

Tests cover model relationships and constraints, (customized) admin data entry, text and combined filtering, duplicate prevention, invalid input, and the search page. Django runs them against a separate test database.

## AI assistance

I used AI to suggest test cases and draft automated tests as part of a test-driven workflow. I reviewed the tests to check that they reflected the intended behavior, then implemented the application logic to make them pass.

I also used AI to help with Django admin configuration (`catalog/admin.py`) and the HTML/CSS interface. Since visual design was not the focus of the assignment, I relied more on AI for those parts and reviewed and checked the resulting code.
