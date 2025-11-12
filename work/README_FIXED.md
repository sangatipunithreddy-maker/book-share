# Bookshare — Fixed & Ready

This package contains a cleaned backend (Django) and a static frontend.

## Run Backend (Django)

```bash
cd backend_django
python -m venv venv
# Windows PowerShell:
venv\Scripts\activate
# macOS/Linux:
# source venv/bin/activate

pip install -r requirements.txt
python manage.py makemigrations
python manage.py migrate
python manage.py runserver
```

Server will be at: http://127.0.0.1:8000/

## Run Frontend (Static)

Open `frontend/index.html` directly in the browser, or use the VS Code **Live Server** extension:
- Right-click `index.html` → **Open with Live Server**

## Notes

- Database is stored at `backend_django/db.sqlite3`
- CORS is enabled for dev (`CORS_ALLOW_ALL_ORIGINS = True`)
- Custom user model is `api.User` (ensure your `api` app has the model and migrations)
