from django.db import models

class Product(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    # stock keeping unit: the code that identifies a product,
    # unique because two products can share the same name
    sku = models.CharField(max_length=100, unique=True)

    # PROTECT blocks deleting a category that still has products,
    # instead of silently deleting the products with it (CASCADE).
    # 'Category' and 'Tag' are passed as strings because those
    # classes are defined further down in this file
    category = models.ForeignKey(
        'Category', 
        on_delete=models.PROTECT, 
        related_name='products'
    )

    # blank=True lets a product be saved without any tags
    tags = models.ManyToManyField(
        'Tag', 
        related_name='products', 
        blank=True
    )

    def __str__(self):
        return self.name

class Tag(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name

class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)

    class Meta:
        # without this, the admin would call the section "Categorys"
        verbose_name_plural = "Categories"

    def __str__(self):
        return self.name