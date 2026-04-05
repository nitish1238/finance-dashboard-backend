from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password
from .models import User

class UserSerializer(serializers.ModelSerializer):
    full_name = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'full_name',
                   'phone', 'is_active', 'date_joined', 'last_login', 
                  'created_at', 'updated_at']
        read_only_fields = ['id', 'date_joined', 'last_login', 'created_at', 'updated_at']
    
    def get_full_name(self, obj):
        return obj.get_full_name()

class UserCreateSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True, validators=[validate_password])
    confirm_password = serializers.CharField(write_only=True, required=True)
    role = serializers.CharField(required=False, default='viewer')  # FIXED: Added this line
    
    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'confirm_password', 
                  'first_name', 'last_name', 'role', 'phone']
    
    def validate_role(self, value):
        request = self.context.get('request')
        if not request or not request.user.is_authenticated:
            raise serializers.ValidationError("Authentication required")
        if not getattr(request.user, 'is_admin', False):
            raise serializers.ValidationError("Only admin can change user role")
        return value
    
    def create(self, validated_data):
        validated_data.pop('confirm_password')
        password = validated_data.pop('password')
        role = validated_data.pop('role', 'viewer')
        
       
        username = validated_data.pop('username')
        email = validated_data.pop('email')
        
        user = User.objects.create_user(
            username=username,
            email=email,
            password=password,
            role=role,
            **validated_data
        )
        return user

class UserUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'phone', 'role']
    
    def validate_role(self, value):
        request = self.context.get('request')
        
        if request and request.user.is_authenticated:
            if not getattr(request.user, 'is_admin', False):
                raise serializers.ValidationError("Only admin can change user role")
        return value

class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)

class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True, validators=[validate_password])
    confirm_password = serializers.CharField(required=True)
    
    def validate(self, data):
        if data['new_password'] != data['confirm_password']:
            raise serializers.ValidationError({"confirm_password": "Passwords do not match"})
        return data