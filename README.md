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
├── permissions/     # Role-based access logic
├── config/          # Settings & main config
└── manage.py
```

---

##  Setup Instructions

### 1. Clone Repository

```
git clone <your-repo-link>
cd finance-dashboard-backend
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

##  API Endpoints (Examples)

### Auth

```
POST /api/auth/login/
POST /api/auth/register/
```

### Users (Admin only)

```
GET    /api/users/
POST   /api/users/
PATCH  /api/users/{id}/
DELETE /api/users/{id}/
```

### Financial Records

```
GET    /api/records/
POST   /api/records/
PUT    /api/records/{id}/
DELETE /api/records/{id}/
```

### Dashboard

```
GET /api/dashboard/summary/
GET /api/dashboard/trends/
GET /api/dashboard/category-breakdown/
```

---

## 🔍 Example Request

### Create Record

```json
POST /api/records/

{
  "amount": 5000,
  "type": "income",
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
  "amount": 5000,
  "type": "income",
  "category": "salary",
  "date": "2026-04-01"
}
```

---

##  Deployment

👉 (Add your deployed link here)

Example:

```
Live API: https://your-api-url.com
```

---

##  Assumptions

* SQLite used for simplicity
* Authentication handled via JWT
* Roles are predefined (Admin, Analyst, Viewer)
* System designed for demonstration, not production

---

##  Design Decisions

* Separated apps for modular structure
* Used DRF for fast API development
* Implemented role-based permissions for security
* Focused on clarity and maintainability over complexity

---

##  Future Improvements

* Swagger API documentation
* Unit & integration tests
* PostgreSQL database
* Docker support
* Caching for dashboard APIs
* Rate limiting

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
