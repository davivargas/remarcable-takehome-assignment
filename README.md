# Electrical Product Catalog

A Django take-home project for Remarcable. It lets users search electrical products by name or description and filter by categories and tags. Products are managed through Django admin.

## Stack

Python 3.13, Django 6.1.3, SQLite, and Django templates. SQLite keeps setup simple and is sufficient for this small, local catalog. No database server is needed.

## Run with Docker

```bash
docker build -t catalog .
docker run --rm -p 8000:8000 --name catalog catalog
```

Open [http://127.0.0.1:8000/](http://127.0.0.1:8000/). The sample data is loaded when the image is built.

To use the admin, create an account in the running container:

```bash
docker exec -it catalog python manage.py createsuperuser
```

The database lives inside the container, so changes made through the admin are lost when it stops.

## or Run locally

Tested with Python 3.13. You also need Git. On macOS / Linux the command may be `python3` instead of `python`.

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

Each product has one required category, optional multiple tags, and a unique SKU (Stock Keeping Unit). Product names can repeat, so the SKU is the stable identifier, which is also how inventory systems and external integrations refer to products.

Categories and tags can be shared across products. Deleting a category that is in use is prevented.

## Where things are

- `catalog/models.py`: the `Product`, `Category`, and `Tag` models and their relationships.
- `catalog/filters.py`: all of the search and filter query logic, in one function.
- `catalog/forms.py`: validation of the search text and the selected categories and tags.
- `catalog/views.py` and `catalog/templates/catalog/product_list.html`: the search page.
- `catalog/admin.py`: the admin configuration used to enter the data.
- `catalog/tests/`: one test module per file above.

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

Filtering uses Django QuerySets, not raw SQL, so ORM parameterization protects against SQL injection:

- **Text:** two `Q` objects joined with `|`, because conditions inside one `filter()` are ANDed by default.
- **Categories:** `category__id__in`, which matches any selected category.
- **Tags:** one chained `filter()` per selected tag. Each call adds its own JOIN, so a product must have every tag. A single `tags__id__in` would match any of them instead.

The page runs four queries no matter how many products are listed: two for the category and tag checkboxes, one for the products with their category (`select_related()`), and one for all of their tags (`prefetch_related()`).

## Assumptions

- "Search by description" also matches the product name, since that is where most people expect a keyword to be found.
- Users can select several categories and several tags at once. Categories match any, tags match all (see [Search behavior](#search-behavior)).
- A product belongs to exactly one category and can have any number of tags, including none.
- Product names can repeat; the SKU is what makes a product unique.
- The catalog is small enough to show on one page, so there is no pagination.
- The search page is public. Only the admin requires a login.
- This runs locally only. The settings use Django's development configuration (`DEBUG=True` and a development secret key), and SQLite is enough for the data size.

## Tests

```bash
python manage.py test catalog
```

Tests cover model relationships and constraints, custom admin behaviour, text and combined filtering, duplicate prevention, invalid input, and the search page. Django runs them against a separate test database.

## With more time

- Paginate the results, which a real catalog would need.
- Add a "match any / match all" switch for tags, since both are reasonable.
- Move to PostgreSQL and use its full-text search, so results can be ranked by relevance instead of plain substring matching.
- Add a Dockerfile so the project runs with one command.

## AI assistance

I used Claude (Anthropic) as an assistant on this project. The data model,
the query logic, the form, and the view are my own work, and I can explain
all of them.

| Where                             | How AI was used                                                                                                                                              | My contribution                                                                                                                                                              |
| --------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------ | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `catalog/tests/`                  | Suggested test cases and drafted the tests, as part of a test-first workflow                                                                                 | Decided what behaviour to cover, reviewed every test, and corrected them where they were wrong (for example the max-length boundary, commit `45a46da`).                      |
| `catalog/admin.py`                | Drafted the admin configuration                                                                                                                              | Reviewed it and kept it as drafted. I used it to enter all of the sample data, and limited the admin tests to its custom behaviour (the tags column and creating a product). |
| Template and CSS                  | Drafted the markup and styles, since design was not the focus                                                                                                | Reviewed them and kept them largely as drafted. The fields, validation errors, and results the page renders come from my own form and view.                                  |
| `catalog/filters.py` (tag filter) | An AI review of the finished project questioned whether tags should match any or all. AI proposed the chained-filter approach and updated the affected tests | I made the decision to switch to "all", then reviewed the new query and the updated tests.                                                                                   |
| In-line comments                  | AI pointed out where comments were missing and drafted them                                                                                                  | Reviewed each comment against my own reasoning for the code.                                                                                                                 |
| Formatting                        | AI ran a cleanup pass (whitespace, quotes, imports, file encoding)                                                                                           | Reviewed the diff                                                                                                                                                            |

I wrote the models, `filters.py` (apart from the tag change above),
`forms.py`, and `views.py` myself.
