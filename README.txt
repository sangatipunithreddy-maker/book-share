# BookShare — Python (Django + DRF) Backend + Frontend

## Backend (Django)
1) Open a terminal:
```
cd backend_django
python -m venv venv
# Windows: venv\Scripts\activate
# Linux/Mac: source venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver 0.0.0.0:8000
```
API base: http://127.0.0.1:8000/api

### Endpoints
- POST `/api/auth/register`  → {name,email,password,role,year,branch}
- POST `/api/auth/login`     → {email,password,role}
- GET  `/api/auth/me`        → Header `Authorization: Bearer <token>`

On first `migrate`, demo users are seeded automatically:
- student@bookshare.edu / student123 (student)
- faculty@bookshare.edu / faculty123 (faculty)
- admin@bookshare.edu   / admin123   (admin)

## Frontend
Open `frontend/` in VS Code → **Open with Live Server** on `index.html`.
(Frontend calls Django at http://127.0.0.1:8000/api)

If you had older Node backend, this version **replaces** it with Python.

## Notes
- Uses Django REST Framework + SimpleJWT for tokens
- SQLite DB file: `backend_django/bookshare.db`
- Custom user model extends AbstractUser with fields: role, year, branch (email is unique)


## Database for the whole project (Django models)
Included tables:
- User (custom, with role/year/branch)
- Ad (book ads, owner = seller)
- Material (faculty uploads, admin verifies)
- InterviewPost (blog)
- Notification (per user)
- ReportedAd (flag invalid ads)

### New API routes
- /api/ads/                 (GET list, POST create, PUT/PATCH/DELETE by owner)
- /api/ads/mine/            (GET your ads)
- /api/materials/           (CRUD; create by faculty, verify by admin: POST /materials/{id}/verify/)
- /api/interviews/          (CRUD by author)
- /api/notifications/       (GET your notifications; POST /notifications/{id}/mark_read/)
- /api/reports/             (CRUD; admin can resolve: POST /reports/{id}/resolve/)

### After pulling this update
Run migrations again:
```
cd backend_django
source venv/bin/activate    # or venv\Scripts\activate on Windows
python manage.py makemigrations api
python manage.py migrate
python manage.py runserver 0.0.0.0:8000
```
Then open the frontend with Live Server again.


---------------------------------------------
## Database moved to a separate folder

The SQLite file now lives in:
```
backend_django/db/bookshare.db
```

Django `settings.py` is updated to use that path.

### Run migrations (after moving DB path)
```
cd backend_django
# activate venv ...
python manage.py makemigrations api
python manage.py migrate
python manage.py runserver 0.0.0.0:8000
```

### Backup command
We added a management command to create timestamped backups:
```
cd backend_django
python manage.py backupdb
```
Backups will be created in:
```
backend_django/backups/
```
with filenames like `bookshare-YYYYMMDD-HHMMSS.db`.
