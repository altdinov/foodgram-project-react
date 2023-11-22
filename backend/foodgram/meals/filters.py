import django_filters
from django_filters import rest_framework as filters

from users.models import Subscription

from .models import Product, Recipe, Tag


class ProductFilter(django_filters.FilterSet):
    """Product Filter"""
    name = filters.CharFilter(lookup_expr='istartswith')

    class Meta:
        model = Product
        fields = {
            'name',
        }


class RecipeFilter(django_filters.FilterSet):
    """Recipe filter"""
    tags = django_filters.ModelMultipleChoiceFilter(
        field_name='tags__slug',
        to_field_name='slug',
        queryset=Tag.objects.all(),
    )
    is_favorited = filters.BooleanFilter(field_name='is_favorited')
    is_in_shopping_cart = filters.BooleanFilter(
        field_name='is_in_shopping_cart'
    )

    class Meta:
        model = Recipe
        fields = ('author', 'tags', 'is_favorited', 'is_in_shopping_cart')


class SubscriptionFilter(django_filters.FilterSet):
    """Subsctiption filter"""
    recipes_limit = filters.NumberFilter(field_name='recipes_limit')

    class Meta:
        model = Subscription
        fields = ('recipes_limit',)
