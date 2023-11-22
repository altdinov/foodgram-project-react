from django.contrib.auth import update_session_auth_hash
from django.shortcuts import get_object_or_404
from rest_framework import filters, mixins, permissions, status, viewsets
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from meals.pagination import PaginationWithLimit

from .models import Subscription, User
from .serializers import (
    ChangePasswordSerializer,
    SubscriptionSerializer,
    UserCreateSerializer,
    UserSerializer
)


class UserViewSet(mixins.ListModelMixin,
                  mixins.CreateModelMixin,
                  mixins.RetrieveModelMixin,
                  viewsets.GenericViewSet):
    """User ViewSet"""
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = (permissions.AllowAny,)
    pagination_class = PaginationWithLimit

    def get_serializer_class(self):
        if self.action == 'create':
            return UserCreateSerializer
        return UserSerializer

    @action(
        detail=False,
        url_path="me",
        permission_classes=(permissions.IsAuthenticated,),
    )
    def get_me_data(self, request):
        """Endpoint /api/users/me/"""
        serializer = self.serializer_class(
            request.user, context=self.get_serializer_context()
        )
        return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def change_password(request):
    """API View for change password, endpoint users/set_password/"""
    if request.method == 'POST':
        serializer = ChangePasswordSerializer(data=request.data)
        if serializer.is_valid():
            user = request.user
            if user.check_password(serializer.data.get('current_password')):
                user.set_password(serializer.data.get('new_password'))
                user.save()
                update_session_auth_hash(request, user)
                return Response(status=status.HTTP_204_NO_CONTENT)
            return Response(
                {'error': 'Incorrect old password.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class SubscriptionViewSet(mixins.ListModelMixin,
                          viewsets.GenericViewSet):
    """Subscription ViewSet"""
    serializer_class = SubscriptionSerializer
    filter_backends = (filters.OrderingFilter,)
    permission_classes = (permissions.IsAuthenticated,)
    ordering = ('id',)
    pagination_class = PaginationWithLimit

    def get_queryset(self):
        subscriptions = Subscription.objects.filter(user=self.request.user)
        return subscriptions


class SubscribeViewSet(ModelViewSet):
    """Subscribe ViewSet"""
    queryset = Subscription.objects.all()
    serializer_class = SubscriptionSerializer
    permission_classes = (permissions.IsAuthenticated,)
    pagination_class = None

    def _get_user(self):
        """The function returns the user who will be subscribed to"""
        subscription_to_user = get_object_or_404(
            User, id=self.kwargs.get('user_id')
        )
        return subscription_to_user

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        subscription_to_user = self._get_user()
        user = request.user
        if subscription_to_user == user:
            data = {'detail': "You can't subscribe to yourself"}
            return Response(data, status=status.HTTP_400_BAD_REQUEST, )
        if Subscription.objects.filter(
            user=user, subscription_to_user=subscription_to_user
        ).exists():
            data = {'detail': 'You are already following this user'}
            return Response(data, status=status.HTTP_400_BAD_REQUEST, )
        serializer.save(user=user, subscription_to_user=subscription_to_user)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=False, methods=["delete"])
    def delete(self, request, *args, **kwargs):
        """Delete a subscription"""
        subscription_to_user = self._get_user()
        user = request.user
        subscription = Subscription.objects.filter(
            user=user, subscription_to_user=subscription_to_user
        ).first()
        if subscription:
            subscription.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        else:
            data = {
                'detail':
                'You cannot delete a subscription you are not subscribed to'
            }
            return Response(data, status=status.HTTP_400_BAD_REQUEST, )
