from rest_framework import generics
from rest_framework.response import Response
from rest_framework import status
from .serializers import (
    RegistrationSerializer,
    CustomAuthTokenSerializer,
    CustomTokenObtainPairSerializer,
    ChangePasswordSerializer,
    ProfileSerializer,
    ActivationResendSerializer,
    PasswordResetRequestSerializer,
    SetNewPasswordSerializer,
)
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.authtoken.models import Token
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.views import TokenObtainPairView
from django.contrib.auth import get_user_model
from ...models import Profile
from django.shortcuts import get_object_or_404
from django.conf import settings
from mail_templated import EmailMessage
import jwt
from jwt.exceptions import ExpiredSignatureError, InvalidSignatureError
from rest_framework_simplejwt.tokens import RefreshToken
from ..utils import EmailThread
from datetime import datetime, timedelta, timezone

User = get_user_model()


# API Registration Class
class RegistrationAPIView(generics.GenericAPIView):
    serializer_class = RegistrationSerializer

    def post(self, request, *args, **kwargs):
        serializer = RegistrationSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            email = serializer.validated_data["email"]
            data = {"email": email}
            user_obj = get_object_or_404(User, email=email)
            token = self.get_tokens_for_user(user_obj)
            email_obj = EmailMessage(
                "email/activation_email.tpl",
                {"token": token},
                "admin@admin.com",
                to=[email],
            )
            EmailThread(email_obj).start()

            return Response(data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def get_tokens_for_user(self, user):
        refresh = RefreshToken.for_user(user)
        return refresh.access_token
    

# API Token Login Class 
class CustomObtainAuthToken(ObtainAuthToken):
    serializer_class = CustomAuthTokenSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(
            data=request.data, context={"request": request}
        )
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data["user"]
        token, created = Token.objects.get_or_create(user=user)
        return Response({"token": token.key, "user_id": user.pk, "email": user.email})
    

# API Token Logout class
class CustomDiscardAuthToken(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        request.user.auth_token.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    


# API Class For JWT Create
class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer


# API Change Password View
class ChangePasswordAPIView(generics.GenericAPIView):
    model = User
    permission_classes = [IsAuthenticated]
    serializer_class = ChangePasswordSerializer


    def get_object(self, queryset=None):
        obj = self.request.user
        return obj

    def put(self, request, *args, **kwargs):
        self.object = self.get_object()
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            if not self.object.check_password(serializer.data.get("old_password")):
                return Response(
                    {"old_password": ["Wrong Password!"]},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            self.object.set_password(serializer.data.get("new_password"))
            self.object.save()
            return Response(
                {"details": "Your password changed successfully!"},
                status=status.HTTP_200_OK,
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    


# API Profile View
class ProfileAPIView(generics.RetrieveUpdateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = ProfileSerializer
    queryset = Profile.objects.all()

    def get_object(self):
        queryset = self.get_queryset()
        obj = get_object_or_404(queryset, user=self.request.user)
        return obj
    

# User Activation API View
class ActivationAPIView(APIView):


    def get(self, request, *args, **kwargs):
        raw_token = kwargs.get("token")

        try:
            decoded = jwt.decode(raw_token, settings.SECRET_KEY, algorithms=["HS256"])
            user_id = decoded.get("user_id")
        except ExpiredSignatureError:
            return Response(
                {"details": "Token has been expired"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        except Exception:
            return Response(
                {"details": "Invalid token"}, status=status.HTTP_400_BAD_REQUEST
            )

        user_obj = User.objects.get(pk=user_id)

        if user_obj.is_verified:
            return Response({"details": "Your account has already been verified!"})

        user_obj.is_verified = True
        user_obj.save()

        return Response(
            {"details": "Your account has been verified and activated successfully!"}
        )


# Resending User Activation API View
class ActivationResendAPIView(generics.GenericAPIView):
    serializer_class = ActivationResendSerializer

    def post(self, request, *args, **kwargs):
        serializer = ActivationResendSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user_obj = serializer.validated_data["user"]
        token = self.get_tokens_for_user(user_obj)
        email_obj = EmailMessage(
            "email/activation_email.tpl",
            {"token": token},
            "admin@admin.com",
            to=[user_obj.email],
        )
        EmailThread(email_obj).start()
        return Response(
            {"details": "user activation resend successfully"},
            status=status.HTTP_200_OK,
        )

    def get_tokens_for_user(self, user):
        refresh = RefreshToken.for_user(user)
        return refresh.access_token


# API Password Reset Class
class PasswordResetRequestAPIView(generics.GenericAPIView):
    serializer_class = PasswordResetRequestSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user_obj = serializer.validated_data["user"]

        payload = {
            "user_id": user_obj.id,
            "password": user_obj.password,
            "exp": datetime.now(timezone.utc) + timedelta(minutes=15),
        }

        token = jwt.encode(
            payload,
            settings.SECRET_KEY,
            algorithm="HS256",
        )

        email_obj = EmailMessage(
            "email/password_reset.tpl",
            {"token": token},
            "admin@admin.com",
            to=[user_obj.email],
        )
        EmailThread(email_obj).start()

        return Response(
            {"details": "Password reset email sent successfully!"},
            status=status.HTTP_200_OK,
        )
    

# API Confirm Password Reset Class
class SetNewPasswordAPIView(generics.GenericAPIView):
    
    serializer_class = SetNewPasswordSerializer


    def post(self, request, *args, **kwargs):
        raw_token = kwargs.get("token")
        try:
            decoded = jwt.decode(raw_token, settings.SECRET_KEY, algorithms=["HS256"])
            user_id = decoded.get("user_id")
        except ExpiredSignatureError:
            return Response(
                {"details": "Token has been expired"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        except Exception:
            return Response(
                {"details": "Invalid token"}, status=status.HTTP_400_BAD_REQUEST
            )

        try:
            user_obj = User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return Response(
                {"details": "Invalid token"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        

        if decoded.get("password") != user_obj.password:
            return Response(
        {"details": "Invalid or already used token"},
        status=status.HTTP_400_BAD_REQUEST,
    )


        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user_obj.set_password(serializer.validated_data["new_password"])
        user_obj.save()

        return Response(
            {"details": "Password has been reset successfully!"},
            status=status.HTTP_200_OK,
        )
