from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status
from users.models import User
from records.models import Transaction


class DashboardTests(TestCase):

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

        # Analyst transactions: income=7000, expense=700
        Transaction.objects.create(
            user=self.analyst, amount=5000,
            transaction_type='income', category='salary',
            date='2026-01-15', description='January salary'
        )
        Transaction.objects.create(
            user=self.analyst, amount=2000,
            transaction_type='income', category='freelance',
            date='2026-02-10', description='Freelance work'
        )
        Transaction.objects.create(
            user=self.analyst, amount=500,
            transaction_type='expense', category='food',
            date='2026-02-20', description='Groceries'
        )
        Transaction.objects.create(
            user=self.analyst, amount=200,
            transaction_type='expense', category='transport',
            date='2026-03-05', description='Monthly pass'
        )

        # Viewer transactions: income=3000
        Transaction.objects.create(
            user=self.viewer, amount=3000,
            transaction_type='income', category='freelance',
            date='2026-03-01', description='Side project'
        )

    def get_token(self, username, password):
        response = self.client.post('/api/users/auth/login/', {
            'username': username,
            'password': password
        })
        return response.data.get('access')

    # ------------------------------------------------------------------ #
    #  Summary Endpoint                                                    #
    # ------------------------------------------------------------------ #

    def test_summary_unauthenticated_returns_401(self):
        response = self.client.get('/api/dashboard/summary/')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_summary_returns_required_fields(self):
        token = self.get_token('analyst', 'test123')
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
        response = self.client.get('/api/dashboard/summary/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        for field in ['total_income', 'total_expenses', 'net_balance',
                      'total_transactions', 'average_transaction']:
            self.assertIn(field, response.data)

    def test_summary_correct_totals_for_analyst(self):
        token = self.get_token('analyst', 'test123')
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
        response = self.client.get('/api/dashboard/summary/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(float(response.data['total_income']), 7000)
        self.assertEqual(float(response.data['total_expenses']), 700)
        self.assertEqual(float(response.data['net_balance']), 6300)
        self.assertEqual(response.data['total_transactions'], 4)

    def test_summary_correct_totals_for_viewer(self):
        token = self.get_token('viewer', 'test123')
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
        response = self.client.get('/api/dashboard/summary/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(float(response.data['total_income']), 3000)
        self.assertEqual(float(response.data['total_expenses']), 0)
        self.assertEqual(float(response.data['net_balance']), 3000)

    def test_summary_empty_user_returns_zeros(self):
        """Admin with no transactions should get zeros, not errors"""
        token = self.get_token('admin', 'admin123')
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
        response = self.client.get('/api/dashboard/summary/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_summary_scoped_to_own_data(self):
        """Analyst should not see viewer's transactions in summary"""
        token = self.get_token('analyst', 'test123')
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
        response = self.client.get('/api/dashboard/summary/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Analyst income is 7000 — if viewer's 3000 leaked, total would be 10000
        self.assertEqual(float(response.data['total_income']), 7000)

    # ------------------------------------------------------------------ #
    #  Category Breakdown Endpoint                                         #
    # ------------------------------------------------------------------ #

    def test_category_breakdown_unauthenticated_returns_401(self):
        response = self.client.get('/api/dashboard/category-breakdown/')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_category_breakdown_returns_income_and_expense_keys(self):
        token = self.get_token('analyst', 'test123')
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
        response = self.client.get('/api/dashboard/category-breakdown/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('income', response.data)
        self.assertIn('expense', response.data)

    def test_category_breakdown_correct_income_totals(self):
        token = self.get_token('analyst', 'test123')
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
        response = self.client.get('/api/dashboard/category-breakdown/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        income = response.data['income']
        self.assertIn('salary', income)
        self.assertIn('freelance', income)
        self.assertEqual(float(income['salary']), 5000)
        self.assertEqual(float(income['freelance']), 2000)

    def test_category_breakdown_correct_expense_totals(self):
        token = self.get_token('analyst', 'test123')
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
        response = self.client.get('/api/dashboard/category-breakdown/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        expense = response.data['expense']
        self.assertIn('food', expense)
        self.assertIn('transport', expense)
        self.assertEqual(float(expense['food']), 500)
        self.assertEqual(float(expense['transport']), 200)

    def test_category_breakdown_scoped_to_own_data(self):
        """Viewer should only see their own category breakdown"""
        token = self.get_token('viewer', 'test123')
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
        response = self.client.get('/api/dashboard/category-breakdown/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Viewer has only freelance income
        self.assertIn('freelance', response.data['income'])
        self.assertNotIn('salary', response.data['income'])

    # ------------------------------------------------------------------ #
    #  Monthly Trends Endpoint                                             #
    # ------------------------------------------------------------------ #

    def test_monthly_trends_unauthenticated_returns_401(self):
        response = self.client.get('/api/dashboard/monthly-trends/')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_monthly_trends_returns_list(self):
        token = self.get_token('analyst', 'test123')
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
        response = self.client.get('/api/dashboard/monthly-trends/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsInstance(response.data, list)

    def test_monthly_trends_default_returns_6_months(self):
        token = self.get_token('analyst', 'test123')
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
        response = self.client.get('/api/dashboard/monthly-trends/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 6)

    def test_monthly_trends_custom_months_param(self):
        token = self.get_token('analyst', 'test123')
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
        response = self.client.get('/api/dashboard/monthly-trends/?months=3')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 3)

    def test_monthly_trends_each_entry_has_required_fields(self):
        token = self.get_token('analyst', 'test123')
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
        response = self.client.get('/api/dashboard/monthly-trends/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        for entry in response.data:
            self.assertIn('month', entry)
            self.assertIn('income', entry)
            self.assertIn('expenses', entry)
            self.assertIn('net', entry)
            self.assertIn('transaction_count', entry)

    # ------------------------------------------------------------------ #
    #  Recent Activity Endpoint                                            #
    # ------------------------------------------------------------------ #

    def test_recent_activity_unauthenticated_returns_401(self):
        response = self.client.get('/api/dashboard/recent-activity/')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_recent_activity_returns_list(self):
        token = self.get_token('analyst', 'test123')
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
        response = self.client.get('/api/dashboard/recent-activity/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsInstance(response.data, list)

    def test_recent_activity_default_limit_10(self):
        """Default limit is 10 — analyst has 4 transactions, all should appear"""
        token = self.get_token('analyst', 'test123')
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
        response = self.client.get('/api/dashboard/recent-activity/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 4)

    def test_recent_activity_custom_limit(self):
        token = self.get_token('analyst', 'test123')
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
        response = self.client.get('/api/dashboard/recent-activity/?limit=2')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)

    def test_recent_activity_scoped_to_own_data(self):
        """Analyst should not see viewer's transactions in recent activity"""
        token = self.get_token('analyst', 'test123')
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
        response = self.client.get('/api/dashboard/recent-activity/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        usernames = [item['user_name'] for item in response.data]
        for username in usernames:
            self.assertEqual(username, 'analyst')

    # ------------------------------------------------------------------ #
    #  Financial Health Endpoint                                           #
    # ------------------------------------------------------------------ #

    def test_financial_health_unauthenticated_returns_401(self):
        response = self.client.get('/api/dashboard/financial-health/')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_financial_health_returns_required_fields(self):
        token = self.get_token('analyst', 'test123')
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
        response = self.client.get('/api/dashboard/financial-health/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        for field in ['savings_rate', 'expense_to_income_ratio',
                      'top_expense_category', 'top_income_category']:
            self.assertIn(field, response.data)

    def test_financial_health_correct_savings_rate(self):
        """Analyst: income=7000, expense=700 → savings = 6300/7000 * 100 = 90%"""
        token = self.get_token('analyst', 'test123')
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
        response = self.client.get('/api/dashboard/financial-health/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertAlmostEqual(float(response.data['savings_rate']), 90.0, places=1)

    def test_financial_health_correct_top_expense_category(self):
        """food (500) > transport (200) so top expense = food"""
        token = self.get_token('analyst', 'test123')
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
        response = self.client.get('/api/dashboard/financial-health/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['top_expense_category'], 'food')

    def test_financial_health_correct_top_income_category(self):
        """salary (5000) > freelance (2000) so top income = salary"""
        token = self.get_token('analyst', 'test123')
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
        response = self.client.get('/api/dashboard/financial-health/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['top_income_category'], 'salary')

    def test_financial_health_no_transactions_does_not_crash(self):
        """Admin has no transactions — should return 200 with zero values"""
        token = self.get_token('admin', 'admin123')
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
        response = self.client.get('/api/dashboard/financial-health/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(float(response.data['savings_rate']), 0)
        self.assertIsNone(response.data['top_expense_category'])
        self.assertIsNone(response.data['top_income_category'])
