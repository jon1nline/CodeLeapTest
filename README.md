# Blog API Documentation

## Overview

This API provides functionality for user authentication and blog post management.
It allows users to register, login, create posts, and manage their own content.

## Technologies Used

- **Backend Framework:** Django REST Framework
- **Authentication:** JWT (JSON Web Tokens)
- **Database:** Postgres
- **Python Version:** 3.13.15

### Dependencies

- Django
- djangorestframework
- PyJWT
- django-cors-headers

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
- **Response:** Sets HTTP-only cookies with access and refresh tokens

---

### Blog Posts

#### List/Create Posts

- **URL:** `/blog/posts/`
- **Methods:**
  - `GET`: List all active posts
  - `POST`: Create a new post (requires authentication)
- **POST Request Body:**
  ```json
  {
    "title": "string",
    "content": "string",
    "author_ip": "string",
    "likes": 0
  }
  ```

#### Retrieve/Update/Delete Post

- **URL:** `/blog/posts/<int:pk>/`
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
2. User logs in via `/users/login/` which sets HTTP-only cookies:
   - `access_token`: Short-lived token for API access
   - `refresh_token`: Long-lived token for getting new access tokens
3. Subsequent requests automatically include these cookies for authentication

---

## Error Responses

- **401 Unauthorized:** Authentication failed or token is invalid
- **403 Forbidden:** User tries to modify another user's post
- **404 Not Found:** Resource does not exist
- **400 Bad Request:** Request data is invalid

---

## Security Features

- JWT authentication with HTTP-only cookies
- CSRF protection
- Secure and SameSite cookie attributes
- Password hashing
- Soft delete for posts (no permanent deletion)

---

## Testing the API

You can test the API using SwaggerUI:

- **SwaggerUI API:** [http://localhost:8000/swagger/](http://localhost:8000/swagger/)

### Example `cURL` command for creating a post:

```bash
curl -X POST http://localhost:8000/blog/posts/ \
  -H "Content-Type: application/json" \
  -H "Cookie: access_token=your_access_token_here" \
  -d '{"title":"My Post", "content":"This is my first post", "author_ip": "MyIP", likes: 0}'
```
