# Natachat AI

This is a modern AI chat application for document management and intelligent conversations.

## How to run the project

### Backend

1.  Navigate to the `api` directory:
    ```bash
    cd api
    ```
2.  Install the dependencies from `pyproject.toml`:
    ```bash
    pip install "fastapi[standard]>=0.118.0" "google-genai>=1.42.0" "pwdlib[argon2]>=0.2.1" "pyjwt>=2.10.1" "requests>=2.32.5" "sqlmodel>=0.0.25" "websockets>=15.0.1"
    ```
3.  Run the backend server:
    ```bash
    uvicorn main:app
    ```
    The server will be running on `http://127.0.0.1:8000`.

### Frontend

1.  Navigate to the `ui` directory:
    ```bash
    cd ui
    ```
2.  Install the dependencies:
    ```bash
    npm install
    ```
3.  Run the frontend server:
    ```bash
    npm run dev
    ```
    The server will be running on `http://127.0.0.1:8080`.

Note: You need to have Python 3.10+ and Node.js installed on your system.
