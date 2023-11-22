from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import Subscription, User


class UserAdmin(UserAdmin):
    list_display = (
        'username',
        'email',
        'first_name',
        'last_name',
    )
    list_filter = ('username', 'email')


class SubscriptionAdmin(admin.ModelAdmin):
    list_display = (
        'user',
        'subscription_to_user',
    )


admin.site.register(User, UserAdmin)
admin.site.register(Subscription, SubscriptionAdmin)
