from rest_framework import serializers
from django.contrib.auth.models import User
from user_auth_app.models import UserProfile
from django.contrib.auth import authenticate

class RegistrationSerializer(serializers.ModelSerializer):
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
            username = validated_data['email'],
            email = validated_data['email'],
            first_name = fullname, 
        )
        user.set_password(password)
        user.save()
        
        UserProfile.objects.create(user=user)

        return user
    

class LoginSerializer(serializers.Serializer):
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
    


class MailCheckSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "email", "first_name"]
    

class UserSerializer(serializers.ModelSerializer):
    fullname = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ["id", "email", "fullname"]

    def get_fullname(self, obj):
        if hasattr(obj, 'userprofile') and obj.userprofile:
            return f"{obj.first_name} {obj.last_name}".strip()
        return f"{obj.first_name} {obj.last_name}".strip()