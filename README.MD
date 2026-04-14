# Gender Analyzer API

A lightweight, production-ready RESTful API built with FastAPI that analyzes names and predicts gender-related properties using the external `genderize.io` service.

---

## 🚀 Overview

This API provides a simple endpoint to classify names and return:

* Gender prediction
* Probability score
* Sample size used for prediction
* Confidence indicator
* Timestamp of processing

It also includes:

* Rate limiting
* Custom error handling
* Input validation
* CORS configuration
* Health check endpoint

---

## 🧱 Tech Stack

* Python 3.10+
* FastAPI
* SlowAPI (Rate limiting)
* Uvicorn (ASGI server)

---

## 📁 Project Structure (Simplified)

```
.
├── main.py
├── core/
│   ├── config.py
│   ├── exceptions.py
│   └── error_handlers.py
├── services/
│   └── fetch_name_data.py
└── requirements.txt
```

---

## ⚙️ Installation

### 1. Clone the repository

```
git clone <your-repo-url>
cd <your-project>
```

### 2. Create virtual environment

```
python -m venv venv
source venv/bin/activate   # Linux/macOS
venv\\Scripts\\activate    # Windows
```

### 3. Install dependencies

```
pip install -r requirements.txt
```

---

## ▶️ Running the Application

Start the development server:

```
uvicorn main:app --reload
```

The API will be available at:

```
http://127.0.0.1:8000
```

Interactive docs:

```
http://127.0.0.1:8000/docs
```

---

## 📡 API Endpoints

### 1. Home

```
GET /
```

Response:

```json
{
  "success": true,
  "message": {
    "title": "Gender Analyzer",
    "about": "REST API for analyzing name-based gender"
  }
}
```

---

### 2. Health Check

```
GET /health
```

Response:

```json
{
  "success": true,
  "message": "Ok"
}
```

---

### 3. Classify Name

```
GET /api/classify?name=John
```

#### Query Parameters

| Parameter | Type   | Required | Description     |
| --------- | ------ | -------- | --------------- |
| name      | string | Yes      | Name to analyze |

#### Success Response

```json
{
  "status": "success",
  "data": {
    "name": "john",
    "gender": "male",
    "probability": 0.99,
    "sample_size": 12345,
    "is_confident": true,
    "processed_at": "2026-01-01T00:00:00Z"
  }
}
```

---

## ⛔ Error Handling

The API uses structured error responses:

| Status Code | Description                         |
| ----------- | ----------------------------------- |
| 400         | Bad Request (missing or empty name) |
| 404         | Name not found                      |
| 422         | Invalid input                       |
| 429         | Rate limit exceeded                 |
| 500         | Internal server error               |
| 502         | Bad Gateway                         |

Example:

```json
{
  "Status": "error",
  "message": "Too many requests, please slow down."
}
```

---

## 🚦 Rate Limiting

* Endpoint: `/api/classify`
* Limit: **8 requests per minute per IP**

---

## 🔍 Input Validation Logic

* Removes non-alphabetic characters
* Converts input to lowercase
* Rejects empty or invalid strings

---

## 🔄 Lifecycle Events

The app uses FastAPI lifespan events:

* Startup: Initializes rate limiter
* Shutdown: Graceful cleanup logging

---

## 🌐 CORS Configuration

Currently configured to allow all origins:

```python
allow_origins = ["*"]
```

⚠️ For production, restrict this to trusted domains.

---

## 🧪 Example Request

```
curl "http://127.0.0.1:8000/api/classify?name=Amaka"
```

---

## 🛠️ Future Improvements

* Add caching layer (Redis)
* Add authentication (API keys)
* Improve confidence scoring logic
* Logging & monitoring (Prometheus/Grafana)

---

## 📄 License

MIT License

---

## 👨‍💻 Author

James Kehinde

---


