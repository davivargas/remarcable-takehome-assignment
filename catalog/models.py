from django.db import models

class Product(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    sku = models.CharField(max_length=100, unique=True) #stock keeping unit
    category = models.ForeignKey(
        'Category', 
        on_delete=models.PROTECT, 
        related_name='products'
    )
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

    def __str__(self):
        return self.name