from rest_framework import serializers
from .models import User, Task
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError


class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=6)
    first_name = serializers.CharField(required=True)

    class Meta:
        model = User
        fields = ['id', 'username', 'first_name', 'last_name', 'password']
        extra_kwargs = {
            'username': {'required': True, 'allow_blank': False},
        }

    def validate_password(self, value):
        user = User(username=self.initial_data.get('username'))
        try:
            validate_password(value, user)
        except ValidationError as e:
            raise serializers.ValidationError(e.messages)
        return value

    def create(self, validated_data):
        password = validated_data.pop('password')
        user = User(**validated_data)
        user.set_password(password)
        user.save()
        return user


class TaskSerializer(serializers.ModelSerializer):
    user = serializers.ReadOnlyField(source='user.username')

    class Meta:
        model = Task
        fields = ['id', 'title', 'description', 'status', 'user', 'created_at', 'updated_at']

    def validate_status(self, value):
        allowed_statuses = [choice[0] for choice in Task.STATUS_CHOICES]
        if value not in allowed_statuses:
            raise serializers.ValidationError(f"Status must be one of {allowed_statuses}")
        return value

    def validate_title(self, value):
        if not value.strip():
            raise serializers.ValidationError("Title cannot be empty or whitespace")
        return value