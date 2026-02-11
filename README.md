# Course Enrollment Platform

    # Project Overview

This project is a secure, database backed RESTful API built with FastAPI for managing a course enrollment platform.

This  system supports authentication,authorization, role based access control (RBAC), course management,and enrollment workflows,  Handles non trivial business rules. It enforces real world business rules and includes comprehensive automated tests.

###Features

      ### Authentication & Authorization

1. JWT Authentication (Secure user authentication with JSON Web Tokens)
2. Role Based Access Control (RBAC)
3. Course Management Create, read, update, and delete courses
4. Enrollment System, Students can enroll or deregister from course
5. Business Rules Enforcement, Validates capacity limits, duplicate enrollments, and   course status
6. Comprehensive TestingFull test coverage with automated tests
7. PostgreSQL Database, Relational database with proper migrations

     ## Tech Stack
1. FastAPI: Modern Python web framework
2. PostgreSQL: Relational database
3. SQLAlchemy: ORM for database operations
4. Alembic: Database migration tool
5. Pydantic: Data validation
6. JWT: Authentication tokens
7. Pytest: Testing framework
8. Bcrypt: Password hashing

    # Prerequisites
*Python 3.10+
*PostgreSQL


    #installation
git clone 
cd course-enrollment-platform

   #create virtual enviroment(venv)
python -m venv venv
source  venv\Scripts\activate (for windows)

   # Install dependencies
pip install -r requirements.txt

    #Setup enviroment variable(.env)
 Edit .env with your database credentials and generate SECRET_KEY:

   #Create database
*psql -U postgres -c "CREATE DATABASE course_enrollment_db;"

   #Run migration
#setup the database tables
*alembic upgrade head
verify migrations worked
*alembic current



# 7. Start server
uvicorn app.main:app --reload


#API Documentation:http://127.0.0.1:8000/docs

## Running Tests
# Run all tests
pytest / pytest -v(for a detailed output)

## API Overview

### Authentication
*`POST /api/v1/auth/register` - Register new user
* `POST /api/v1/auth/login` - Login and get JWT token

### Users
* `GET /api/v1/users/me` - Get current user profile (authenticated)

### Courses
* `GET /api/v1/courses/` - List all active courses (public)
* `GET /api/v1/courses/{id}` - Get course details (public)
* `POST /api/v1/courses/` - Create course (admin only)
* `PUT /api/v1/courses/{id}` - Update course (admin only)
* `DELETE /api/v1/courses/{id}` - Deactivate course (admin only)

### Enrollments
* `POST /api/v1/enrollments/` - Enroll in course (student only)
* `DELETE /api/v1/enrollments/{id}` - Deregister from course (student only)
* `GET /api/v1/enrollments/` - View all enrollments (admin only)
* `GET /api/v1/enrollments/course/{id}` - View course enrollments (admin only)
* `DELETE /api/v1/enrollments/admin/{id}` - Remove student from course (admin only)



