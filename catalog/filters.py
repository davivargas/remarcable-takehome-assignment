from django.db.models import Q

from catalog import models


def filter_products(search_term="", category_ids=None, tag_ids=None):
    """
    Filter products by name or description, categories, and tags
    Return a QuerySet with unique products in deterministic order
    """
    
    # since QuerySet is lazy, we can start with all products
    # and filter them down based on the parameters provided
    products = models.Product.objects.all()
    search_term = search_term.strip()
    
    if search_term:
        # conditions inside one ".filter()" are ANDed by default,
        # so we need Q objects to say "name OR description"
        products =  products.filter(
            Q(name__icontains=search_term) |
            Q(description__icontains=search_term)
        )

    if category_ids:
        # "__in" matches any of the selected categories
        # (a product only has one, so "all of them" would never match)
        products = products.filter(category__id__in=category_ids)

    if tag_ids:
        # a product must have every selected tag, so we chain one filter
        # per tag: each ".filter()" call adds its own JOIN on the tags table.
        # "tags__id__in" would use a single JOIN and match any of the tags
        for tag_id in tag_ids:
            products = products.filter(tags__id=tag_id)

    # names can repeat, so pk breaks the tie and keeps the order stable
    return products.order_by('name', 'pk')