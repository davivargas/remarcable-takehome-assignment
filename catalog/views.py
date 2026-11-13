from django.shortcuts import render

from catalog.filters import filter_products
from catalog.forms import ProductFilterForm
from catalog.models import Product

def product_list(request):
    """
    Display the catalog using validated search and filter parameters
    """
    form = ProductFilterForm(request.GET or None)
    products = Product.objects.none()

    if not form.is_bound:
        products = filter_products()

    elif form.is_valid():
        data = form.cleaned_data

        products = filter_products(
            search_term=data["search"],
            category_ids=[category.pk for category in data["categories"]],
            tag_ids=[tag.pk for tag in data["tags"]]
        )

    products = products.select_related("category").prefetch_related("tags")

    return render(
        request,
        "catalog/product_list.html",
        {
            "form": form,
            "products": products
        }
    )