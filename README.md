#  Finance Dashboard Backend

A backend system for managing financial records with role-based access control and dashboard analytics.
Built to demonstrate backend architecture, API design, and business logic implementation.

---

##  Features

###  Authentication & User Management

* JWT-based authentication
* User registration & login
* Role-based access:

  * Admin – Full access (users + records)
  * Analyst – View + analyze data
  * Viewer – Read-only access
* User activation/deactivation

---

###  Financial Records Management

* Create, update, delete financial records
* Fields:

  * Amount
  * Type (Income / Expense)
  * Category
  * Date
  * Description
* Filtering:

  * By date range
  * Category
  * Type
* Search + Pagination support

---

###  Dashboard Analytics

* Total income
* Total expenses
* Net balance
* Category-wise breakdown
* Recent transactions
* Monthly trends

---

###  Access Control

* Strict role-based permissions
* Middleware/permission classes enforce rules:

  * Viewer → read-only
  * Analyst → read + analytics
  * Admin → full control

---

###  Validation & Error Handling

* Input validation using serializers
* Proper HTTP status codes
* Meaningful error responses

---

##  Tech Stack

* Backend: Django, Django REST Framework
* Authentication: JWT
* Database: SQLite (for simplicity)
* Language: Python

---

##  Project Structure

```
finance-dashboard-backend/
│
├── users/           # User & role management
├── records/         # Financial records
├── dashboard/       # Analytics APIs
├── core/            # Role-based access logic
├── finance_dashboard/  # Settings & main config
└── manage.py
```

---

##  Setup Instructions

### 1. Clone Repository

```
git clone <https://github.com/nitish1238/finance-dashboard-backend.git>
cd finance-dashboard
```

### 2. Create Virtual Environment

```
python -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate
```

### 3. Install Dependencies

```
pip install -r requirements.txt
```

### 4. Run Migrations

```
python manage.py migrate
```

### 5. Run Server

```
python manage.py runserver
```

---

## 🔑 Sample Users (for testing)

| Role    | Username | Password |
| ------- | -------- | -------- |
| Admin   | admin    | admin123 |
| Analyst | analyst  | test123  |
| Viewer  | viewer   | test123  |

---

##  API Endpoints

### Auth

```
POST /api/users/register/          # Register new user (always assigned viewer role)
POST /api/users/auth/login/        # Login and receive JWT tokens
POST /api/users/auth/refresh/      # Refresh access token
```

### Users

```
GET    /api/users/                  # List users (admin sees all, others see self only)
POST   /api/users/                  # Create user (admin only)
GET    /api/users/{id}/             # Retrieve user
PATCH  /api/users/{id}/             # Update user
DELETE /api/users/{id}/             # Delete user (admin only)

GET    /api/users/profile/          # Get current user profile
PATCH  /api/users/profile/          # Update current user profile

POST   /api/users/change-password/  # Change password
POST   /api/users/{id}/activate/    # Activate user (admin only)
POST   /api/users/{id}/deactivate/  # Deactivate user (admin only)
```

### Financial Records

```
GET    /api/records/                # List transactions (filtered by role)
POST   /api/records/                # Create transaction (analyst/admin only)
GET    /api/records/{id}/           # Retrieve transaction
PUT    /api/records/{id}/           # Update transaction (analyst/admin only)
PATCH  /api/records/{id}/           # Partial update
DELETE /api/records/{id}/           # Delete transaction (admin only)

GET    /api/records/categories/     # List all available categories
GET    /api/records/statistics/     # Aggregated income/expense statistics
```

#### Filtering & Search

```
GET /api/records/?transaction_type=income
GET /api/records/?category=salary
GET /api/records/?start_date=2026-01-01&end_date=2026-03-31
GET /api/records/?min_amount=1000&max_amount=5000
GET /api/records/?search=salary
GET /api/records/?ordering=-date
```

### Dashboard

```
GET /api/dashboard/summary/            # Total income, expenses, net balance
GET /api/dashboard/category-breakdown/ # Totals grouped by category
GET /api/dashboard/monthly-trends/     # Income/expense trends per month
GET /api/dashboard/recent-activity/    # Latest transactions
GET /api/dashboard/financial-health/   # Savings rate, top categories
```

### Docs

```
GET /api/docs/      # Swagger UI
GET /api/schema/    # OpenAPI schema
```

---

## 🔍 Example Request

### Login

```json
POST /api/users/auth/login/

{
  "username": "admin",
  "password": "admin123"
}
```

### Create Transaction

```json
POST /api/records/

{
  "amount": 5000,
  "transaction_type": "income",
  "category": "salary",
  "date": "2026-04-01",
  "description": "Monthly salary"
}
```

---

##  Example Response

### Login Response

```json
{
  "access": "<access_token>",
  "refresh": "<refresh_token>",
  "user": {
    "id": 1,
    "username": "admin",
    "email": "admin@example.com",
    "role": "admin"
  }
}
```

### Create Transaction Response

```json
{
  "id": 1,
  "amount": "5000.00",
  "formatted_amount": "$5,000.00",
  "transaction_type": "income",
  "category": "salary",
  "date": "2026-04-01",
  "description": "Monthly salary",
  "notes": "",
  "created_at": "2026-04-01T10:00:00Z"
}
```

---

##  Deployment

### Base URL
https://finance-dashboard-backend-jv22.onrender.com

###  API Documentation (Swagger)
https://finance-dashboard-backend-jv22.onrender.com/api/docs/

---

##  Assumptions

* SQLite used for simplicity (can be swapped to PostgreSQL)
* Authentication handled via JWT
* Roles are predefined: Admin, Analyst, Viewer
* Public registration always assigns viewer role — admin role can only be assigned by an existing admin
* System designed for demonstration, not production

---

##  Design Decisions

* Separated apps (users, records, dashboard, core) for modular structure
* Used DRF for fast and consistent API development
* Role-based permissions enforced at both view and object level
* Dashboard analytics kept separate from records to allow independent scaling
* Focused on clarity and maintainability over complexity

---

##  Future Improvements

* Unit & integration tests
* PostgreSQL database
* Docker support
* Caching for dashboard APIs
* Rate limiting
* Soft delete for transactions

---

##  Author

**Nitish Kumar**

---

##  Final Note

This project focuses on backend fundamentals:

* Clean API design
* Logical data handling
* Role-based access control
* Scalable structure

---
