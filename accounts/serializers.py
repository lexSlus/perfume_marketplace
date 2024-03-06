from django.apps import apps
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.tokens import RefreshToken

from .models import Account, UserProfile


class AccountSerializer(serializers.ModelSerializer):
    profile_picture = serializers.ImageField(source='userprofile.profile_picture', read_only=True)
    address_line = serializers.CharField(source='userprofile.address_line', read_only=True)
    city = serializers.CharField(source='userprofile.city', read_only=True)
    could_sell = serializers.BooleanField(source='userprofile.could_sell', read_only=True)

    class Meta:
        model = Account
        fields = ['id', 'email', 'first_name', 'last_name', 'phone_number',
                  'profile_picture', 'address_line', 'city', 'could_sell', 'is_confirmed']

    def get_isAdmin(self, obj):
        return obj.is_staff


class AccountSerializerWithToken(AccountSerializer):
    token = serializers.SerializerMethodField(read_only=True)

    class Meta(AccountSerializer.Meta):
        fields = AccountSerializer.Meta.fields + ['token']

    def get_token(self, obj):
        token = RefreshToken.for_user(obj)
        return str(token.access_token)


class UserProfileSerializer(serializers.ModelSerializer):
    token = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = UserProfile
        fields = ['id', 'address_line', 'profile_picture', 'city', 'token']

    def get_token(self, obj):
        user = obj.user
        token = RefreshToken.for_user(user)
        return str(token.access_token)
