# Bestiary Registry

## 1. Introduction
This project implements **EX1 (FastAPI Backend)** and **EX2 (Streamlit Frontend)**. It is a registry for managing a "Bestiary" of mythical creatures, allowing users to catalogue and view entities across different mythologies and danger levels.

## 2. Important Links
*   **Backend (Render)**: [https://bestiary-registry.onrender.com](https://bestiary-registry.onrender.com)
*   **Frontend (Streamlit)**: [https://bestiary-registry.streamlit.app](https://bestiary-registry.streamlit.app)
*   **API Documentation**: [https://bestiary-registry.onrender.com/docs](https://bestiary-registry.onrender.com/docs)

## 3. Backend
The backend is built with **FastAPI**. It provides full CRUD support for the main resources (Creatures and Classes) using **SQLite** for data persistence. It returns standard JSON responses with appropriate HTTP status codes (e.g., 404 for missing resources, 422 for validation errors).

## 4. Frontend
The frontend is built with **Streamlit**. It allows users to view the existing registry of creatures fetched from the backend. CRUD actions (Create, Read, Update, Delete) are **fully implemented** and working, allowing users to summon, edit, and banish entities directly from the UI.

## 5. Avatars
Creature avatars are generated using the external **DiceBear Identicon API**. These are simple deterministic images based on the creature's name; no AI or machine learning generation is involved.

## 6. Testing
Automated tests are implemented using `pytest` and `FastAPI TestClient`.
To run the full test suite (Backend + Frontend workflows), use the following verified command:

```powershell
uv run python -m pytest tests/ ../frontend/tests/
# (Run from the 'backend' directory)
```

**Status**: All tests pass successfully.

## 7. Code Quality
The project uses `ruff` for code formatting and linting.
To verify code quality, the following commands are used:

```powershell
uv run ruff check .
uv run ruff format --check .
```

## 8. Local Development (Quick Start)
### Backend
1.  Navigate to the backend directory:
    ```powershell
    cd backend
    ```
2.  Install dependencies and run the server:
    ```powershell
    uv sync
    uv run python main.py
    ```
    *API will run at http://localhost:8000*

### Frontend
1.  Open a new terminal and navigate to the `backend` directory (to leverage the existing environment):
    ```powershell
    cd backend
    ```
2.  Run the Streamlit app:
    ```powershell
    uv run python -m streamlit run ../frontend/dashboard.py
    ```
    *Dashboard will open at http://localhost:8501*

## 9. Docker (Alternative)
The backend is dockerized. A `Dockerfile` exists and builds successfully.
If you prefer running via Docker:

```powershell
docker build -t bestiary-backend ./backend
docker run -d -p 8000:8000 bestiary-backend
```

## 10. Note
This project serves as a foundation for further course work.