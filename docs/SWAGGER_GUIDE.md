# FastAPI Swagger UI & OpenAPI Specification Guide

This guide explains how to access, inspect, and test the backend REST APIs using FastAPI's built-in interactive Swagger UI and ReDoc interfaces.

---

## 1. Accessing Interactive Documentation

When the FastAPI backend server is running (`python -m uvicorn app.main:app` or via Docker), access interactive documentation at:

- **Swagger UI Interactive Interface**: `http://localhost:8000/docs`
- **ReDoc Technical Specification**: `http://localhost:8000/redoc`
- **Raw OpenAPI JSON Schema**: `http://localhost:8000/api/v1/openapi.json`

---

## 2. Using Swagger UI for Interactive Testing

1. Open `http://localhost:8000/docs` in your browser.
2. Locate the desired endpoint group (e.g., `Transporters`, `Vehicles`, `AI Recognition`, `System`).
3. Click on an endpoint row (e.g., `POST /api/v1/vehicle-recognition/process-image`).
4. Click **Try it out**.
5. Fill in required body parameters or upload a test file binary.
6. Click **Execute**.
7. Inspect the **Curl command**, **Request URL**, **Response Body (JSON)**, and **HTTP Response Code** (e.g., `200 OK`, `201 Created`, `422 Validation Error`).

---

## 3. Swagger Authorize Button (JWT Tokens)

If authentication is enabled:
1. Click the **Authorize** button at the top right of the Swagger UI page.
2. Enter your JWT Access Token in format: `Bearer <your_token_here>`.
3. Click **Authorize** to attach headers to all subsequent test calls.
