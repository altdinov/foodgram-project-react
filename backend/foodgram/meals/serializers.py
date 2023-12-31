from django.contrib.auth import get_user_model
from django.db import models
from rest_framework import serializers

from users.serializers import UserSerializer

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
from .utils import (
    Base64ImageField,
    check_ingredients_and_tags,
    create_ingredients
)

User = get_user_model()


class TagSerializer(serializers.ModelSerializer):
    """Tag serializer"""
    class Meta:
        model = Tag
        fields = (
            'id', 'name', 'color', 'slug'
        )
        read_only_fields = ('name', 'color', 'slug')


class ProductSerializer(serializers.ModelSerializer):
    """Product serializer"""
    class Meta:
        model = Product
        fields = (
            'id', 'name', 'measurement_unit'
        )


class IngredientSerializer(serializers.ModelSerializer):
    """Ingredient serializer"""
    id = serializers.IntegerField(source='product.id')
    name = serializers.CharField(source='product.name')
    measurement_unit = serializers.CharField(source='product.measurement_unit')

    class Meta:
        model = Ingredient
        fields = (
            'id', 'name', 'measurement_unit', 'amount'
        )
        read_only_fields = ('id', 'name', 'measurement_unit')


class IngredientSerializerForWrite(serializers.ModelSerializer):
    """Ingredient write serializer"""
    id = serializers.PrimaryKeyRelatedField(queryset=Product.objects.all())

    class Meta:
        model = Ingredient
        fields = (
            'id', 'amount'
        )


class RecipeSerializer(serializers.ModelSerializer):
    """Recipe serializer"""
    image = Base64ImageField()
    tags = TagSerializer(many=True)
    author = UserSerializer()
    ingredients = IngredientSerializer(many=True)
    is_favorited = serializers.BooleanField()
    is_in_shopping_cart = serializers.BooleanField()

    class Meta:
        model = Recipe
        fields = (
            'id', 'tags', 'author', 'ingredients', 'is_favorited',
            'is_in_shopping_cart', 'name', 'image', 'text', 'cooking_time'
        )
        read_only_fields = (
            'id', 'author', 'is_favorited', 'is_in_shopping_cart'
        )


class RecipeSerializerForWrite(serializers.ModelSerializer):
    """Recipe write serializer"""
    image = Base64ImageField(required=True)
    tags = serializers.PrimaryKeyRelatedField(
        many=True, queryset=Tag.objects.all(), required=True
    )
    ingredients = IngredientSerializerForWrite(many=True, required=True)

    class Meta:
        model = Recipe
        fields = (
            'tags', 'ingredients', 'name',
            'image', 'text', 'cooking_time'
        )

    def to_representation(self, value):
        # Adding annotations for filtering
        is_favorited = Favorite.objects.none()
        is_in_shopping_cart = ShoppingCart.objects.none()
        value = Recipe.objects.filter(id=value.id).annotate(
            is_favorited=models.Exists(is_favorited),
            is_in_shopping_cart=models.Exists(is_in_shopping_cart)
        ).first()
        serializer = RecipeSerializer(value, context=self.context)
        return serializer.data

    def create(self, validated_data):
        check_ingredients_and_tags(validated_data)
        # Pop ingredients and tags (nested serializer)
        ingredients_ord_dict = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')
        recipe = Recipe.objects.create(
            **validated_data, author=self.context['request'].user
        )
        create_ingredients(ingredients_ord_dict, recipe)
        tags_list = []
        for tag in tags:
            tags_list.append(TagRecipe(tag=tag, recipe=recipe))
        TagRecipe.objects.bulk_create(tags_list)
        return recipe

    def update(self, instance, validated_data):
        check_ingredients_and_tags(validated_data)
        instance.author = self.context['request'].user
        instance.name = validated_data.get('name', instance.name)
        instance.image = validated_data.get('image', instance.image)
        instance.text = validated_data.get('text', instance.text)
        instance.cooking_time = validated_data.get(
            'cooking_time',
            instance.cooking_time
        )
        instance.save()
        tags = validated_data.pop('tags')
        instance.tags.set(tags)
        ingredients_ord_dict = validated_data.pop('ingredients')
        IngredientRecipe.objects.filter(recipe=instance).delete()
        create_ingredients(ingredients_ord_dict, instance)
        return instance


class FavoriteSubsBaseSerializer(serializers.ModelSerializer):
    """Base serializer for Favorite and Shopping Cart"""
    name = serializers.CharField(source='recipe.name', required=False)
    cooking_time = serializers.IntegerField(
        source='recipe.cooking_time', required=False
    )
    image = serializers.SerializerMethodField()

    def get_image(self, obj):
        request = self.context.get('request')
        image = obj.recipe.image.url
        return request.build_absolute_uri(image)


class FavoriteSerializer(FavoriteSubsBaseSerializer):
    """Favorite serializer"""
    class Meta:
        fields = (
            'id', 'name', 'image', 'cooking_time'
        )
        read_only_fields = (
            'id', 'name', 'image', 'cooking_time'
        )
        model = Favorite


class ShoppingCartSerializer(FavoriteSubsBaseSerializer):
    """Shopping cart serializer"""
    class Meta:
        fields = (
            'id', 'name', 'image', 'cooking_time'
        )
        read_only_fields = (
            'id', 'name', 'image', 'cooking_time'
        )
        model = ShoppingCart
