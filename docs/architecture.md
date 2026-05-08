# 🏗️ System Architecture — AI Career Copilot

## High-Level Overview

AI Career Copilot follows a **monolithic full-stack architecture** designed for simplicity, fast iteration, and seamless deployment to containerized cloud environments like Google Cloud Run.

```
┌──────────────────────────────────────────────────────────────┐
│                        CLIENT (Browser)                       │
│  ┌──────────┐  ┌───────────┐  ┌────────────┐  ┌───────────┐ │
│  │  HTML/CSS │  │ Vanilla JS│  │  Chart.js  │  │Font Awesome│ │
│  └──────────┘  └───────────┘  └────────────┘  └───────────┘ │
└───────────────────────────┬──────────────────────────────────┘
                            │  HTTPS / REST API
                            ▼
┌──────────────────────────────────────────────────────────────┐
│                    FLASK APPLICATION SERVER                    │
│  ┌──────────────┐  ┌────────────┐  ┌───────────────────────┐ │
│  │  app.py       │  │ Static File│  │   API Routes          │ │
│  │  (Main Entry) │  │ Serving    │  │   /api/*              │ │
│  └──────────────┘  └────────────┘  └───────────────────────┘ │
│  ┌──────────────┐  ┌────────────┐  ┌───────────────────────┐ │
│  │ Auth Module   │  │ SQLAlchemy │  │   Flask-Login         │ │
│  │ (User/Session)│  │ ORM        │  │   Session Mgmt        │ │
│  └──────────────┘  └────────────┘  └───────────────────────┘ │
└───────────────────────────┬──────────────────────────────────┘
                            │
              ┌─────────────┼─────────────┐
              ▼             ▼             ▼
     ┌──────────────┐ ┌──────────┐ ┌──────────────┐
     │  AI Service   │ │  Resume  │ │  Job Service  │
     │  (Gemini API) │ │  Parser  │ │  (Adzuna API) │
     └──────────────┘ └──────────┘ └──────────────┘
              │                           │
              ▼                           ▼
     ┌──────────────┐            ┌──────────────┐
     │ Google Gemini │            │  Adzuna Jobs  │
     │ 2.5 Flash     │            │  REST API     │
     └──────────────┘            └──────────────┘
```

---

## Component Breakdown

### 🎨 Frontend Layer

| Component | Technology | Purpose |
|-----------|-----------|---------|
| Structure | HTML5 | Semantic markup with SPA-like page system |
| Styling | Vanilla CSS | Dark theme, CSS custom properties, responsive grid |
| Logic | Vanilla JavaScript | State management, API calls, DOM manipulation |
| Charts | Chart.js | Analytics visualizations |
| Icons | Font Awesome 6 | UI iconography |
| Typography | Google Fonts (Inter) | Modern, professional font family |

**Key Design Decisions:**
- **No framework overhead** — Pure vanilla JS for maximum performance and zero build step
- **SPA-like routing** — Page sections toggled via CSS classes, no page reloads
- **Progressive enhancement** — Works with mock data when APIs are unavailable

### ⚙️ Backend Layer

| Module | File | Responsibility |
|--------|------|----------------|
| Main Application | `backend/app.py` | Route handling, auth, database, business logic |
| AI Service | `backend/ai_service.py` | All Gemini API integrations with structured prompts |
| Resume Parser | `backend/resume_parser.py` | PDF text extraction via pdfplumber |
| Job Service | `backend/job_service.py` | Job listing aggregation (Adzuna + fallback) |

**Key Design Decisions:**
- **Concurrent AI requests** — `ThreadPoolExecutor` for parallel Gemini API calls during career analysis
- **Graceful degradation** — Mock data fallback when APIs hit rate limits (HTTP 429)
- **Cloud-ready paths** — Dynamic file paths (`/tmp` on Cloud Run, local otherwise)

### 💾 Data Layer

| Component | Technology | Purpose |
|-----------|-----------|---------|
| Database | SQLite | User accounts & analysis history |
| ORM | Flask-SQLAlchemy | Database abstraction |
| Auth | Flask-Login + Werkzeug | Session management & password hashing |

**Schema:**

```
┌─────────────┐       ┌───────────────────┐
│    User      │       │     History        │
├─────────────┤       ├───────────────────┤
│ id (PK)     │◄──┐   │ id (PK)           │
│ email       │   └───│ user_id (FK)      │
│ password    │       │ target_role        │
│ _hash       │       │ match_percentage   │
└─────────────┘       │ missing_skills     │
                      │ timestamp          │
                      └───────────────────┘
```

---

## Request Flow

### Resume Upload & Analysis

```
User drops PDF → Frontend FormData → POST /api/upload_resume
    → resume_parser.extract_text_from_pdf()
    → ai_service.analyze_resume() [Gemini API]
    → JSON response with ATS score, skills, improvements
    → Frontend renders dashboard with animated score rings
```

### Career Analysis (Deep)

```
User enters target role → POST /api/analyze_career
    → ThreadPoolExecutor spawns 4 concurrent tasks:
        1. match_role()           → Role fit percentage
        2. generate_roadmap()     → 30-day learning plan
        3. optimize_linkedin()    → Profile optimization
        4. analyze_resume()       → Skills extraction
    → job_service.fetch_jobs()    → Matched job listings
    → History saved to DB (if authenticated)
    → All results returned as single JSON payload
```

---

## Scalability Considerations

| Concern | Current Solution | Future Enhancement |
|---------|------------------|--------------------|
| Concurrent requests | Gunicorn with 2 workers + 4 threads | Horizontal scaling via Cloud Run auto-scaling |
| Database | SQLite (file-based) | PostgreSQL / Cloud SQL for multi-instance |
| File storage | Local `/tmp` | Cloud Storage (GCS) for persistent uploads |
| API rate limits | Mock data fallback | Redis-based request queuing & caching |
| Session state | Server-side Flask sessions | Redis-backed session store |

---

## Security Measures

- **Password hashing** with PBKDF2-SHA256 (Werkzeug)
- **CORS** configured for cross-origin safety
- **Session cookies** with `SameSite=Lax`
- **No secrets in code** — all credentials via environment variables
- **File cleanup** — uploaded PDFs are deleted after processing
- **Input validation** on all API endpoints
