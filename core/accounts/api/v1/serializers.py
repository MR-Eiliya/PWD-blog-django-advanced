from rest_framework import serializers
from ...models import CustomUser, Profile
from django.contrib.auth.password_validation import validate_password
from django.core import exceptions
from django.contrib.auth import authenticate
from django.utils.translation import gettext_lazy as _
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer



# Registration Serializer
class RegistrationSerializer(serializers.ModelSerializer):
    password1 = serializers.CharField(max_length=255, write_only=True)

    class Meta:
        model = CustomUser
        fields = ["email","username","password","password1"]

    def validate(self, attrs):
        if attrs.get("password") != attrs.get("password1"):
            raise serializers.ValidationError({"detail": "password does not match"})
        try:
            validate_password(attrs.get("password"))
        except exceptions.ValidationError as e:
            raise serializers.ValidationError({"password": list(e.messages)})
        return attrs 
    
    def create(self, validated_data):
        validated_data.pop("password1", None)
        return CustomUser.objects.create_user(**validated_data)
    

# Custom auth token serializer for user login
class CustomAuthTokenSerializer(serializers.Serializer):
    email = serializers.CharField(label=_("email"), write_only=True)
    password = serializers.CharField(
        label=_("Password"),
        style={"input_type": "password"},
        trim_whitespace=False,
        write_only=True,
    )
    token = serializers.CharField(label=_("Token"), read_only=True)

    def validate(self, attrs):
        username = attrs.get("email")
        password = attrs.get("password")

        if username and password:
            user = authenticate(
                request=self.context.get("request"),
                username=username,
                password=password,
            )

            if not user:
                msg = _("Unable to login with provided credentials.")
                raise serializers.ValidationError(msg, code="authorization")
            if not user.is_verified:
                raise serializers.ValidationError({"detail": "user is not verified"})
        else:
            msg = _('Must include "username" and "password".')
            raise serializers.ValidationError(msg, code="authorization")

        attrs["user"] = user
        return attrs


# Serializer for jwt create
class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        validated_data = super().validate(attrs)
        if not self.user.is_verified:
            raise serializers.ValidationError({"detail": "User is not verified"})
        validated_data["email"] = self.user.email
        validated_data["user_id"] = self.user.id
        return validated_data
    


# Serializer for password changing
class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True)
    new_password1 = serializers.CharField(required=True)

    def validate(self, attrs):
        if attrs.get("new_password") != attrs.get("new_password1"):
            raise serializers.ValidationError({"detail": "password does not match"})

        try:
            validate_password(attrs.get("new_password"))
        except exceptions.ValidationError as e:
            raise serializers.ValidationError({"new_password": list(e.messages)})

        return super().validate(attrs)



# Serializer for profile
class ProfileSerializer(serializers.ModelSerializer):
    email = serializers.CharField(source="user.email", read_only=True)

    class Meta:
        model = Profile
        fields = ("id", "email", "first_name", "last_name", "image", "description")
        read_only_fields = ["email"]



# Serializer for resending user activation
class ActivationResendSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)

    def validate(self, attrs):
        email = attrs.get("email")

        try:
            user_obj = CustomUser.objects.get(email=email)
        except CustomUser.DoesNotExist:
            raise serializers.ValidationError({"detail": "user does not exist!"})
        if user_obj.is_verified:
            raise serializers.ValidationError(
                {"detail": "user is already activated and verified!"}
            )
        attrs["user"] = user_obj
        return super().validate(attrs)
    

# Serializer for sending password reset
class PasswordResetRequestSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)

    def validate(self, attrs):
        email = attrs.get("email")
        try:
            user_obj = CustomUser.objects.get(email=email)
        except CustomUser.DoesNotExist:
            raise serializers.ValidationError({"detail": "user does not exist!"})
        attrs["user"] = user_obj
        return super().validate(attrs)


# Serializer for password reset confirmation
class SetNewPasswordSerializer(serializers.Serializer):
    new_password = serializers.CharField(required=True)
    new_password1 = serializers.CharField(required=True)

    def validate(self, attrs):
        if attrs.get("new_password") != attrs.get("new_password1"):
            raise serializers.ValidationError({"detail": "password does not match"})

        try:
            validate_password(attrs.get("new_password"))
        except exceptions.ValidationError as e:
            raise serializers.ValidationError({"new_password": list(e.messages)})

        return super().validate(attrs)
