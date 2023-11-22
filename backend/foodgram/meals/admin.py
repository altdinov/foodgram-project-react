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


class TagAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'color',
        'slug',
    )


class IngredientAdmin(admin.ModelAdmin):
    list_display = (
        'product',
        'amount',
    )


class ProductAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'measurement_unit',
    )
    list_filter = ('name',)
    search_fields = ('name',)
    ordering = ['id']


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


class FavoritAdmin(admin.ModelAdmin):
    list_display = (
        'user',
        'recipe',
    )


class ShoppingCartAdmin(admin.ModelAdmin):
    list_display = (
        'user',
        'recipe',
    )


admin.site.register(Tag, TagAdmin)
admin.site.register(Ingredient, IngredientAdmin)
admin.site.register(Recipe, RecipeAdmin)
admin.site.register(Product, ProductAdmin)
admin.site.register(Favorite, FavoritAdmin)
admin.site.register(ShoppingCart, ShoppingCartAdmin)
