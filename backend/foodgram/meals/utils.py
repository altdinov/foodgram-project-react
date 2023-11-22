import base64

from django.core.files.base import ContentFile
from rest_framework import serializers
from rest_framework.exceptions import ValidationError


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
        else:
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
        else:
            unique_tags.append(tag)

    values_form_data = {
        'image': validated_data.get('image'),
        'name': validated_data.get('name'),
        'text': validated_data.get('text'),
        'cooking_time': validated_data.get('cooking_time')

    }
    description = {
        'image': 'The recipe must have a picture',
        'name': 'The recipe must have a title',
        'text': 'The recipe must have a description',
        'cooking_time': 'The recipe must have a cooking time'
    }
    for key, value in values_form_data.items():
        if not value:
            message = {key: description.get(key)}
            raise ValidationError(message)


def image_url(shopping_cart_serializer, obj):
    request = shopping_cart_serializer.context.get('request')
    image = obj.recipe.image.url
    return request.build_absolute_uri(image)
