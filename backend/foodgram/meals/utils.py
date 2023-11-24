import base64
import csv

from django.core.files.base import ContentFile
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from .models import Ingredient, IngredientRecipe, ShoppingCart


class Base64ImageField(serializers.ImageField):
    """ImageField custom serializer"""

    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith('data:image'):
            format, imgstr = data.split(';base64,')
            ext = format.split('/')[-1]
            data = ContentFile(base64.b64decode(imgstr), name='temp.' + ext)
        return super().to_internal_value(data)


def check_ingredients_and_tags(validated_data):
    ingredients_ord_dict = validated_data.get('ingredients')
    if not ingredients_ord_dict:
        message = {'ingredients': 'The recipe cannot be without ingredients'}
        raise ValidationError(message)
    unique_ingredients = []
    for ingredient_ord_dict in ingredients_ord_dict:
        if ingredient_ord_dict.get('id') in unique_ingredients:
            message = {
                'ingredients':
                'The recipe cannot contain the same ingredients'
            }
            raise ValidationError(message)
        unique_ingredients.append(ingredient_ord_dict.get('id'))
    tags = validated_data.get('tags')
    if not tags:
        message = {'tags': 'The recipe cannot be without a tag'}
        raise ValidationError(message)
    unique_tags = []
    for tag in tags:
        if tag in unique_tags:
            message = {
                'tags': 'The recipe cannot contain the same tags'
            }
            raise ValidationError(message)
        unique_tags.append(tag)

    description = {
        'image': 'The recipe must have a picture',
        'name': 'The recipe must have a title',
        'text': 'The recipe must have a description',
        'cooking_time': 'The recipe must have a cooking time'
    }
    for key, value in description.items():
        if validated_data.get(key) is None:
            message = {key: value}
            raise ValidationError(message)


def image_url(shopping_cart_serializer, obj):
    request = shopping_cart_serializer.context.get('request')
    image = obj.recipe.image.url
    return request.build_absolute_uri(image)


def create_ingredients(ingredients_ord_dict, recipe):
    ingredients_list = []
    for ingredient_ord_dict in ingredients_ord_dict:
        ingredient, _created = Ingredient.objects.get_or_create(
            product=ingredient_ord_dict['id'],
            amount=ingredient_ord_dict['amount']
        )
        ingredients_list.append(
            IngredientRecipe(ingredient=ingredient, recipe=recipe)
        )
    IngredientRecipe.objects.bulk_create(ingredients_list)


def generate_file(request, response):
    shopping_cart = ShoppingCart.objects.select_related('recipe').filter(
        user=request.user
    )
    writer = csv.writer(response)
    recipe_num = 1
    ingredient_sum = {}
    measurement_unit_sum = {}
    writer.writerow(['Shopping list', ])
    writer.writerow([])
    for row_from_shopping_cart in shopping_cart:
        recipe = row_from_shopping_cart.recipe
        row = ['Recipe #', recipe_num, recipe.name]
        writer.writerow(row)
        ingredient_num = 1
        for ingredient in recipe.ingredients.all():
            row = [
                ingredient_num,
                ingredient.product.name,
                ingredient.amount,
                ingredient.product.measurement_unit
            ]
            writer.writerow(row)
            if ingredient.product.name in ingredient_sum.keys():
                ingredient_sum[ingredient.product.name] += ingredient.amount
            else:
                ingredient_sum[ingredient.product.name] = ingredient.amount
                measurement_unit_sum[
                    ingredient.product.name
                ] = ingredient.product.measurement_unit
            ingredient_num += 1
        writer.writerow([])
        recipe_num += 1
    writer.writerow(['Sum'])
    ingredient_num = 1
    for product, amount in ingredient_sum.items():
        row = [ingredient_num, product, amount, measurement_unit_sum[product]]
        writer.writerow(row)
        ingredient_num += 1
    return response
