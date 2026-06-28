# Task Management System API

A secure, asynchronous task management API featuring user authentication, bcrypt password hashing, and user-isolated Task CRUD workflows. Built using **FastAPI**, **SQLAlchemy ORM**, **JWT**, and **PostgreSQL**.

The codebase adheres to the **Repository Pattern** to decouple database operations from application router handlers.

---

## 🚀 Key Features

*   **Repository Pattern Implementation**: Database access operations are fully isolated inside `UserRepository` and `TaskRepository`.
*   **JWT Authentication (OAuth2 Bearer)**: Protects endpoints via stateless JSON Web Tokens.
*   **Secure Password Storage**: Uses `bcrypt` to hash user passwords before storing them.
*   **Owner-Bound Isolation**: Ensures users can only view, edit, or delete tasks they own. Attempts to access other users' tasks result in authorization failures (`403 Forbidden`).

---

## 📁 File Structure

```bash
TaskManagementSystemApi/
├── auth.py          # JWT creation/decoding and password hashing/verification
├── database.py      # SQLAlchemy async engine and connection helpers
├── main.py          # FastAPI endpoints, authorization dependencies, and app config
├── models.py        # SQLAlchemy relational schemas (User, Task)
├── repositories.py  # Repository classes encapsulating DB queries (UserRepository, TaskRepository)
├── requirements.txt # Project dependencies
├── run.py           # Entry point file to launch the Uvicorn ASGI server
└── schemas.py       # Pydantic validation and serialization models
```

---

## 📊 Database Schema

```mermaid
erDiagram
    USERS {
        int id PK
        string username UK
        string password_hash
    }
    TASKS {
        int id PK
        string title
        string description
        string status
        int owner_id FK
    }
    USERS ||--o{ TASKS : "owns"
```

### 1. User Table (`users`)
*   `id`: Primary Key (Integer)
*   `username`: Unique String, Indexed
*   `password_hash`: String

### 2. Task Table (`tasks`)
*   `id`: Primary Key (Integer)
*   `title`: String, Indexed
*   `description`: Nullable String
*   `status`: String (Default: `"pending"`, e.g., `"pending"`, `"in_progress"`, `"completed"`)
*   `owner_id`: Foreign Key referencing `users.id` (ON DELETE CASCADE)

---

## 🔌 API Endpoints Summary

### General
*   `GET /`: Welcome index.

### Authentication (`/auth`)
*   `POST /auth/register`: Register a new user account.
*   `POST /auth/login`: Authenticate with `username` and `password` to obtain a JWT bearer token.

### Tasks (`/tasks`) — *Requires Authorization Header*
*   `POST /tasks`: Create a task owned by the authenticated user.
*   `GET /tasks`: Retrieve all tasks created by the authenticated user.
*   `GET /tasks/{task_id}`: Retrieve a specific task owned by the user.
*   `PUT /tasks/{task_id}`: Update task properties (e.g. title, description, status).
*   `DELETE /tasks/{task_id}`: Delete a task.

---

## 🛠️ Step-by-Step Setup

1.  **Configure PostgreSQL**
    Ensure PostgreSQL server is running on port `5432` with connection credentials:
    `postgresql+asyncpg://postgres:mysecretypassword@localhost:5432/postgres`

2.  **Initialize Environment & Install Packages**
    ```bash
    # Create the virtual environment
    python -m venv .venv
    
    # Activate the environment (Windows)
    .venv\Scripts\activate
    
    # Install Python packages
    pip install -r requirements.txt
    ```

3.  **Run the Server**
    ```bash
    python run.py
    ```
    The server will startup on `http://127.0.0.1:8000`. You can visit `http://127.0.0.1:8000/docs` to register users, log in, and test the task manager.
