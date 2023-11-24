from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator
from django.db import models

User = get_user_model()


class Tag(models.Model):
    """Tag model"""
    name = models.CharField(
        max_length=200,
        verbose_name='Name',
        help_text='Name, maximum 200 characters'
    )
    color = models.CharField(
        max_length=7,
        default=None,
        verbose_name='Color',
        help_text='Color in HEX, maximum 7 characters, first character "#"'
    )
    slug = models.SlugField(
        max_length=200,
        unique=True,
        verbose_name='Slug',
        help_text='Unique slug, maximum 200 characters'
    )

    class Meta:
        ordering = ('id',)
        verbose_name = 'Tag'
        verbose_name_plural = 'Tags'

    def __str__(self):
        return self.name


class Product(models.Model):
    """Product model"""
    name = models.CharField(
        max_length=200,
        verbose_name='Name',
        help_text='Name, maximum 200 characters'
    )
    measurement_unit = models.CharField(
        max_length=200,
        verbose_name='Unit',
        help_text='Units of measurement, maximum 200 characters'
    )

    class Meta:
        ordering = ('id',)
        verbose_name = 'Ingredient'
        verbose_name_plural = 'Ingredients'

    def __str__(self):
        return self.name


class Ingredient(models.Model):
    """Ingredient model"""
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='ingredients',
        verbose_name='Ingredient',
        help_text='Ingredient'
    )
    amount = models.FloatField(
        verbose_name='Quantity',
        help_text='Ingredient quantity',
        validators=[
            MinValueValidator(
                limit_value=0.01,
                message=('The quantity of the ingredient cannot be equal '
                         'to or less than 0')
            )
        ]
    )

    class Meta:
        ordering = ('id',)
        verbose_name = 'Ingredient with quantities'
        verbose_name_plural = 'Ingredients with quantities'

    def __str__(self):
        return (
            f'{self.product.name} {self.amount}{self.product.measurement_unit}'
        )


class Recipe(models.Model):
    """Recipe model"""
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='recipes',
        verbose_name='Author',
        help_text='Author of the recipe'
    )
    name = models.CharField(
        max_length=200,
        verbose_name='Name',
        help_text='Name, maximum 200 characters'
    )
    image = models.ImageField(
        upload_to='recipes/images/',
        verbose_name='Picture',
        help_text='Link to picture'
    )
    text = models.TextField(
        verbose_name='Description',
        help_text='Recipe description'
    )
    ingredients = models.ManyToManyField(
        Ingredient,
        through='IngredientRecipe',
        verbose_name='Ingredients',
        help_text='List of ingredients'
    )
    tags = models.ManyToManyField(
        Tag,
        through='TagRecipe',
        related_name='recipes',
        verbose_name='Tags',
        help_text='List of tags'
    )
    cooking_time = models.PositiveSmallIntegerField(
        verbose_name='Cooking time',
        help_text='Cooking time (minutes)',
        validators=[
            MinValueValidator(
                limit_value=1,
                message='Cooking time cannot be less than 1 minute'
            )
        ]
    )

    class Meta:
        ordering = ('-id',)
        verbose_name = 'Recipe'
        verbose_name_plural = 'Recipes'

    def __str__(self):
        return self.name


class IngredientRecipe(models.Model):
    """IngredientRecipe model"""
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        verbose_name='Ingredient',
        help_text='Ingredient'
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        verbose_name='Recipe',
        help_text='Recipe'
    )

    class Meta:
        ordering = ('id',)
        verbose_name = 'IngredientRecipe'
        verbose_name_plural = 'IngredientRecipe'


class TagRecipe(models.Model):
    """TagRecipe model"""
    tag = models.ForeignKey(
        Tag,
        on_delete=models.CASCADE,
        verbose_name='Tag',
        help_text='Tag'
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        verbose_name='Recipe',
        help_text='Recipe'
    )

    class Meta:
        ordering = ('id',)
        verbose_name = 'TagRecipe'
        verbose_name_plural = 'TagRecipe'


class Favorite(models.Model):
    """Favorite model"""
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='favorites',
        verbose_name='Recipe',
        help_text='Recipe'
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='favorites',
        verbose_name='User',
        help_text='User'
    )

    class Meta:
        ordering = ('-id',)
        verbose_name = 'Favorite'
        verbose_name_plural = 'Favorites'


class ShoppingCart(models.Model):
    """ShoppingCart model"""
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='shopping_cart',
        verbose_name='Recipe',
        help_text='Recipe'
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='shopping_cart',
        verbose_name='User',
        help_text='User'
    )

    class Meta:
        ordering = ('-id',)
        verbose_name = 'ShoppingCart'
        verbose_name_plural = 'ShoppingCarts'
