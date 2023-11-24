from .models import Subscription


def subscribed(serializer, user):
    """Check: user is subscribed"""
    subscription_to_user = serializer.context.get("request").user
    return (
        subscription_to_user.is_authenticated
        and Subscription.objects.filter(
            user=user, subscription_to_user=subscription_to_user
        ).exists()
    )
