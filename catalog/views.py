from django.shortcuts import render

from catalog.filters import filter_products
from catalog.forms import ProductFilterForm
from catalog.models import Product


def product_list(request):
    """
    Display the catalog using validated search and filter parameters
    """
    # with no query string, "request.GET or None" gives None and the form
    # stays unbound, so the first visit doesn't run validation
    form = ProductFilterForm(request.GET or None)

    # start empty: if the filters are invalid we show the form errors
    # and no products, instead of falling back to the whole catalog
    products = Product.objects.none()

    if not form.is_bound:
        # first visit, nothing to filter by
        products = filter_products()

    elif form.is_valid():
        data = form.cleaned_data

        products = filter_products(
            search_term=data["search"],
            category_ids=[category.pk for category in data["categories"]],
            tag_ids=[tag.pk for tag in data["tags"]]
        )

    # the template shows each product's category and tags, so we load them
    # up front (a JOIN for category, one extra query for all the tags)
    # instead of hitting the database again for every product
    products = products.select_related("category").prefetch_related("tags")

    return render(
        request,
        "catalog/product_list.html",
        {
            "form": form,
            "products": products
        }
    )
