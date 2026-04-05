from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status
from users.models import User
from .models import Transaction


class TransactionTests(TestCase):

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

        # Analyst transactions
        self.t1 = Transaction.objects.create(
            user=self.analyst,
            amount=5000,
            transaction_type='income',
            category='salary',
            date='2026-03-01',
            description='March salary'
        )
        self.t2 = Transaction.objects.create(
            user=self.analyst,
            amount=200,
            transaction_type='expense',
            category='food',
            date='2026-03-15',
            description='Groceries'
        )
        # Viewer transaction
        self.t3 = Transaction.objects.create(
            user=self.viewer,
            amount=3000,
            transaction_type='income',
            category='freelance',
            date='2026-03-20',
            description='Freelance project'
        )

    def get_token(self, username, password):
        response = self.client.post('/api/users/auth/login/', {
            'username': username,
            'password': password
        })
        return response.data.get('access')

    # ------------------------------------------------------------------ #
    #  Create Tests                                                        #
    # ------------------------------------------------------------------ #

    def test_analyst_can_create_transaction(self):
        token = self.get_token('analyst', 'test123')
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
        response = self.client.post('/api/records/', {
            'amount': 1500,
            'transaction_type': 'income',
            'category': 'freelance',
            'date': '2026-04-01',
            'description': 'New project'
        })
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_admin_can_create_transaction(self):
        token = self.get_token('admin', 'admin123')
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
        response = self.client.post('/api/records/', {
            'amount': 9000,
            'transaction_type': 'income',
            'category': 'business',
            'date': '2026-04-01',
        })
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_viewer_cannot_create_transaction(self):
        token = self.get_token('viewer', 'test123')
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
        response = self.client.post('/api/records/', {
            'amount': 1500,
            'transaction_type': 'income',
            'category': 'salary',
            'date': '2026-04-01',
        })
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_unauthenticated_cannot_create_transaction(self):
        response = self.client.post('/api/records/', {
            'amount': 1000,
            'transaction_type': 'income',
            'category': 'salary',
            'date': '2026-04-01',
        })
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_create_assigns_transaction_to_logged_in_user(self):
        """Transaction must be owned by the user who creates it"""
        token = self.get_token('analyst', 'test123')
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
        response = self.client.post('/api/records/', {
            'amount': 800,
            'transaction_type': 'expense',
            'category': 'transport',
            'date': '2026-04-01',
        })
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        txn = Transaction.objects.get(id=response.data['id'])
        self.assertEqual(txn.user, self.analyst)

    # ------------------------------------------------------------------ #
    #  Read / Scope Tests                                                  #
    # ------------------------------------------------------------------ #

    def test_admin_sees_all_transactions(self):
        token = self.get_token('admin', 'admin123')
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
        response = self.client.get('/api/records/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 3)

    def test_analyst_sees_only_own_transactions(self):
        token = self.get_token('analyst', 'test123')
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
        response = self.client.get('/api/records/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 2)

    def test_viewer_sees_only_own_transactions(self):
        token = self.get_token('viewer', 'test123')
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
        response = self.client.get('/api/records/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 1)

    def test_unauthenticated_request_returns_401(self):
        response = self.client.get('/api/records/')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_retrieve_own_transaction(self):
        token = self.get_token('analyst', 'test123')
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
        response = self.client.get(f'/api/records/{self.t1.id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['id'], self.t1.id)

    def test_cannot_retrieve_other_users_transaction(self):
        """Analyst cannot retrieve viewer's transaction"""
        token = self.get_token('analyst', 'test123')
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
        response = self.client.get(f'/api/records/{self.t3.id}/')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_response_contains_formatted_amount(self):
        token = self.get_token('analyst', 'test123')
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
        response = self.client.get(f'/api/records/{self.t1.id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('formatted_amount', response.data)
        self.assertEqual(response.data['formatted_amount'], '$5,000.00')

    # ------------------------------------------------------------------ #
    #  Filter Tests                                                        #
    # ------------------------------------------------------------------ #

    def test_filter_by_transaction_type_income(self):
        token = self.get_token('admin', 'admin123')
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
        response = self.client.get('/api/records/?transaction_type=income')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        for item in response.data['results']:
            self.assertEqual(item['transaction_type'], 'income')

    def test_filter_by_transaction_type_expense(self):
        token = self.get_token('admin', 'admin123')
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
        response = self.client.get('/api/records/?transaction_type=expense')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        for item in response.data['results']:
            self.assertEqual(item['transaction_type'], 'expense')

    def test_filter_by_date_range(self):
        token = self.get_token('admin', 'admin123')
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
        response = self.client.get(
            '/api/records/?start_date=2026-03-01&end_date=2026-03-10'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 1)

    def test_filter_by_min_amount(self):
        token = self.get_token('admin', 'admin123')
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
        response = self.client.get('/api/records/?min_amount=1000')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        for item in response.data['results']:
            self.assertGreaterEqual(float(item['amount']), 1000)

    def test_filter_by_max_amount(self):
        token = self.get_token('admin', 'admin123')
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
        response = self.client.get('/api/records/?max_amount=500')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        for item in response.data['results']:
            self.assertLessEqual(float(item['amount']), 500)

    def test_filter_by_category(self):
        token = self.get_token('admin', 'admin123')
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
        response = self.client.get('/api/records/?category=salary')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 1)
        self.assertEqual(response.data['results'][0]['category'], 'salary')

    def test_search_by_description(self):
        token = self.get_token('analyst', 'test123')
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
        response = self.client.get('/api/records/?search=salary')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 1)

    def test_ordering_by_amount_desc(self):
        token = self.get_token('analyst', 'test123')
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
        response = self.client.get('/api/records/?ordering=-amount')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        amounts = [float(r['amount']) for r in response.data['results']]
        self.assertEqual(amounts, sorted(amounts, reverse=True))

    # ------------------------------------------------------------------ #
    #  Validation Tests                                                    #
    # ------------------------------------------------------------------ #

    def test_invalid_category_for_type_returns_400(self):
        """food is expense category — cannot be used for income"""
        token = self.get_token('analyst', 'test123')
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
        response = self.client.post('/api/records/', {
            'amount': 500,
            'transaction_type': 'income',
            'category': 'food',
            'date': '2026-04-01',
        })
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_negative_amount_returns_400(self):
        token = self.get_token('analyst', 'test123')
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
        response = self.client.post('/api/records/', {
            'amount': -100,
            'transaction_type': 'income',
            'category': 'salary',
            'date': '2026-04-01',
        })
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_zero_amount_returns_400(self):
        token = self.get_token('analyst', 'test123')
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
        response = self.client.post('/api/records/', {
            'amount': 0,
            'transaction_type': 'income',
            'category': 'salary',
            'date': '2026-04-01',
        })
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_large_expense_over_10000_returns_400(self):
        token = self.get_token('analyst', 'test123')
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
        response = self.client.post('/api/records/', {
            'amount': 15000,
            'transaction_type': 'expense',
            'category': 'rent',
            'date': '2026-04-01',
        })
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_missing_required_fields_returns_400(self):
        token = self.get_token('analyst', 'test123')
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
        response = self.client.post('/api/records/', {
            'amount': 500,
            # missing transaction_type, category, date
        })
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_invalid_transaction_type_returns_400(self):
        token = self.get_token('analyst', 'test123')
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
        response = self.client.post('/api/records/', {
            'amount': 500,
            'transaction_type': 'transfer',  # invalid type
            'category': 'salary',
            'date': '2026-04-01',
        })
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    # ------------------------------------------------------------------ #
    #  Update Tests                                                        #
    # ------------------------------------------------------------------ #

    def test_analyst_can_update_own_transaction(self):
        token = self.get_token('analyst', 'test123')
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
        response = self.client.patch(f'/api/records/{self.t1.id}/', {
            'description': 'Updated description'
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['description'], 'Updated description')

    def test_analyst_cannot_update_others_transaction(self):
        token = self.get_token('analyst', 'test123')
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
        response = self.client.patch(f'/api/records/{self.t3.id}/', {
            'description': 'Hacked'
        })
        # analyst cannot see viewer's record, so 404
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_admin_can_update_any_transaction(self):
        token = self.get_token('admin', 'admin123')
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
        response = self.client.patch(f'/api/records/{self.t3.id}/', {
            'description': 'Admin updated'
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_viewer_cannot_update_transaction(self):
        token = self.get_token('viewer', 'test123')
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
        response = self.client.patch(f'/api/records/{self.t3.id}/', {
            'description': 'Viewer trying to update'
        })
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    # ------------------------------------------------------------------ #
    #  Delete Tests                                                        #
    # ------------------------------------------------------------------ #

    def test_analyst_cannot_delete_transaction(self):
        token = self.get_token('analyst', 'test123')
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
        response = self.client.delete(f'/api/records/{self.t1.id}/')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_viewer_cannot_delete_transaction(self):
        token = self.get_token('viewer', 'test123')
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
        response = self.client.delete(f'/api/records/{self.t3.id}/')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_admin_can_delete_transaction(self):
        token = self.get_token('admin', 'admin123')
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
        response = self.client.delete(f'/api/records/{self.t1.id}/')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Transaction.objects.filter(id=self.t1.id).exists())

    # ------------------------------------------------------------------ #
    #  Categories & Statistics Endpoint Tests                              #
    # ------------------------------------------------------------------ #

    def test_categories_endpoint_returns_income_and_expense(self):
        token = self.get_token('viewer', 'test123')
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
        response = self.client.get('/api/records/categories/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('income', response.data)
        self.assertIn('expense', response.data)

    def test_statistics_returns_correct_totals_for_analyst(self):
        token = self.get_token('analyst', 'test123')
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
        response = self.client.get('/api/records/statistics/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('total_income', response.data)
        self.assertIn('total_expense', response.data)
        self.assertIn('net_balance', response.data)
        # analyst has income=5000, expense=200
        self.assertEqual(float(response.data['total_income']['total']), 5000)
        self.assertEqual(float(response.data['total_expense']['total']), 200)
        self.assertEqual(float(response.data['net_balance']), 4800)

    def test_statistics_admin_sees_all_data(self):
        token = self.get_token('admin', 'admin123')
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
        response = self.client.get('/api/records/statistics/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # total income across all users = 5000 + 3000 = 8000
        self.assertEqual(float(response.data['total_income']['total']), 8000)

    def test_statistics_unauthenticated_returns_401(self):
        response = self.client.get('/api/records/statistics/')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    # ------------------------------------------------------------------ #
    #  Pagination Tests                                                    #
    # ------------------------------------------------------------------ #

    def test_list_response_is_paginated(self):
        token = self.get_token('admin', 'admin123')
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
        response = self.client.get('/api/records/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('count', response.data)
        self.assertIn('results', response.data)
