from rest_framework import serializers
from .models import CustomUser
from django.contrib import auth
from rest_framework.exceptions import AuthenticationFailed
from rest_framework_simplejwt.tokens import RefreshToken, TokenError


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(max_length=68, write_only=True)

    class Meta:
        model = CustomUser
        fields = ["name", "email", "phone_number", "photo","password"]

    def validate(self, attrs):
        email = attrs.get("email")
        phone_number = attrs.get("phone_number")
        return attrs

    def create(self, validated_data):
        return CustomUser.objects.create_user(**validated_data)


class LoginSerializer(serializers.ModelSerializer):
    password = serializers.CharField(max_length=68, write_only=True)
    phone_number = serializers.CharField(max_length=20)
    tokens = serializers.SerializerMethodField()

    def get_tokens(self, obj):
        user = CustomUser.objects.get(phone_number=obj["phone_number"])
        return {"refresh": user.tokens()["refresh"], "access": user.tokens()["access"]}

    class Meta:
        model = CustomUser
        fields = ["phone_number", "password", "tokens"]

        def validate(self, attrs):
            phone_number = attrs.get("phone_number")
            password = attrs.get("password")
            user = auth.authenticate(phone_number=phone_number, password=password)
            if not user:
                raise AuthenticationFailed("Invalid credentials, try again")
            if not user.is_active:
                raise AuthenticationFailed("Account disabled, contact admin")
            return {"name": user.name, "email": user.email, "tokens": user.tokens}


class LogoutSerializer(serializers.Serializer):
    refresh = serializers.CharField()
    def validate(self, attrs):
        self.token = attrs['refresh']
        return attrs
    def save(self, **kwargs):
        try:
            RefreshToken(self.token).blacklist()
        except TokenError:
            self.fail('bad_token')
