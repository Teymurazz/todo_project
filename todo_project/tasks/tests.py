from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase, APIClient
from django.contrib.auth import get_user_model
from .models import Task

User = get_user_model()

class UserRegistrationTests(APITestCase):
    def setUp(self):
        self.url = reverse('user-register')  # correct url for registration

   

    def test_user_registration_success(self):
        data = {
            'username': 'testuser',
            'password': 'StrongPass123!',
            'first_name': 'Test',
            'last_name': 'User',
        }
        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('id', response.data)
        self.assertEqual(response.data['username'], 'testuser')

    def test_user_registration_weak_password(self):
        data = {
            'username': 'weakpassuser',
            'password': '123',
            'first_name': 'Test',
            'last_name': 'User',
        }
        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('password', response.data)

    def test_user_registration_duplicate_username(self):
        User.objects.create_user(username='existinguser', password='StrongPass123!')
        data = {
            'username': 'existinguser',
            'password': 'AnotherStrongPass1!',
            'first_name': 'Test',
            'last_name': 'User',
        }
        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('username', response.data)


class JWTAuthenticationTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='jwtuser', password='StrongPass123!')
        self.token_url = reverse('token_obtain_pair')
        self.refresh_url = reverse('token_refresh')

    def test_obtain_jwt_token(self):
        data = {'username': 'jwtuser', 'password': 'StrongPass123!'}
        response = self.client.post(self.token_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)

    def test_obtain_jwt_token_invalid_credentials(self):
        data = {'username': 'jwtuser', 'password': 'WrongPass'}
        response = self.client.post(self.token_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_refresh_jwt_token(self):
        data = {'username': 'jwtuser', 'password': 'StrongPass123!'}
        token_response = self.client.post(self.token_url, data, format='json')
        refresh_token = token_response.data['refresh']
        response = self.client.post(self.refresh_url, {'refresh': refresh_token}, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)


class UsersEndpointTests(APITestCase):
    def setUp(self):
        self.admin = User.objects.create_superuser(username='admin', password='adminpass')
        self.user = User.objects.create_user(username='normaluser', password='pass1234')
        self.url = reverse('users-list')
        self.client = APIClient()

    def test_access_without_authentication(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_access_with_non_admin_user(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Check user sees only themselves
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['username'], self.user.username)

    def test_access_with_admin_user(self):
        self.client.force_authenticate(user=self.admin)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Admin sees all users, check more than one user present
        self.assertTrue(len(response.data) > 1)

    def test_user_can_update_own_profile(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('users-detail', args=[self.user.id])
        data = {'first_name': 'UpdatedName'}
        response = self.client.patch(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['first_name'], 'UpdatedName')

    def test_user_cannot_update_other_profile(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('users-detail', args=[self.admin.id])
        data = {'first_name': 'Hacker'}
        response = self.client.patch(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_admin_can_update_any_profile(self):
        self.client.force_authenticate(user=self.admin)
        url = reverse('users-detail', args=[self.user.id])
        data = {'first_name': 'AdminUpdated'}
        response = self.client.patch(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['first_name'], 'AdminUpdated')


class TaskTests(APITestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(username='user1', password='pass1234')
        self.user2 = User.objects.create_user(username='user2', password='pass1234')
        self.client = APIClient()

        self.task1 = Task.objects.create(title='Task 1', description='Desc 1', status='Pending', user=self.user1)
        self.task2 = Task.objects.create(title='Task 2', description='Desc 2', status='Completed', user=self.user1)
        self.task3 = Task.objects.create(title='Task 3', description='Desc 3', status='Pending', user=self.user2)

    def test_task_list_requires_authentication(self):
        url = reverse('tasks-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_user_sees_only_their_tasks(self):
        self.client.force_authenticate(user=self.user1)
        url = reverse('tasks-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        for task in response.data['results']:
            self.assertEqual(task['user'], self.user1.username)

    def test_create_task_success(self):
        self.client.force_authenticate(user=self.user1)
        url = reverse('tasks-list')
        data = {'title': 'New Task', 'description': 'New Desc', 'status': 'Pending'}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['title'], 'New Task')
        self.assertEqual(response.data['user'], self.user1.username)

    def test_create_task_invalid_data(self):
        self.client.force_authenticate(user=self.user1)
        url = reverse('tasks-list')
        data = {'title': '', 'description': 'No title', 'status': 'Pending'}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('title', response.data)

    def test_create_task_invalid_status(self):
        self.client.force_authenticate(user=self.user1)
        url = reverse('tasks-list')
        data = {'title': 'Task with bad status', 'description': 'Desc', 'status': 'InvalidStatus'}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('status', response.data)

    def test_forbidden_to_modify_others_task(self):
        self.client.force_authenticate(user=self.user1)
        url = reverse('tasks-detail', args=[self.task3.id])  # task owned by user2
        data = {'title': 'Updated Title'}

        response = self.client.put(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_update_own_task_success(self):
        self.client.force_authenticate(user=self.user1)
        url = reverse('tasks-detail', args=[self.task1.id])
        data = {'title': 'Updated Task 1', 'description': 'Updated Desc', 'status': 'Completed'}
        response = self.client.put(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], 'Updated Task 1')

    def test_partial_update_task(self):
        self.client.force_authenticate(user=self.user1)
        url = reverse('tasks-detail', args=[self.task1.id])
        data = {'status': 'Completed'}
        response = self.client.patch(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['status'], 'Completed')

    def test_delete_own_task(self):
        self.client.force_authenticate(user=self.user1)
        url = reverse('tasks-detail', args=[self.task1.id])
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_filter_tasks_by_invalid_status(self):
        self.client.force_authenticate(user=self.user1)
        url = reverse('tasks-list')
        response = self.client.get(url, {'status': 'InvalidStatus'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 0)


    def test_filter_tasks_by_invalid_status(self):
        self.client.force_authenticate(user=self.user1)
        url = reverse('tasks-list')
        response = self.client.get(url, {'status': 'InvalidStatus'})
        self.assertEqual(response.status_code,
        )
    
    def test_mark_completed_own_task(self):
        self.client.force_authenticate(user=self.user1)
        url = reverse('tasks-mark-completed', args=[self.task1.id])
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['status'], 'Completed')

    def test_mark_completed_other_task_forbidden(self):
       self.client.force_authenticate(user=self.user1)
       url = reverse('tasks-mark-completed', args=[self.task3.id])  # task3 принадлежит user2
       response = self.client.post(url)
       self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
