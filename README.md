# Tour Ceylon — unified MVC monolith (Travel + SOS + Wellness)

One product with **one backend** and **one frontend folder** (4 apps inside).

## Architecture

**Modular monolith + MVC**

| Layer | Where |
|---|---|
| **Model** | `backend/app/models/` (travel + wellness) + `backend/app/sos_models.py` (SOS) |
| **View** | `frontend/travel`, `frontend/tourist`, `frontend/police`, `frontend/wellness` |
| **Controller** | `backend/app/routes/` (Flask blueprints) |
| **Service** | `backend/app/services/` (itinerary, SOS routing, wellness matching engine) |

One Flask process on **port 5002** serves Travel + SOS + Wellness APIs.

```
tour-ceylon/
├── backend/                 ← single API (MVC)
│   ├── app/                 ← models, routes, services
│   ├── data/
│   │   ├── travel/          ← travel Excel/CSV seed files
│   │   ├── sos/             ← hospitals, police, credentials
│   │   └── wellness/        ← candidate pool + evaluation files
│   ├── database/            ← schema.sql + migrations
│   ├── scripts/
│   │   ├── travel/          ← apply schema, seed travel data
│   │   ├── sos/             ← SOS helper scripts
│   │   └── wellness/        ← seed wellness centers
│   ├── seed_sos_data.py
│   └── run.py
└── frontend/
    ├── travel/              ← itinerary planner (:5180)
    ├── tourist/             ← SOS PWA (:5175)
    ├── police/              ← police dashboard (:5176)
    └── wellness/            ← Ayurveda / spiritual matcher (:5181)
```

The original standalone matcher still lives in `component/` (not deleted). Runtime code is the unified copy above.

## Quick start

### 1. Database

Create Postgres DB `travel_app`, then:

```bat
cd backend
copy .env.example .env
python -m venv .venv
.\.venv\Scripts\activate
python -m pip install -r requirements.txt
```

Apply travel schema + seed (from `backend/`):

```bat
cd backend
.\.venv\Scripts\activate
python scripts\travel\apply_schema.py
python scripts\travel\seed_data.py
python seed_sos_data.py
python scripts\wellness\seed_data.py
```

### 2. Backend (one server)

```bat
cd backend
.\.venv\Scripts\activate
python run.py
```

API: http://127.0.0.1:5002/api/health  
Wellness: http://127.0.0.1:5002/api/wellness/health

### 3. Frontends (one command)

First time only — install deps for all four apps:

```bat
cd frontend
npm install
npm run install:all
```

Then start **all four** with one command:

```bat
cd frontend
npm run dev
```

| App | URL |
|---|---|
| Travel | http://localhost:5180 |
| Tourist SOS | http://localhost:5175 |
| Police | http://localhost:5176 |
| Wellness matcher | http://localhost:5181 |
| Wellness admin | http://localhost:5181/admin |

Optional single app: `npm run dev:travel` / `dev:tourist` / `dev:police` / `dev:wellness`

## Auth

- Travel login/register: `POST /api/auth/login` with **email**
- Police login: `POST /api/auth/login` with **username**
- Tourist SOS: `/api/tourists/...`
- Wellness admin: `POST /api/admin/login` with the shared demo password (`WELLNESS_ADMIN_PASSWORD`, default `tourceylon2026`)

## GitHub

1. Create a new empty repo
2. Push this `tour-ceylon` folder
3. Add your friend as collaborator
4. Do **not** commit `.env` or `.venv`

Old folders `travel_app_sourse` and `tourist-sos-app` can stay as backups until you confirm this works.
