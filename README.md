# ⚔️ NinjaFastAPI

NinjaFastAPI is a backend API built with FastAPI for managing ninjas, teams and villages in a Naruto-inspired world.

The main goal of this project was to deepen my practical knowledge of FastAPI by building a larger backend application with strong business logic, validation, testing and clean project organization.

This project includes authentication, filtering, sorting, pagination, avatar upload, and extensive test coverage.

---

## 🚀 Features

- JWT authentication
    - user registration
    - user login
    - protected endpoints

- Ninja management
    - create and read ninjas
    - training and resting actions
    - chakra and experience system
    - rank progression
    - business rules for dead and forbidden ninjas

- Teams management
    - assigning a sensei
    - team member validation
    - business rules for team composition

- Villages management
    - assigning ninjas to villages
    - setting kage
    - validation rules for village leadership

- Query support
    - filtering
    - sorting
    - pagination

- User avatars
    - file upload with multipart/form-data
    - avatar extension validation
    - saving files to local storage

- Strong quality assurance
    - 200+ tests
    - unit tests
    - integration tests
    - TDD approach
    - API schema testing with Schemathesis

---

## 🛠 Tech Stack

- FastAPI
- SQLAlchemy
- PostgreSQL
- Alembic
- Pytest
- Schemathesis
- Docker
- Docker Compose
- JWT / python-jose
- Black
- Ruff
- GitHub Actions

---

## 🧪 Testing

This project was developed with a strong TDD approach and contains more than 200 tests.

Run tests locally:

pytest

Run tests with Docker:

docker-compose run --rm app sh -c "pytest"

Run linting:

black .
ruff check .

Run API schema tests with Schemathesis:

schemathesis run http://127.0.0.1:8000/openapi.json

---

## ⚙️ Running the project

git clone <your-repository-url>
cd NinjaFastAPI
docker-compose up --build
alembic upgrade head

API docs:

http://127.0.0.1:8000/docs

---

## 📡 Example Endpoints

### Auth
- POST /auth/register
- POST /auth/login
- POST /auth/me/avatar

### Ninjas
- GET /ninja/
- GET /ninja/my_ninjas
- GET /ninja/my_ninjas/{ninja_id}
- POST /ninja/my_ninjas/{ninja_id}/train
- POST /ninja/my_ninjas/{ninja_id}/rest

### Teams
- GET /team/

### Villages
- GET /village/
- GET /village/{village_id}
- POST /village/{village_id}/add_ninja_to_village/{ninja_id}
- POST /village/{village_id}/set_kage/{ninja_id}

---

## 📂 Project Structure
~~~
NinjaFastAPI/
├── .github/
├── app/
│   ├── auth/
│   ├── models/
│   ├── routers/
│   ├── schemas/
│   ├── __init__.py
│   ├── db_connection.py
│   └── main.py
├── media/
│   └── avatars/
├── migrations/
├── scripts/
├── tests/
├── .env
├── .gitignore
├── .pre-commit-config.yaml
├── alembic.ini
├── docker-compose.yml
├── Dockerfile
├── logging.conf
├── pyproject.toml
├── pytest.ini
└── requirements.txt
~~~

---

## 🧠 What this project focuses on

- FastAPI backend development
- API design
- business logic implementation
- SQLAlchemy models and relationships
- authentication with JWT
- filtering, sorting and pagination
- file upload handling
- PostgreSQL integration
- Dockerized development workflow
- test-driven development
- schema-based API testing with Schemathesis

This is not my first backend project — I had already worked with TDD, Docker and PostgreSQL before.  
The main purpose here was to go deeper into FastAPI and build a more complete backend API with broader validation and stronger automated testing.

---

## 🔄 CI / Code Quality

- GitHub Actions for CI
- Black for formatting
- Ruff for linting
- Pytest for testing
- Schemathesis for API validation

---

## 🔮 Possible future improvements

- async chat with WebSockets
- notifications
- Redis-based background features
- cloud file storage (S3)
- more advanced user profiles

---

## 👨‍💻 Author

Kamil Kalicki  
GitHub: https://github.com/Kali2114

---

## 📌 Status

Portfolio backend project focused on FastAPI, testing, validation and real-world API structure.  
Project is near completion.
EOF