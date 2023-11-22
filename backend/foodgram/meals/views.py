import csv

from django.db import models
from django.http import HttpResponse
from django.shortcuts import render
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, mixins, permissions, status, viewsets
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.exceptions import MethodNotAllowed, ValidationError
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from .filters import ProductFilter, RecipeFilter
from .models import Favorite, Ingredient, Product, Recipe, ShoppingCart, Tag
from .pagination import PaginationWithLimit
from .permissions import OwnerOrReadOnly
from .serializers import (
    FavoriteSerializer,
    IngredientSerializer,
    ProductSerializer,
    RecipeSerializer,
    RecipeSerializerForWrite,
    ShoppingCartSerializer,
    TagSerializer
)


class TagViewSet(mixins.ListModelMixin,
                 mixins.RetrieveModelMixin,
                 viewsets.GenericViewSet):
    """Tag ViewSet"""
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = (permissions.AllowAny,)
    pagination_class = None


class ProductViewSet(mixins.ListModelMixin,
                     mixins.RetrieveModelMixin,
                     viewsets.GenericViewSet):
    """Product ViewSet"""
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = (permissions.AllowAny,)
    filter_backends = (DjangoFilterBackend,)
    filterset_class = ProductFilter
    pagination_class = None


class IngredientViewSet(mixins.ListModelMixin,
                        mixins.RetrieveModelMixin,
                        viewsets.GenericViewSet):
    """Ingredient ViewSet"""
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = (permissions.AllowAny,)


class RecipeViewSet(mixins.ListModelMixin,
                    mixins.CreateModelMixin,
                    mixins.UpdateModelMixin,
                    mixins.RetrieveModelMixin,
                    mixins.DestroyModelMixin,
                    viewsets.GenericViewSet):
    """Recipe ViewSet"""
    filter_backends = (DjangoFilterBackend, filters.OrderingFilter,)
    ordering = ('-id',)
    pagination_class = PaginationWithLimit
    filterset_class = RecipeFilter
    filterset_fields = (
        'author', 'tags', 'is_favorited', 'is_in_shopping_cart'
    )

    def get_serializer_class(self):
        if self.action == 'create' or self.action == 'partial_update':
            return RecipeSerializerForWrite
        return RecipeSerializer

    def get_permissions(self):
        if self.action == 'create':
            return (permissions.IsAuthenticated(),)
        if self.action == 'partial_update' or self.action == 'destroy':
            return (OwnerOrReadOnly(),)
        return (permissions.AllowAny(),)

    def update(self, *args, **kwargs):
        raise MethodNotAllowed('POST', detail='Use PATCH')

    def partial_update(self, *args, **kwargs):
        return super().update(*args, **kwargs, partial=True)

    def get_queryset(self):
        # Adding annotations for filtering
        if self.request.user.is_authenticated:
            is_favorited = Favorite.objects.filter(
                recipe=models.OuterRef('pk'), user=self.request.user
            )
            is_in_shopping_cart = ShoppingCart.objects.filter(
                recipe=models.OuterRef('pk'), user=self.request.user
            )
        else:
            is_favorited = Favorite.objects.none()
            is_in_shopping_cart = ShoppingCart.objects.none()
        return Recipe.objects.all().annotate(
            is_favorited=models.Exists(is_favorited),
            is_in_shopping_cart=models.Exists(is_in_shopping_cart)
        )


class FavoriteViewSet(ModelViewSet):
    """Favorite ViewSet"""
    serializer_class = FavoriteSerializer
    permission_classes = (permissions.IsAuthenticated,)
    pagination_class = None
    ordering = ('-id',)

    def _get_recipe(self):
        # Throw exception 400 if there is no recipe
        try:
            recipe = Recipe.objects.get(id=self.kwargs.get('recipe_id'))
        except Recipe.DoesNotExist:
            raise ValidationError({'detail': 'The recipe does not exist'})
        return recipe

    def get_queryset(self):
        recipe = self._get_recipe()
        return recipe.favorites.all()

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        recipe = self._get_recipe()
        user = request.user
        if Favorite.objects.filter(recipe=recipe, user=user).exists():
            data = {'detail': 'The recipe has already been added to favorites'}
            return Response(data, status=status.HTTP_400_BAD_REQUEST, )
        serializer.save(recipe=recipe, user=user)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=False, methods=['delete'])
    def delete(self, request, *args, **kwargs):
        recipe = self._get_recipe()
        user = request.user
        favorite = Favorite.objects.filter(recipe=recipe, user=user).first()
        if favorite:
            favorite.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        else:
            data = {
                'detail':
                ('You cannot remove a recipe from favorites '
                 'that has not yet been added there')
            }
            return Response(data, status=status.HTTP_400_BAD_REQUEST, )


class ShoppingCartViewSet(ModelViewSet):
    """Shopping cart ViewSet"""
    serializer_class = ShoppingCartSerializer
    permission_classes = (permissions.IsAuthenticated,)
    pagination_class = None
    ordering = ('-id',)

    def _get_recipe(self):
        # Throw exception 400 if there is no recipe
        try:
            recipe = Recipe.objects.get(id=self.kwargs.get('recipe_id'))
        except Recipe.DoesNotExist:
            raise ValidationError({'detail': 'The recipe does not exist'})
        return recipe

    def get_queryset(self):
        recipe = self._get_recipe()
        return recipe.shopping_cart.all()

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        recipe = self._get_recipe()
        user = request.user
        if ShoppingCart.objects.filter(recipe=recipe, user=user).exists():
            data = {
                'detail':
                'The recipe has already been added to the shopping list'
            }
            return Response(data, status=status.HTTP_400_BAD_REQUEST, )
        serializer.save(recipe=recipe, user=user)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=False, methods=['delete'])
    def delete(self, request, *args, **kwargs):
        recipe = self._get_recipe()
        user = request.user
        shopping_cart = ShoppingCart.objects.filter(
            recipe=recipe, user=user
        ).first()
        if shopping_cart:
            shopping_cart.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        else:
            data = {
                'detail':
                ('You cannot remove something from your shopping '
                 'list that has not yet been added there.')
            }
            return Response(data, status=status.HTTP_400_BAD_REQUEST, )


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def download_shopping_cart(request):
    """Download shopping cart api view"""
    response = HttpResponse(
        content_type='text/csv',
        headers={
            'Content-Disposition':
            'attachment; filename="somefilename.csv"'
        },
    )
    shopping_cart = ShoppingCart.objects.select_related('recipe').filter(
        user=request.user
    )
    writer = csv.writer(response)
    recipe_num = 1
    ingredient_sum = {}
    measurement_unit_sum = {}
    writer.writerow(['Shopping list',])
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


def page_not_found(request, exception):
    """Custom page 404"""
    return render(request, 'meals/404.html', status=404)
