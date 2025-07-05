from rest_framework import serializers
from .models import User, Task
from django.contrib.auth.password_validation import validate_password

class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=6)
    first_name = serializers.CharField(required=True)

    class Meta:
        model = User
        fields = ['id', 'username', 'first_name', 'last_name', 'password']

    def create(self, validated_data):
        password = validated_data['password']
        user = User.objects.create_user(
        username=validated_data['username'],
        first_name=validated_data.get('first_name', ''),
        last_name=validated_data.get('last_name', '')
    )
        validate_password(password, user)
        user.set_password(password)
        user.save()
        return user


class TaskSerializer(serializers.ModelSerializer):
    user = serializers.ReadOnlyField(source='user.username')

    class Meta:
        model = Task
        fields = ['id', 'title', 'description', 'status', 'user']