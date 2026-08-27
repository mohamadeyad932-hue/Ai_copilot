# Backend API Fundamentals - Week 2

A modular, production-ready REST API built with **FastAPI**, **Pydantic v2**, **pydantic-settings**, and **Uvicorn**. This repository implements environment configuration, strict schema validation, custom HTTP middleware for request duration tracking and structured logging, automated unit testing with `pytest`, and containerization via `Dockerfile`.

---

## 📁 Project Structure

```text
copilot_ai/
├── app/
│   ├── __init__.py         # App package initialization
│   ├── config.py           # Pydantic Settings configuration & .env loader
│   ├── schemas.py          # Data validation models (Pydantic v2)
│   └── main.py             # FastAPI entrypoint, middleware & endpoints
├── tests/
│   ├── __init__.py         # Test package initialization
│   └── test_main.py        # Automated test suite using pytest & TestClient
├── .env.example            # Environment configuration template
├── Dockerfile              # Production multi-stage Docker build file
├── requirements.txt        # Production & development dependencies
└── README.md               # Complete documentation
```

---

## ⚙️ Environment Configuration

Environment configuration is managed via `app/config.py` using `pydantic-settings`.

Create a `.env` file from `.env.example`:

```bash
cp .env.example .env
```

### Supported Configuration Variables:

| Variable | Type | Default | Description |
| :--- | :--- | :--- | :--- |
| `APP_NAME` | `str` | `"Backend API Fundamentals"` | Application title |
| `APP_VERSION` | `str` | `"1.0.0"` | Semantic version |
| `DEBUG` | `bool` | `False` | Debug mode |
| `PORT` | `int` | `8000` | Server listening port |
| `HOST` | `str` | `"0.0.0.0"` | Host address binding |
| `LOG_LEVEL` | `str` | `"INFO"` | Logging verbosity (`DEBUG`, `INFO`, `WARNING`, `ERROR`) |

---

## 🚀 Local Setup & Installation

### 1. Prerequisites
- Python 3.11+
- Virtual environment tool (`venv` or `conda`)

### 2. Create and Activate Virtual Environment

**On Linux/macOS:**
```bash
python3 -m venv venv
source venv/bin/activate
```

**On Windows:**
```powershell
python -m venv venv
.\venv\Scripts\activate
```

### 3. Install Dependencies
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

---

## 🏃 Running the Application

Start the development server using **Uvicorn**:

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Once running, interactive documentation is available at:
- **Swagger UI**: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
- **ReDoc**: [http://127.0.0.1:8000/redoc](http://127.0.0.1:8000/redoc)

---

## 🧪 Automated Testing

Execute the unit test suite with `pytest`:

```bash
pytest -v
```

To view test coverage details:
```bash
pytest -v --tb=short
```

---

## 🐳 Docker Deployment

### 1. Build Docker Image
```bash
docker build -t backend-api-fundamentals .
```

### 2. Run Container
```bash
docker run -d -p 8000:8000 --env-file .env --name backend-api-app backend-api-fundamentals
```

### 3. Verify Container Status
```bash
curl http://localhost:8000/health
```

---

## 📡 API Endpoints Specification

### 1. Health Check Endpoint
- **URL**: `GET /health`
- **Description**: Returns operational status, app metadata, and system uptime.
- **Response `200 OK`**:
```json
{
  "status": "ok",
  "app_name": "Backend API Fundamentals",
  "version": "1.0.0",
  "uptime_seconds": 14.52
}
```

---

### 2. Text Analysis Endpoint
- **URL**: `POST /api/v1/analyze-text`
- **Description**: Processes non-AI metrics on the provided text string (character count, word count, line count, uppercase string, alphanumeric status, estimated reading time).
- **Request Headers**: `Content-Type: application/json`
- **Request Payload**:
```json
{
  "text": "FastAPI provides high performance and automatic interactive API documentation."
}
```

- **Response `200 OK`**:
```json
{
  "char_count": 75,
  "word_count": 9,
  "line_count": 1,
  "uppercase_text": "FASTAPI PROVIDES HIGH PERFORMANCE AND AUTOMATIC INTERACTIVE API DOCUMENTATION.",
  "is_alphanumeric": False,
  "estimated_reading_time_minutes": 0.05
}
```

- **Error Response `400 Bad Request`** (Whitespace or empty string):
```json
{
  "detail": "Text cannot be empty or contain only whitespace."
}
```

- **Error Response `422 Unprocessable Entity`** (Min length < 1 or Max length > 10,000):
```json
{
  "detail": [
    {
      "type": "string_too_long",
      "loc": ["body", "text"],
      "msg": "String should have at most 10000 characters",
      "input": "..."
    }
  ]
}
```

---

## ⚡ Custom HTTP Middleware & Headers

Every request processed by the API automatically passes through custom execution time middleware:
- **`X-Process-Time-Ms` Header**: Added to all HTTP responses, displaying the total request processing time in milliseconds (e.g. `X-Process-Time-Ms: 1.25`).
- **Structured Logs**: Logs request method, path, status code, and duration to standard output.
