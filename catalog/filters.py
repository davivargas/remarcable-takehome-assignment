from django.db.models import Q

from catalog import models


def filter_products(search_term=""):
    """
    Search for products by name or description.
    Returns a queryset of matching products
    """
    
    # since QuerySet is lazy, we start with all products
    # and filter them down based on the search string
    products = models.Product.objects.all()
    search_term = search_term.strip()
    if search_term:
        products =  products.filter(
            Q(name__icontains=search_term) |
            Q(description__icontains=search_term)
        )

    return products