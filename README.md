# Finance Dashboard Backend

A backend system for managing financial records with role-based access control and dashboard analytics.

---

##  Features

### 👤 User & Role Management

* Roles: Viewer, Analyst, Admin
* JWT Authentication (login & token refresh)
* User CRUD operations
* Profile management
* Activate/Deactivate users

###  Financial Records

* Income & Expense tracking
* CRUD operations
* Filtering (date, category, amount)
* Search & ordering
* Pagination support

###  Dashboard APIs

* Total income, expenses, net balance
* Category-wise breakdown
* Monthly trends
* Recent transactions

###  Access Control

* Role-based permissions:

  * Viewer → Read-only
  * Analyst → Manage records
  * Admin → Full access

---

## 🛠 Tech Stack

* Django 5
* Django REST Framework
* JWT (SimpleJWT)
* SQLite

---

##  Setup Instructions

```bash
git clone https://github.com/nitish1238/finance-dashboard-backend.git
cd finance_dashboard

python -m venv venv
venv\Scripts\activate  # Windows
source venv/bin/activate  # Mac/Linux

pip install -r requirements.txt

python manage.py migrate
python manage.py createsuperuser

python manage.py runserver
```

---

##  Authentication Flow

1. Login:

```
POST /api/users/auth/login/
```

2. Use token:

```
Authorization: Bearer <access_token>
```

---

##  Important APIs

### Auth

* POST `/api/users/auth/login/`
* POST `/api/users/auth/refresh/`

### Users

* GET `/api/users/users/`
* GET `/api/users/users/profile/`

### Records

* POST `/api/records/`
* GET `/api/records/`

### Dashboard

* GET `/api/dashboard/summary/`

---

##  Query & Filtering Support

* Filter by date range, category, amount
* Search within transaction descriptions
* Ordering by fields (amount, date, etc.)
* Pagination (default: 20 items per page)

---

##  Assumptions

* SQLite used for simplicity
* JWT authentication used instead of session
* Role-based access enforced at API level
* Data is user-specific unless accessed by admin

---

##  Architecture

* `users/` → user, authentication, role management
* `records/` → financial transactions
* `dashboard/` → analytics & summary APIs
* `core/` → shared utilities and permissions

---

##  Enhancements (Beyond Core Requirements)

* JWT-based authentication
* Advanced filtering, search, pagination
* Extended analytics APIs (category breakdown, trends, financial insights)

---

##  Additional APIs

The system also includes extended endpoints such as:

* User activation/deactivation
* Password change
* Category analytics
* Monthly trends & recent activity

> Full API details can be explored via code or API client (Postman/Thunder Client).

---

##  Testing

You can test APIs using:

* Thunder Client (VS Code)
* Postman

Basic flow:

1. Login → get token
2. Use token for authenticated APIs
3. Create records → view dashboard

---

##  Notes

* Designed for clarity, maintainability, and clean architecture
* Focused on backend logic, access control, and API design
* Includes additional features to demonstrate deeper backend understanding

---
