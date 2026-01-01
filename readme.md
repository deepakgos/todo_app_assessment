# To-Do List Application

A Flask-based To-Do List web application that provides RESTful APIs for managing tasks and HTML templates for user interaction.  
The application uses raw SQL with SQLite for persistence and avoids ORM and generic viewsets as per assessment requirements.

---

## Features

- Create, view, and delete tasks via REST APIs
- HTML-based UI using Jinja2 templates
- SQLite database with raw SQL (no ORM)
- Automatic database initialization using `schema.sql`
- Logging and exception handling
- Automated API tests using pytest

---

## Tech Stack

- Python 3.10+
- Flask
- SQLite
- Pytest
- Jinja2 Templates

---

## Project Structure

```bash
todo_app_assessment/
│
├── todo_app/
│ ├── __init__.py
│ ├── app.py # Flask application & API routes
│ ├── db.py # Database connection logic
│ ├── schema.sql # SQL schema for tasks table
│ ├── tasks.db # SQLite database (auto-generated)
│ └── templates/
│ ├── base.html
│ ├── tasks.html
│ └── add_task.html
│
├── tests/
│ ├── __init__.py
│ └── test_tasks_api.py
│
├── requirements.txt
├── README.md
└── .gitignore
```

---

## Setup Instructions

### 1. Clone the Repository
```bash
git clone https://github.com/deepakgos/todo_app_assessment.git
cd todo_app_assessment
```

### 2. Create Virtual Environment
```bash
python -m venv .venv
.venv\Scripts\activate     # Windows
# source .venv/bin/activate  # macOS/Linux
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

## Running the Application
```bash
python -m todo_app.app
```

- The application will be available at:
```bash
http://127.0.0.1:8000
```

## Database Initialization

- The SQLite database is automatically initialized on application startup.

- SQLite creates the database file (tasks.db) on first connection
- The schema is applied using schema.sql
- No manual database setup is required

## API Documentation

### Create Task

#### POST /api/tasks

- Request:
```bash
{
  "title": "Buy groceries",
  "description": "Milk, Bread",
  "due_date": "2025-01-10",
  "status": "pending"
}
```
- Response:
```bash
{
  "id": 1,
  "message": "Task created"
}
```

### Get All Tasks

#### GET /api/tasks

- Response:
```bash
[
  {
    "id": 1,
    "title": "Buy groceries",
    "description": "Milk, Bread",
    "due_date": "2025-01-10",
    "status": "pending"
  }
]
```

### Get Task by ID
- **GET** `/api/tasks/<id>`

### Delete Task
- **DELETE** `/api/tasks/<id>`

### Web Interface

- `/` → View all tasks
- `/add` → Add a new task

- The UI communicates with the backend using the same REST APIs.

### Running Tests
```bash
pytest
```
- All API endpoints are covered with automated tests.

## Logging & Error Handling

- Application-level logging is enabled

- API errors are handled gracefully with appropriate HTTP responses

## Notes
- ORM and generic viewsets are intentionally not used
- Raw SQL ensures explicit and controlled database operations
- Schema-driven initialization keeps database logic simple and transparent
