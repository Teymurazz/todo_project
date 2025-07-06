from rest_framework.test import APITestCase
from django.urls import reverse
from rest_framework import status
from django.contrib.auth import get_user_model
from .models import Task

User = get_user_model()

# Unit-тесты API задач


class TaskAPITestCase(APITestCase):

    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpass123')
        response = self.client.post(reverse('token_obtain_pair'), {
            'username': 'testuser',
            'password': 'testpass123'
        })
        self.token = response.data['access']
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.token)

    def test_create_task(self):
        data = {'title': 'Test Task', 'description': 'Just a test', 'status': 'Pending'}
        response = self.client.post('/api/tasks/', data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Task.objects.count(), 1)

    def test_get_task_list(self):
        Task.objects.create(user=self.user, title='Task 1', description='Desc 1', status='Pending')
        response = self.client.get('/api/tasks/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)  # из-за пагинации

    def test_get_task_detail(self):
        task = Task.objects.create(user=self.user, title='Task Detail', description='Details', status='Pending')
        response = self.client.get(f'/api/tasks/{task.id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], 'Task Detail')

    def test_update_task(self):
        task = Task.objects.create(user=self.user, title='Old Title', description='Old Desc', status='Pending')
        data = {'title': 'New Title', 'description': 'New Desc', 'status': 'In Progress'}
        response = self.client.put(f'/api/tasks/{task.id}/', data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        task.refresh_from_db()
        self.assertEqual(task.title, 'New Title')

    def test_delete_task(self):
        task = Task.objects.create(user=self.user, title='To Delete', description='...', status='Pending')
        response = self.client.delete(f'/api/tasks/{task.id}/')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Task.objects.count(), 0)

    def test_mark_task_completed(self):
        task = Task.objects.create(user=self.user, title='Complete Me', description='...', status='Pending')
        response = self.client.post(f'/api/tasks/{task.id}/mark_completed/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        task.refresh_from_db()
        self.assertEqual(task.status, 'Completed')

    def test_filter_task_by_status(self):
        Task.objects.create(user=self.user, title='T1', description='...', status='Completed')
        Task.objects.create(user=self.user, title='T2', description='...', status='Pending')
        response = self.client.get('/api/tasks/?search=Completed')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['status'], 'Completed')
