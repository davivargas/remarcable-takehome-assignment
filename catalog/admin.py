
from django.contrib import admin

from .models import Category, Product, Tag


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "description")
    search_fields = ("name",)
    ordering = ("name",)


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ("name",)
    search_fields = ("name",)
    ordering = ("name",)


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ("name", "sku", "category", "display_tags")
    list_filter = ("category", "tags")
    search_fields = ("name", "sku", "description")
    filter_horizontal = ("tags",)
    list_select_related = ("category",)
    ordering = ("name",)

    @admin.display(description="Tags")
    def display_tags(self, obj):
        return ", ".join(sorted(tag.name for tag in obj.tags.all()))

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        return queryset.prefetch_related("tags")
