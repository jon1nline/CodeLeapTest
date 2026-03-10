# Blog API Documentation

## Overview

This API provides functionality for user authentication and blog post management.
It allows users to register, login, create posts, and manage their own content.

## Technologies Used

- **Backend Framework:** Django REST Framework
- **Authentication:** JWT (SimpleJWT)
- **Database:** PostgreSQL 16
- **Python Version:** 3.11

### Dependencies

- Django
- djangorestframework
- djangorestframework-simplejwt
- django-cors-headers
- drf-yasg
- python-dotenv
- psycopg2-binary

---

## Local Installation

### Prerequisites

- Python 3.12+ installed
- `pip` package manager
- Virtual environment (recommended)

### Setup Steps

1. **Clone the repository**
   ```bash
   git clone https://github.com/jon1nline/CodeLeapTest.git
   cd CodeLeapTest
   ```

2. **Create and activate a virtual environment**
   ```bash
   python -m venv venv
   # On Windows
   venv\Scripts\activate
   # On macOS/Linux
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run database migrations**
   ```bash
   python manage.py migrate
   ```

5. **Create a superuser (optional)**
   ```bash
   python manage.py createsuperuser
   ```

6. **Start the development server**
   ```bash
   python manage.py runserver
   ```

   The API will be available at:
   **http://localhost:8000/**

7. **Install pre-commit hooks (recommended)**
   ```bash
   pre-commit install
   ```

8. **Run lint/format hooks manually**
   ```bash
   pre-commit run --all-files
   ```

---

## Docker Setup

### Prerequisites

- Docker and Docker Compose installed

### Steps

1. **Copy and configure environment**
   ```bash
   cp .env.example .env
   # Edit .env with your values
   ```

2. **Start all services** (API + PostgreSQL)
   ```bash
   docker compose up --build
   ```

   Migrations run automatically on startup.
   The API will be available at **http://localhost:8000/**

3. **Stop services**
   ```bash
   docker compose down
   ```

   To also remove the database volume:
   ```bash
   docker compose down -v
   ```

---

## API Endpoints

### Authentication

#### User Registration

- **URL:** `/users/register/`
- **Method:** `POST`
- **Description:** Register a new user
- **Request Body:**
  ```json
  {
    "username": "string",
    "password": "string",
    "email": "string"
  }
  ```

#### User Login

- **URL:** `/users/login/`
- **Method:** `POST`
- **Description:** Authenticate user and get JWT tokens
- **Request Body:**
  ```json
  {
    "username": "string",
    "password": "string"
  }
  ```
- **Response:** Returns `access` and `refresh` tokens

#### Refresh Access Token

- **URL:** `/users/refresh/`
- **Method:** `POST`
- **Description:** Generate a new access token from a valid refresh token
- **Request Body:**
  ```json
  {
    "refresh": "string"
  }
  ```

---

### Blog Posts

#### List/Create Posts

- **URL:** `/posts/`
- **Methods:**
  - `GET`: List all active posts
  - `POST`: Create a new post (requires authentication)
- **POST Request Body:**
  ```json
  {
    "title": "string",
    "content": "string"
  }
  ```

- **GET Response:** Paginated (`count`, `next`, `previous`, `results`)

  #### Swagger documentation

- **URL:** `/docs`

---

#### Retrieve/Update/Delete Post

- **URL:** `/posts/<int:pk>/`
- **Methods:**
  - `PATCH`: Update a post (only by owner)
  - `DELETE`: Soft delete a post (only by owner)
- **PATCH Request Body:**
  ```json
  {
    "title": "string",
    "content": "string"
  }
  ```

---

## Authentication Flow

1. User registers via `/users/register/`
2. User logs in via `/users/login/` and receives `access` and `refresh`
3. When access expires, call `/users/refresh/` with `refresh` to get a new `access`
4. To use the token: add `Authorization: Bearer <access_token>`

---

## Error Responses

- **401 Unauthorized:** Authentication failed or token is invalid
- **403 Forbidden:** User tries to modify another user's post
- **404 Not Found:** Resource does not exist
- **400 Bad Request:** Request data is invalid

---

## Security Features

- JWT authentication with Bearer token (SimpleJWT)
- CSRF protection
- Secure and SameSite cookie attributes
- Password hashing
- Soft delete for posts (no permanent deletion)

---

## Testing the API

You can test the API using SwaggerUI:

- **SwaggerUI API AWS DEPLOY:** [http://54.242.30.117/docs/](http://54.242.30.117/docs/)

### Example `cURL` command for creating a post:

```bash
curl -X POST http://localhost:8000/posts/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <your_access_token_here>" \
  -d '{"title":"My Post", "content":"This is my first post"}'
```
