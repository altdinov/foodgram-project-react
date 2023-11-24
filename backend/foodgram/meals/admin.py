from django.contrib import admin

from .models import (
    Favorite,
    Ingredient,
    IngredientRecipe,
    Product,
    Recipe,
    ShoppingCart,
    Tag,
    TagRecipe
)


class IngredientRecipeInline(admin.StackedInline):
    model = IngredientRecipe
    extra = 0


class TagRecipeInline(admin.StackedInline):
    model = TagRecipe
    extra = 0


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'color',
        'slug',
    )


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = (
        'product',
        'amount',
    )


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'measurement_unit',
    )
    list_filter = ('name',)
    search_fields = ('name',)


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = (
        'author',
        'name',
        'favorites_number'
    )
    list_filter = ('author', 'name', 'tags')
    ordering = ['id']
    inlines = (
        TagRecipeInline, IngredientRecipeInline
    )

    @admin.display(description="In favorites")
    def favorites_number(self, obj):
        return obj.favorites.all().count()


@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    list_display = (
        'user',
        'recipe',
    )


@admin.register(ShoppingCart)
class ShoppingCartAdmin(admin.ModelAdmin):
    list_display = (
        'user',
        'recipe',
    )
