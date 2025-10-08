from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from rest_framework import serializers
from user_auth_app.models import UserProfile


class RegistrationSerializer(serializers.ModelSerializer):
    """
    Serializer for user registration.

    Fields:
    - fullname: full name of the user (write-only)
    - email: user's email address
    - password: user's password (write-only)
    - repeated_password: confirmation of the password (write-only)

    Validates:
    - Email must be unique.
    - Password and repeated_password must match.

    On creation:
    - Creates a new User instance with username set to email.
    - Sets the password securely.
    - Creates a related UserProfile instance.
    """
    fullname = serializers.CharField(write_only=True)
    password = serializers.CharField(write_only=True, min_length=8)
    repeated_password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ["id", "fullname", "email", "password", "repeated_password"]
        read_only_fields = ["id"]

    def validate(self, attrs):
        if User.objects.filter(email=attrs['email']).exists():
            raise serializers.ValidationError({"email": "A user with this email already exists"})
        if attrs['password'] != attrs['repeated_password']:
            raise serializers.ValidationError({"repeated_password": "Passwords do not match"})
        return attrs

    def create(self, validated_data):
        fullname = validated_data.pop('fullname')
        password = validated_data.pop('password')
        validated_data.pop('repeated_password')

        user = User.objects.create(
            username=validated_data['email'],
            email=validated_data['email'],
            first_name=fullname,
        )
        user.set_password(password)
        user.save()

        UserProfile.objects.create(user=user)

        return user


class LoginSerializer(serializers.Serializer):
    """
    Serializer for user login.

    Fields:
    - email: user's email address
    - password: user's password (write-only)

    Validates:
    - Checks if the provided email and password authenticate a user.
    """
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        email = attrs.get("email")
        password = attrs.get("password")

        user = authenticate(username=email, password=password)
        if not user:
            raise serializers.ValidationError({"error": "Invalid email or password"})

        attrs["user"] = user
        return attrs



class UserSerializer(serializers.ModelSerializer):
    """
    Serializer to represent a user with fullname.

    Fields:
    - id: user ID
    - email: user email
    - fullname: concatenation of first_name and last_name if user profile exists
    """
    fullname = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ["id", "email", "fullname"]

    def get_fullname(self, obj):
        if hasattr(obj, 'userprofile') and obj.userprofile:
            return f"{obj.first_name} {obj.last_name}".strip()
        return f"{obj.first_name} {obj.last_name}".strip()
