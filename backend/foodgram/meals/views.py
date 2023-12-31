from django.db import models
from django.http import HttpResponse
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
from .utils import generate_file


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
    pagination_class = PaginationWithLimit
    filterset_class = RecipeFilter
    filterset_fields = (
        'author', 'tags', 'is_favorited', 'is_in_shopping_cart'
    )

    def get_serializer_class(self):
        if self.action in ('create', 'partial_update'):
            return RecipeSerializerForWrite
        return RecipeSerializer

    def get_permissions(self):
        if self.action == 'create':
            return (permissions.IsAuthenticated(),)
        if self.action in ('partial_update', 'destroy'):
            return (OwnerOrReadOnly(),)
        return (permissions.AllowAny(),)

    def update(self, *args, **kwargs):
        raise MethodNotAllowed('PUT', detail='Use PATCH')

    def partial_update(self, *args, **kwargs):
        return super().update(*args, **kwargs)

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
        return Recipe.objects.all().select_related('author').prefetch_related(
            'tags', 'ingredients', 'ingredients__product').annotate(
            is_favorited=models.Exists(is_favorited),
            is_in_shopping_cart=models.Exists(is_in_shopping_cart)
        )


class FavoriteAndShopCartMixin:
    """Mixin for Favorite and Shopping Cart"""
    use_model = None
    object_alredy_added_text = None
    cannot_remove_text = None

    def _get_recipe(self):
        recipe = Recipe.objects.filter(id=self.kwargs.get('recipe_id')).first()
        if recipe is None:
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
        if self.use_model.objects.filter(recipe=recipe, user=user).exists():
            data = {'detail': self.object_alredy_added_text}
            return Response(data, status=status.HTTP_400_BAD_REQUEST, )
        serializer.save(recipe=recipe, user=user)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=False, methods=['delete'])
    def delete(self, request, *args, **kwargs):
        recipe = self._get_recipe()
        user = request.user
        deleted_object = self.use_model.objects.filter(
            recipe=recipe, user=user
        ).first()
        if deleted_object is None:
            data = {'detail': self.cannot_remove_text}
            return Response(data, status=status.HTTP_400_BAD_REQUEST, )
        deleted_object.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class FavoriteViewSet(FavoriteAndShopCartMixin, ModelViewSet):
    """Favorite ViewSet"""
    serializer_class = FavoriteSerializer
    permission_classes = (permissions.IsAuthenticated,)
    pagination_class = None
    use_model = Favorite
    object_alredy_added_text = 'The recipe has already been added to favorites'
    cannot_remove_text = ('You cannot remove a recipe from favorites '
                          'that has not yet been added there')


class ShoppingCartViewSet(FavoriteAndShopCartMixin, ModelViewSet):
    """Shopping cart ViewSet"""
    serializer_class = ShoppingCartSerializer
    permission_classes = (permissions.IsAuthenticated,)
    pagination_class = None
    use_model = ShoppingCart
    object_alredy_added_text = ('he recipe has already been added '
                                'to the shopping list')
    cannot_remove_text = ('You cannot remove something from your shopping '
                          'list that has not yet been added there.')


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
    return generate_file(request, response)
