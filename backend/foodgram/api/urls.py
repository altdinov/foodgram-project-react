from django.urls import include, path
from rest_framework import routers

from meals.views import (
    FavoriteViewSet,
    ProductViewSet,
    RecipeViewSet,
    ShoppingCartViewSet,
    TagViewSet,
    download_shopping_cart
)
from users.views import (
    SubscribeViewSet,
    SubscriptionViewSet,
    UserViewSet,
    change_password
)

app_name = 'api'

router_v1 = routers.DefaultRouter()
router_v1.register(
    'users/subscriptions',
    SubscriptionViewSet,
    basename='subscriptions'
)
router_v1.register("users", UserViewSet, basename="users")
router_v1.register("tags", TagViewSet, basename="tags")
router_v1.register("ingredients", ProductViewSet, basename="ingredients")
router_v1.register("recipes", RecipeViewSet, basename="recipes")
router_v1.register(
    r'users/(?P<user_id>\d+)/subscribe',
    SubscribeViewSet,
    basename='subscribe'
)
router_v1.register(
    r'recipes/(?P<recipe_id>\d+)/favorite',
    FavoriteViewSet,
    basename='favorite'
)
router_v1.register(
    r'recipes/(?P<recipe_id>\d+)/shopping_cart',
    ShoppingCartViewSet,
    basename='shopping_cart'
)

urlpatterns = [
    path('users/set_password/', change_password, name='change_password'),
    path(
        'recipes/download_shopping_cart/',
        download_shopping_cart, name='download_shopping_cart'
    ),
    path("", include(router_v1.urls)),
    path('auth/', include('djoser.urls.authtoken')),
]
