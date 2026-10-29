# Resume AI Analyser and Job Tracker

A full-stack web app that scores a resume against a job description and tracks job applications.
Django REST API, React frontend, local semantic matching, and optional Claude wording suggestions.

## Features

- **Resume analysis:** upload a PDF or DOCX, including two-column PDFs, and paste a job description.
- **Transparent scoring:** five components (required skills, preferred skills, semantic match,
  evidence in projects or experience, section completeness) with adjustable weights.
  Weight sliders recalculate every score in the browser.
- **Evidence, not just a number:** shows matched and missing skills, skills listed but never
  demonstrated, and the resume passage that supports each matched requirement.
- **Job tracker:** add, edit, filter, search and delete applications, track status and interviews.
- **Linked analyses:** run an analysis from an application row, using its saved job description.
- **Dashboard:** totals, applications by status, upcoming interviews, recent analyses.
- **Accounts:** registration and login with token authentication. Every record belongs to one user.
- **Optional AI suggestions:** off by default. Rewords existing lines only, and rejects output
  that adds numbers or skills not in the original line.

## Tech stack

| Layer | Technology |
|---|---|
| Backend | Python 3.10, Django 5.2, Django REST Framework |
| Frontend | React, Vite |
| Parsing | pdfplumber (PDF), python-docx (DOCX) |
| Matching | Keyword vocabulary plus sentence-transformers `all-MiniLM-L6-v2` (runs locally) |
| Database | SQLite |
| Optional AI | Anthropic Claude API |

## Architecture

```
React (localhost:5173)  --JSON + token-->  Django REST API (127.0.0.1:8000)
                                              |
        accounts/      login, registration, tokens
        applications/  job tracker, dashboard
        analyser/      parsing, scoring, semantic matching, suggestions
                                              |
                                           SQLite
```

See [docs/architecture.md](docs/architecture.md) for the scoring pipeline and design decisions.

## Run it locally

Prerequisites: Python 3.10+, Node.js 18+, Git. These steps are for Windows PowerShell.

Backend, in the first terminal:

```powershell
python -m venv venv
.\venv\Scripts\Activate
pip install -r requirements.txt
copy .env.example .env
python manage.py migrate
python manage.py runserver
```

Frontend, in a second terminal:

```powershell
cd frontend
npm install
npm run dev
```

Open http://localhost:5173 and register an account. The first analysis is slow because the
embedding model (about 90 MB) downloads and loads once.

## Tests

```powershell
python manage.py test
```

50 tests cover authentication, per-user data isolation, upload validation, scoring, parsing,
the dashboard, and the suggestion validator. The Claude API is mocked, so tests never make
paid calls.

## API

All endpoints except health, register and login require the header `Authorization: Token <token>`.

| Method | Endpoint | Purpose |
|---|---|---|
| GET | `/api/health/` | Service status |
| POST | `/api/auth/register/`, `/api/auth/login/`, `/api/auth/logout/` | Accounts |
| GET, POST | `/api/applications/` | List (`?status=`, `?search=`) or create |
| GET, PATCH, DELETE | `/api/applications/<id>/` | One application |
| GET | `/api/dashboard/summary/` | Dashboard statistics |
| POST | `/api/analyse/` | Analyse a resume (multipart: `resume`, `job_description`, optional `application`, `two_column`) |
| GET | `/api/analyses/`, `/api/analyses/<id>/` | Saved analyses |
| GET | `/api/analyses/<id>/report/` | Text report download |
| POST | `/api/suggestions/` | Optional Claude suggestions, five per hour per user |

## Privacy

- Uploaded files are not stored. Only scores, skill lists and short evidence snippets are saved.
- The personal-details section of a resume is excluded from scoring and from matching.
- Suggestions are opt-in. When requested, only experience, project and summary text is sent to
  Anthropic for that single request.
- Never commit `.env`. The repository ships `.env.example` with placeholders only.

## Configuration

Copy `.env.example` to `.env`. `DJANGO_DEBUG=false` in production requires a real
`DJANGO_SECRET_KEY`, and the server refuses to start without one.

## Limitations

- The semantic threshold (0.40) was tuned on 24 hand-labelled pairs and is provisional.
- The skill vocabulary is a fixed list, so skills outside it are not recognised.
- Scanned PDFs need OCR, which is not implemented.
- The login token is stored in `localStorage` and does not expire. A production deployment
  should use short-lived tokens or an HttpOnly cookie.
- SQLite and the in-memory cache suit a single process. Several workers would need a shared
  database and cache.
- A match score measures wording overlap. It does not prove ability, and it is not an
  employer's ATS score.