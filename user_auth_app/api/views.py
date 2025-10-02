from rest_framework import generics
from django.contrib.auth.models import User
from .serializers import RegistrationSerializer, LoginSerializer, MailCheckSerializer
from rest_framework.authtoken.models import Token
from rest_framework.response import Response
from rest_framework import status
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.views import APIView

class SignupView(generics.ListCreateAPIView):
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


class MailCheckView(APIView):
    def get(self, request):
        email = request.query_params.get("email")
        if not email:
            return Response({"detail": "Email query parameter is required"}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            user = User.objects.get(email=email)
            serializer = MailCheckSerializer(user)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except User.DoesNotExist:
            return Response({"detail": "User not found"}, status=status.HTTP_404_NOT_FOUND)