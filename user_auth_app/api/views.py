from django.contrib.auth.models import User
from rest_framework import generics, permissions, status
from rest_framework.authtoken.models import Token
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.generics import GenericAPIView
from rest_framework.response import Response
from .serializers import RegistrationSerializer, LoginSerializer, MailCheckSerializer



class SignupView(generics.ListCreateAPIView):
    """
    API endpoint that allows users to register a new account.

    GET:
        Returns a list of all users (mainly for admin/testing purposes).
    POST:
        Registers a new user with the provided data.
        Returns an authentication token along with basic user info.

    Uses:
    - RegistrationSerializer for validation and user creation.
    """
    queryset = User.objects.all()
    serializer_class = RegistrationSerializer

    def create(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        token, created = Token.objects.get_or_create(user=user)

        return Response({
            "token": token.key,
            "user_id": user.id,
            "email": user.email,
            "fullname": user.first_name,
        }, status=status.HTTP_201_CREATED)


class UserLoginView(ObtainAuthToken):
    """
    API endpoint to log in a user.

    POST:
        Validates user credentials.
        Returns an authentication token along with basic user info.

    Uses:
    - LoginSerializer for validation.
    - DRF's TokenAuthentication to generate or retrieve tokens.
    """
    serializer_class = LoginSerializer
    
    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']

        token, created = Token.objects.get_or_create(user=user)

        return Response({
            "token": token.key,
            "user_id": user.id,
            "email": user.email,
            "fullname": user.first_name,
        }, status=status.HTTP_200_OK)


class MailCheckView(GenericAPIView):
    """
    API endpoint to check if an email is registered.

    GET:
        Accepts an 'email' query parameter.
        Returns user info if email exists, otherwise 404.

    Permissions:
    - Requires the user to be authenticated.
    """
    serializer_class = MailCheckSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        email = self.request.query_params.get("email")
        if not email:
            return User.objects.none()
        return User.objects.filter(email=email)

    def get(self, request):
        queryset = self.get_queryset()

        if not queryset.exists():
            return Response({"detail": "User not found"}, status=status.HTTP_404_NOT_FOUND)

        serializer = self.get_serializer(queryset.first())
        return Response(serializer.data, status=status.HTTP_200_OK)
