from django.contrib.auth import get_user_model
from django.http import HttpRequest
from django.utils.translation import ugettext_lazy as _
from allauth.account import app_settings as allauth_settings
from allauth.account.forms import ResetPasswordForm
from allauth.utils import email_address_exists, generate_unique_username
from allauth.account.adapter import get_adapter
from allauth.account.utils import setup_user_email
from rest_framework import serializers
from rest_auth.serializers import PasswordResetSerializer
from rest_framework.serializers import ModelSerializer

from home.models import App
from home.models import Plan
from home.models import Subscription


User = get_user_model()


class RequestMixin:
    def _get_request(self):
        request = self.context.get("request")
        if (
            request
            and not isinstance(request, HttpRequest)
            and hasattr(request, "_request")
        ):
            request = request._request
        return request


class SaveUserMixin(RequestMixin):
    def save(self):
        request = self._get_request()
        return super().save(user=request.user)


class SignupSerializer(RequestMixin, serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'name', 'email', 'password')
        extra_kwargs = {
            'password': {
                'write_only': True,
                'style': {
                    'input_type': 'password'
                }
            },
            'email': {
                'required': True,
                'allow_blank': False,
            }
        }

    def validate_email(self, email):
        email = get_adapter().clean_email(email)
        if allauth_settings.UNIQUE_EMAIL:
            if email and email_address_exists(email):
                raise serializers.ValidationError(
                    _("A user is already registered with this e-mail address."))
        return email

    def create(self, validated_data):
        user = User(
            email=validated_data.get('email'),
            name=validated_data.get('name'),
            username=generate_unique_username([
                validated_data.get('name'),
                validated_data.get('email'),
                'user'
            ])
        )
        user.set_password(validated_data.get('password'))
        user.save()
        request = self._get_request()
        setup_user_email(request, user, [])
        return user

    def save(self, request=None):
        """rest_auth passes request so we must override to accept it"""
        return super().save()


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'email', 'name']


class PasswordSerializer(PasswordResetSerializer):
    """Custom serializer for rest_auth to solve reset password error"""
    password_reset_form_class = ResetPasswordForm


class PlanModelSerializer(ModelSerializer):
    class Meta:
        model = Plan
        fields = (
            "id",
            "name",
            "description",
            "price",
            "created_at",
            "updated_at",
        )
        read_only_fields = ("id", "created_at", "updated_at")


class SubscriptionModelSerializer(SaveUserMixin, ModelSerializer):
    class Meta:
        model = Subscription
        fields = (
            "id",
            "user",
            "plan",
            "app",
            "active",
            "created_at",
            "updated_at",
        )
        read_only_fields = (
            "id",
            "user",
            "created_at",
            "updated_at",
        )


class AppModelSerializer(SaveUserMixin, ModelSerializer):
    subscription = serializers.SerializerMethodField(required=False)

    class Meta:
        model = App
        fields = (
            "id",
            "name",
            "description",
            "type",
            "framework",
            "domain_name",
            "screenshot",
            "user",
            "created_at",
            "updated_at",
            "subscription",
        )
        read_only_fields = ("id", "user", "created_at", "updated_at", "subscription")

    def get_subscription(self, obj):
        return obj.subscription.id if obj.subscription else None
