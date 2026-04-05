#  Finance Dashboard Backend

A backend system for managing financial records with role-based access control and dashboard analytics.
This project demonstrates backend architecture, API design, and business logic implementation using Django REST Framework.

---

##  Overview

This project implements a finance dashboard backend where different users interact with financial data based on roles.

It demonstrates:

* Clean REST API design using Django REST Framework
* Role-based access control (RBAC)
* Financial data processing and aggregation
* Scalable and modular backend structure

---

##  Key Highlights

*  Fully test-driven backend (**98/98 tests passing**)
*  Role-based permissions (Admin / Analyst / Viewer)
*  Dashboard analytics (trends, breakdowns, insights)
*  Advanced filtering, search, and sorting
*  Deployed API with Swagger documentation

---

##  User Roles

| Role        | Permissions                                |
| ----------- | ------------------------------------------ |
| **Admin**   | Full access (manage users + all records)   |
| **Analyst** | Create & view own transactions + analytics |
| **Viewer**  | Read-only access                           |

---

##  Features

### 1. Financial Records Management

* Create, update, delete transactions
* Fields:

  * Amount
  * Type (Income / Expense)
  * Category
  * Date
  * Description / Notes

---

### 2. Filtering & Search

* Filter by:

  * Date range
  * Category
  * Transaction type
  * Amount range
* Search by description/notes
* Sorting support

---

### 3. Dashboard Analytics

* Total income
* Total expenses
* Net balance
* Category-wise breakdown
* Recent activity
* Monthly trends
* Financial health insights

---

### 4. Access Control

* Strict role-based permissions enforced at backend
* Viewer → read-only
* Analyst → limited create/update
* Admin → full control

---

### 5. Validation & Error Handling

* Input validation using serializers
* Proper HTTP status codes
* Clear and meaningful error messages

---

##  Tech Stack

* **Backend:** Django, Django REST Framework
* **Authentication:** JWT
* **Database:** SQLite (for simplicity)
* **Language:** Python

---

##  Project Structure

```
finance-dashboard-backend/
│
├── users/              # User & role management
├── records/            # Financial transactions
├── dashboard/          # Analytics APIs
├── core/               # Access control logic
├── finance_dashboard/  # Settings & configuration
└── manage.py
```

---

##  Setup Instructions

### 1. Clone Repository

```
git clone https://github.com/nitish1238/finance-dashboard-backend.git
cd finance-dashboard-backend
```

### 2. Create Virtual Environment

```
python -m venv venv
venv\Scripts\activate   # Windows
# source venv/bin/activate  # Linux/Mac
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

##  Testing

All backend tests pass successfully:

```
python manage.py test
```

 **98/98 tests passing**

---

##  API Endpoints

###  Authentication

```
POST /api/users/register/
POST /api/users/auth/login/
POST /api/users/auth/refresh/
```

---

###  Users

```
GET    /api/users/
POST   /api/users/
GET    /api/users/{id}/
PATCH  /api/users/{id}/
DELETE /api/users/{id}/

GET    /api/users/profile/
PATCH  /api/users/profile/

POST   /api/users/change-password/
POST   /api/users/{id}/activate/
POST   /api/users/{id}/deactivate/
```

---

###  Financial Records

```
GET    /api/records/
POST   /api/records/
GET    /api/records/{id}/
PUT    /api/records/{id}/
PATCH  /api/records/{id}/
DELETE /api/records/{id}/

GET    /api/records/categories/
GET    /api/records/statistics/
```

####  Filtering Examples

```
/api/records/?transaction_type=income
/api/records/?category=salary
/api/records/?start_date=2026-01-01&end_date=2026-03-31
/api/records/?min_amount=1000&max_amount=5000
/api/records/?search=salary
/api/records/?ordering=-date
```

---

###  Dashboard

```
GET /api/dashboard/summary/
GET /api/dashboard/category-breakdown/
GET /api/dashboard/monthly-trends/
GET /api/dashboard/recent-activity/
GET /api/dashboard/financial-health/
```

---

###  API Documentation

```
GET /api/docs/
GET /api/schema/
```

---

##  Example Request

### Login

```json
{
  "username": "admin",
  "password": "admin123"
}
```

---

### Create Transaction

```json
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

**Base URL:**
https://finance-dashboard-backend-jv22.onrender.com

**Swagger Docs:**
https://finance-dashboard-backend-jv22.onrender.com/api/docs/

---

##  Assumptions

* Categories are predefined based on transaction type
* Large expenses (>10000) are restricted
* Roles are predefined (Admin, Analyst, Viewer)
* Public registration assigns Viewer role by default

---

##  Design Decisions

* Modular app structure (users, records, dashboard)
* Role-based permissions enforced at API level
* Dashboard logic separated for scalability
* Focus on clarity, maintainability, and clean architecture

---

##  Future Improvements

* PostgreSQL database
* Docker support
* Caching (Redis)
* Rate limiting
* Soft delete support

---

##  Author

**Nitish Kumar**

---

##  Final Note

This project focuses on:

* Clean API design
* Logical data handling
* Role-based access control
* Scalable backend architecture

---

