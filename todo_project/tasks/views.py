from rest_framework import viewsets, permissions, generics, filters
from django_filters.rest_framework import DjangoFilterBackend
from .models import Task
from .serializers import TaskSerializer, UserSerializer
from django.contrib.auth import get_user_model
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.exceptions import PermissionDenied

User = get_user_model()


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAdminUser]


class UserRegisterView(generics.CreateAPIView):
    serializer_class = UserSerializer
    permission_classes = [permissions.AllowAny]


class TaskViewSet(viewsets.ModelViewSet):
    serializer_class = TaskSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['status']  # точная фильтрация по статусу

    def get_queryset(self):
        # Возвращаем задачи только текущего пользователя
        return Task.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def update(self, request, *args, **kwargs):
        task = self.get_object()
        if task.user != request.user:
            raise PermissionDenied("You can update only your own tasks.")
        return super().update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        task = self.get_object()
        if task.user != request.user:
            raise PermissionDenied("You can delete only your own tasks.")
        return super().destroy(request, *args, **kwargs)

    @action(detail=True, methods=['post'])
    def mark_completed(self, request, pk=None):
        task = self.get_object()
        if task.user != request.user:
            raise PermissionDenied("You can mark only your own tasks.")
        task.status = 'Completed'
        task.save()
        serializer = self.get_serializer(task)
        return Response(serializer.data)
