from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator
from django.db import models

from foodgram.settings import FORBIDDEN_CHAR


class User(AbstractUser):
    """Custom User class"""
    username = models.CharField(
        max_length=150,
        verbose_name='Username',
        unique=True,
        validators=[
            RegexValidator(
                regex=FORBIDDEN_CHAR,
                message=('The username contains an invalid character'),
            )
        ],
        help_text='Unique username, maximum 150 characters'
    )
    email = models.EmailField(
        max_length=254,
        unique=True,
        verbose_name='E-mail',
        help_text='Email address, maximum 254 characters'
    )
    first_name = models.CharField(
        max_length=150,
        verbose_name='First name',
        help_text='First name, maximum 150 characters'
    )
    last_name = models.CharField(
        max_length=150,
        verbose_name='Last name',
        help_text='Last name, maximum 150 characters'
    )
    password = models.CharField(
        max_length=150,
        verbose_name='Password',
        help_text='Password, maximum 150 characters'
        )

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ('username', 'first_name', 'last_name')

    class Meta:
        verbose_name = 'user'
        verbose_name_plural = 'Users'
        ordering = ('id',)

    def __str__(self):
        return self.username


class Subscription(models.Model):
    """Subscription model"""
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='user_subscriptions',
        verbose_name='User',
        help_text='User who subscribes'
    )
    subscription_to_user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='to_user_subscriptions',
        verbose_name='User',
        help_text='User subscribe to'
    )

    class Meta:
        verbose_name = 'Subscription'
        verbose_name_plural = 'Subscriptions'
        ordering = ('id',)
