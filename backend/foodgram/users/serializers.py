from rest_framework import serializers

from meals.models import Recipe
from meals.utils import Base64ImageField

from .models import Subscription, User
from .utils import subscribed


class UserCreateSerializer(serializers.ModelSerializer):
    """User create serializer"""
    password = serializers.CharField(write_only=True)
    id = serializers.ReadOnlyField()

    class Meta:
        model = User
        fields = (
            'email', 'id', 'username', 'first_name', 'last_name', 'password'
        )

    def create(self, validated_data):
        user = super().create(validated_data)
        user.set_password(validated_data['password'])
        user.save()
        return user


class UserSerializer(serializers.ModelSerializer):
    """User serializer"""
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'email', 'id', 'username', 'first_name',
            'last_name', 'is_subscribed'
        )

    def get_is_subscribed(self, obj):
        return subscribed(self, obj)


class ChangePasswordSerializer(serializers.Serializer):
    """Change password serializer"""
    current_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True)


class RecipeSerializerForSubscription(serializers.ModelSerializer):
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = (
            'id', 'name', 'image', 'cooking_time'
        )


class SubscriptionSerializer(serializers.ModelSerializer):
    """Subscription serializer"""
    email = serializers.EmailField(
        source='subscription_to_user.email',
        required=False
    )
    id = serializers.IntegerField(
        source='subscription_to_user.id',
        required=False
    )
    username = serializers.CharField(
        source='subscription_to_user.username',
        required=False
    )
    first_name = serializers.CharField(
        source='subscription_to_user.first_name',
        required=False
    )
    last_name = serializers.CharField(
        source='subscription_to_user.last_name',
        required=False
    )
    is_subscribed = serializers.SerializerMethodField()
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()

    class Meta:
        model = Subscription
        fields = (
            'email', 'id', 'username', 'first_name', 'last_name',
            'is_subscribed', 'recipes', 'recipes_count'
        )
        read_only_fields = (
            'email', 'id', 'username', 'first_name',
            'last_name', 'recipes'
        )

    def get_is_subscribed(self, obj):
        return subscribed(self, obj.subscription_to_user)

    def get_recipes_count(self, obj):
        return obj.subscription_to_user.recipes.count()

    def get_recipes(self, obj):
        # Filtering if "recipes_limit" is present in the request
        recipes_limit = self.context.get('request').query_params.get(
            'recipes_limit')
        if not recipes_limit:
            recipes = Recipe.objects.filter(author=obj.subscription_to_user)
        else:
            recipes = Recipe.objects.filter(
                author=obj.subscription_to_user)[:int(recipes_limit)]
        serializer = RecipeSerializerForSubscription(recipes, many=True)
        return serializer.data
