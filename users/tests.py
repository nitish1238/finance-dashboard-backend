from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from .models import User


class AuthTests(TestCase):

    def setUp(self):
        self.client = APIClient()
        self.admin = User.objects.create_user(
            username='admin', password='admin123', role='admin'
        )
        self.analyst = User.objects.create_user(
            username='analyst', password='test123', role='analyst'
        )
        self.viewer = User.objects.create_user(
            username='viewer', password='test123', role='viewer'
        )

    def get_token(self, username, password):
        response = self.client.post('/api/users/auth/login/', {
            'username': username,
            'password': password
        })
        return response.data.get('access')

    # --- Login Tests ---

    def test_login_valid_credentials_returns_tokens(self):
        response = self.client.post('/api/users/auth/login/', {
            'username': 'admin',
            'password': 'admin123'
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)
        self.assertIn('user', response.data)

    def test_login_wrong_password_returns_401(self):
        response = self.client.post('/api/users/auth/login/', {
            'username': 'admin',
            'password': 'wrongpassword'
        })
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_login_nonexistent_user_returns_401(self):
        response = self.client.post('/api/users/auth/login/', {
            'username': 'nobody',
            'password': 'test123'
        })
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_login_inactive_user_returns_401(self):
        self.viewer.is_active = False
        self.viewer.save()
        response = self.client.post('/api/users/auth/login/', {
            'username': 'viewer',
            'password': 'test123'
        })
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    # --- Register Tests ---

    def test_register_always_assigns_viewer_role(self):
        response = self.client.post('/api/users/register/', {
            'username': 'newuser',
            'email': 'new@example.com',
            'password': 'StrongPass123!',
            'confirm_password': 'StrongPass123!',
            'role': 'admin'  # should be ignored
        })
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        user = User.objects.get(username='newuser')
        self.assertEqual(user.role, 'viewer')

    def test_register_missing_password_returns_400(self):
        response = self.client.post('/api/users/register/', {
            'username': 'newuser2',
            'email': 'new2@example.com',
        })
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_register_password_mismatch_returns_400(self):
        response = self.client.post('/api/users/register/', {
            'username': 'newuser3',
            'email': 'new3@example.com',
            'password': 'StrongPass123!',
            'confirm_password': 'DifferentPass123!'
        })
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    # --- User Management Tests ---

    def test_viewer_cannot_create_user(self):
        token = self.get_token('viewer', 'test123')
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
        response = self.client.post('/api/users/', {
            'username': 'newuser4',
            'email': 'new4@example.com',
            'password': 'StrongPass123!',
            'confirm_password': 'StrongPass123!'
        })
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_non_admin_cannot_change_role(self):
        token = self.get_token('analyst', 'test123')
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
        response = self.client.patch(f'/api/users/{self.analyst.id}/', {
            'role': 'admin'
        })
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_admin_can_change_role(self):
        token = self.get_token('admin', 'admin123')
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
        response = self.client.patch(f'/api/users/{self.viewer.id}/', {
            'role': 'analyst'
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.viewer.refresh_from_db()
        self.assertEqual(self.viewer.role, 'analyst')

    def test_admin_can_deactivate_user(self):
        token = self.get_token('admin', 'admin123')
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
        response = self.client.post(f'/api/users/{self.viewer.id}/deactivate/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.viewer.refresh_from_db()
        self.assertFalse(self.viewer.is_active)

    def test_admin_cannot_deactivate_self(self):
        token = self.get_token('admin', 'admin123')
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
        response = self.client.post(f'/api/users/{self.admin.id}/deactivate/')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_profile_returns_current_user(self):
        token = self.get_token('analyst', 'test123')
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
        response = self.client.get('/api/users/profile/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['username'], 'analyst')

    def test_change_password_success(self):
        token = self.get_token('viewer', 'test123')
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
        response = self.client.post('/api/users/change-password/', {
            'old_password': 'test123',
            'new_password': 'NewPass456!',
            'confirm_password': 'NewPass456!'
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_change_password_wrong_old_password(self):
        token = self.get_token('viewer', 'test123')
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
        response = self.client.post('/api/users/change-password/', {
            'old_password': 'wrongpassword',
            'new_password': 'NewPass456!',
            'confirm_password': 'NewPass456!'
        })
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)