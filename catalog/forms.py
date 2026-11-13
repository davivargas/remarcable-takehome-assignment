from django import forms

from catalog.models import Category, Tag


class ProductFilterForm(forms.Form):
    """
    Validate product search and filter parameters
    """

    # every field is optional, so any combination of filters is valid

    search = forms.CharField(
        required=False,
        max_length=100,
        label="Search by name or description"
    )

    # ModelMultipleChoiceField only accepts ids that exist in its queryset,
    # so a made-up or malformed id becomes a form error
    categories = forms.ModelMultipleChoiceField(
        queryset=Category.objects.order_by("name"),
        required=False,
        widget=forms.CheckboxSelectMultiple
    )

    tags = forms.ModelMultipleChoiceField(
        queryset=Tag.objects.order_by("name"),
        required=False,
        widget=forms.CheckboxSelectMultiple
    )
