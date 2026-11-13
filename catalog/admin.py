from django.contrib import admin

from catalog.models import Category, Product, Tag


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
    # two-box picker, easier for choosing tags than the default multi-select
    filter_horizontal = ("tags",)
    # fetch each product's category in the same query as the product list
    list_select_related = ("category",)
    ordering = ("name",)

    # list_display can't show a many-to-many field directly,
    # so we build the comma-separated text ourselves
    @admin.display(description="Tags")
    def display_tags(self, obj):
        return ", ".join(sorted(tag.name for tag in obj.tags.all()))

    def get_queryset(self, request):
        # display_tags reads the tags of every row, so we load them all
        # in one extra query instead of one query per product
        queryset = super().get_queryset(request)
        return queryset.prefetch_related("tags")
