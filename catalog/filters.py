from django.db.models import Q

from catalog import models


def filter_products(search_term="", category_ids=None, tag_ids=None):
    """
    Filter products by name or description, categories, and tags
    Return a QuerySet with unique products in deterministic order
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

    if category_ids:
        products = products.filter(category__id__in=category_ids)

    if tag_ids:
        # the ".distinct()" call avoid duplicates if multiple tags match
        products = products.filter(tags__id__in=tag_ids).distinct()

    return products.order_by('name', 'pk')