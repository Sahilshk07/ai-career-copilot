<p align="center">
  <img src="https://img.shields.io/badge/AI-Career_Copilot-0070f3?style=for-the-badge&logo=rocket&logoColor=white" alt="AI Career Copilot"/>
</p>

<h1 align="center">🚀 AI Career Copilot</h1>

<p align="center">
  <strong>Your AI-Powered Career Intelligence Platform</strong><br/>
  Upload your resume, get instant ATS analysis, personalized job matches, skill gap insights, mock interviews, and a 30-day career roadmap — all powered by Google Gemini AI.
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.11+-3776AB?style=flat-square&logo=python&logoColor=white" alt="Python"/>
  <img src="https://img.shields.io/badge/Flask-3.0-000000?style=flat-square&logo=flask&logoColor=white" alt="Flask"/>
  <img src="https://img.shields.io/badge/Gemini_AI-2.5_Flash-4285F4?style=flat-square&logo=google&logoColor=white" alt="Gemini"/>
  <img src="https://img.shields.io/badge/Docker-Ready-2496ED?style=flat-square&logo=docker&logoColor=white" alt="Docker"/>
  <img src="https://img.shields.io/badge/Cloud_Run-Deployed-4285F4?style=flat-square&logo=google-cloud&logoColor=white" alt="Cloud Run"/>
  <img src="https://img.shields.io/badge/License-MIT-green?style=flat-square" alt="License"/>
</p>

---

## 📋 Table of Contents

- [Why This Project](#-why-this-project)
- [Features](#-features)
- [Screenshots](#-screenshots)
- [Tech Stack](#-tech-stack)
- [Architecture](#-architecture)
- [Getting Started](#-getting-started)
- [Environment Variables](#-environment-variables)
- [API Endpoints](#-api-endpoints)
- [Deployment](#-deployment)
- [Performance & Scalability](#-performance--scalability)
- [Future Improvements](#-future-improvements)
- [License](#-license)
- [Author](#-author)

---

## 💡 Why This Project

The job market is brutally competitive. Candidates spend hours tailoring resumes, searching for jobs, and preparing for interviews — often without knowing if they're on the right track.

**AI Career Copilot solves this** by providing an all-in-one AI-powered platform that:

- 🔍 Analyzes resumes like a recruiter would (ATS scoring, skill extraction)
- 🎯 Matches candidates to the right jobs based on their actual skillset
- 🧩 Identifies exact skill gaps for any target role
- 🎤 Conducts mock interviews with AI-powered evaluation
- 🗺️ Generates personalized 30-day career roadmaps
- 📄 Builds ATS-optimized resumes from scratch

> This isn't a toy project — it's a production-deployed SaaS application with real AI integration, user authentication, and cloud infrastructure.

---

## ✨ Features

| Feature | Description |
|---------|-------------|
| 📄 **Resume Upload & Parsing** | Upload PDF resumes with drag-and-drop; AI extracts skills, experience, and education |
| 📊 **ATS Score Analysis** | Get a realistic ATS compatibility score with actionable improvement tips |
| 🎯 **Smart Job Matching** | AI-curated job listings matched to your extracted skill profile |
| 🧩 **Skill Gap Analyzer** | Compare your skills against any target role; see what's missing |
| 🎤 **Mock Interviews** | Practice with AI-generated questions; get instant scoring and feedback |
| 🗺️ **Career Roadmap** | Personalized 30-day plan with weekly goals, projects, and courses |
| 🔗 **LinkedIn Optimizer** | AI-generated headlines, about sections, and post ideas |
| 📝 **Resume Generator** | Build professional, ATS-optimized resumes from your details |
| 🔐 **User Authentication** | Sign up/login to save analysis history across sessions |
| 📈 **Analytics Dashboard** | Track your progress with skill gap charts and history |
| 🌓 **Mock/Live Toggle** | Seamlessly switch between mock data and live AI for demos |

---

## 📸 Screenshots

<details>
<summary><strong>🏠 Landing Page</strong></summary>
<br/>

> Hero section with animated upload zone, "How It Works" steps, and feature grid.
>
> *Screenshot: Upload your resume with drag-and-drop, modern dark UI with gradient accents.*

</details>

<details>
<summary><strong>📊 Dashboard — ATS Score & Analysis</strong></summary>
<br/>

> Animated score rings showing ATS score and role match percentage, with tabbed panels for strengths, weaknesses, skills, and improvement tips.
>
> *Screenshot: Dashboard with circular progress indicators and data-rich analysis panels.*

</details>

<details>
<summary><strong>🎯 Job Matches</strong></summary>
<br/>

> AI-curated job cards with company, location, match percentage, and direct apply links. Filterable by role and location.
>
> *Screenshot: Grid of job cards with "Best Match" badge and skill tags.*

</details>

<details>
<summary><strong>🧩 Skill Gap Analyzer</strong></summary>
<br/>

> Visual comparison of matched vs. missing skills with priority-based learning recommendations.
>
> *Screenshot: Score ring, skill tags (green for matched, red for missing), and recommendation cards.*

</details>

<details>
<summary><strong>🎤 Mock Interview</strong></summary>
<br/>

> Interactive interview session with progress tracking, category/difficulty chips, and detailed AI feedback with model answers.
>
> *Screenshot: Question card with answer textarea, feedback panel with score ring and STAR-method tips.*

</details>

---

## 🛠️ Tech Stack

### Frontend
| Technology | Purpose |
|-----------|---------|
| HTML5 | Semantic structure |
| Vanilla CSS | Custom dark theme with CSS variables, glassmorphism, animations |
| Vanilla JavaScript | SPA-like routing, state management, API integration |
| Chart.js | Analytics visualizations |
| Font Awesome 6 | Icon system |
| Google Fonts (Inter) | Typography |

### Backend
| Technology | Purpose |
|-----------|---------|
| Python 3.11 | Runtime |
| Flask 3.0 | Web framework & API server |
| Google Gemini 2.5 Flash | AI-powered analysis, matching, and generation |
| pdfplumber | PDF text extraction |
| Flask-SQLAlchemy | SQLite ORM |
| Flask-Login | Session-based authentication |
| Werkzeug | Password hashing (PBKDF2-SHA256) |
| Gunicorn | Production WSGI server |

### Infrastructure
| Technology | Purpose |
|-----------|---------|
| Docker | Containerization |
| Google Cloud Run | Serverless deployment |
| SQLite | Database (development) |
| Adzuna API | Real-time job listings |

---

## 🏗️ Architecture

```
ai-career-copilot/
├── backend/
│   ├── app.py                # Main Flask application & API routes
│   ├── ai_service.py         # Gemini AI integration (analysis, matching, roadmap)
│   ├── resume_parser.py      # PDF text extraction service
│   ├── job_service.py        # Job listing aggregation (Adzuna + fallback)
│   └── requirements.txt      # Python dependencies
├── frontend/
│   ├── index.html            # SPA-like single page application
│   ├── style.css             # Complete dark theme design system
│   └── script.js             # Client-side logic & state management
├── docs/
│   ├── architecture.md       # System architecture deep-dive
│   ├── deployment.md         # Step-by-step deployment guide
│   └── api-reference.md      # Complete API documentation
├── uploads/                  # Temporary file storage (git-ignored)
├── .env.example              # Environment variable template
├── .gitignore                # Git ignore rules
├── .dockerignore             # Docker build ignore rules
├── Dockerfile                # Production container config
├── LICENSE                   # MIT License
└── README.md                 # This file
```

> For a detailed architecture overview with system diagrams, see **[docs/architecture.md](docs/architecture.md)**

---

## 🚀 Getting Started

### Prerequisites

- **Python 3.11+** installed
- **Google Gemini API Key** — [Get one free](https://aistudio.google.com/app/apikey)

### Installation

```bash
# 1. Clone the repository
git clone https://github.com/Sahilshk07/ai-career-copilot.git
cd ai-career-copilot

# 2. Create virtual environment
python -m venv venv

# 3. Activate it
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# 4. Install dependencies
pip install -r backend/requirements.txt

# 5. Set up environment variables
cp .env.example .env
# Edit .env and add your GEMINI_API_KEY

# 6. Run the app
python backend/app.py
```

🎉 Open **http://localhost:5000** in your browser.

---

## 🔑 Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `GEMINI_API_KEY` | ✅ | Google Gemini API key for AI features |
| `SECRET_KEY` | ✅ | Flask session secret (generate a strong random key) |
| `ADZUNA_APP_ID` | ⬜ | Adzuna API app ID for live job listings |
| `ADZUNA_APP_KEY` | ⬜ | Adzuna API key |
| `PORT` | ⬜ | Server port (default: 5000, auto-set on Cloud Run) |

> See [`.env.example`](.env.example) for the full template with setup instructions.

---

## 📡 API Endpoints

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| `GET` | `/api/user` | ⬜ | Check auth status |
| `POST` | `/api/signup` | ⬜ | Create account |
| `POST` | `/api/login` | ⬜ | Sign in |
| `POST` | `/api/logout` | 🔒 | Sign out |
| `POST` | `/api/upload_resume` | ⬜ | Upload & analyze PDF resume |
| `POST` | `/api/analyze_career` | ⬜ | Deep career analysis with target role |
| `POST` | `/api/skill_gap` | ⬜ | Skill gap analysis |
| `POST` | `/api/interview/questions` | ⬜ | Generate interview questions |
| `POST` | `/api/interview/evaluate` | ⬜ | Evaluate interview answer |
| `POST` | `/api/generate_resume` | ⬜ | AI resume generation |
| `GET` | `/api/history` | 🔒 | Analysis history |
| `GET` | `/api/analytics` | 🔒 | Skill gap analytics |

> Full request/response documentation: **[docs/api-reference.md](docs/api-reference.md)**

---

## ☁️ Deployment

### Docker

```bash
docker build -t ai-career-copilot .
docker run -p 8080:8080 -e PORT=8080 -e GEMINI_API_KEY=your_key ai-career-copilot
```

### Google Cloud Run

```bash
gcloud run deploy ai-career-copilot \
  --source . \
  --port 8080 \
  --region us-central1 \
  --allow-unauthenticated
```

> Full deployment guide with Docker Compose, secrets management, and troubleshooting: **[docs/deployment.md](docs/deployment.md)**

---

## ⚡ Performance & Scalability

| Optimization | Implementation |
|-------------|----------------|
| **Concurrent AI Calls** | `ThreadPoolExecutor` runs 4 Gemini API calls in parallel during career analysis |
| **Graceful Degradation** | Automatic mock data fallback when APIs hit rate limits (429/RESOURCE_EXHAUSTED) |
| **Production Server** | Gunicorn with 2 workers + 4 threads per worker |
| **Auto-Scaling** | Cloud Run scales from 0 to N instances based on traffic |
| **Minimal Bundle** | Zero frontend build step — vanilla HTML/CSS/JS serves instantly |
| **File Cleanup** | Uploaded PDFs are automatically deleted after processing |
| **Efficient Docker** | Multi-stage-ready slim Python image, `.dockerignore` for lean builds |

---

## 🔮 Future Improvements

- [ ] 🗄️ **PostgreSQL / Cloud SQL** — Replace SQLite for multi-instance persistence
- [ ] 🔄 **Redis Caching** — Cache Gemini responses to reduce API calls and latency
- [ ] 📧 **Email Notifications** — Weekly career progress reports
- [ ] 🎯 **Advanced Job Filters** — Salary range, experience level, remote-only
- [ ] 📱 **Progressive Web App** — Offline support and mobile install
- [ ] 🧪 **A/B Testing** — Optimize resume suggestions with user feedback
- [ ] 🌐 **Multi-Language** — i18n support for global users
- [ ] 📊 **Admin Dashboard** — User analytics and system monitoring
- [ ] 🤖 **Chat Interface** — Conversational AI career advisor
- [ ] 📄 **PDF Export** — Download generated resumes as formatted PDFs

---

## 📄 License

This project is licensed under the **MIT License** — see the [LICENSE](LICENSE) file for details.

---

## 👨‍💻 Author

**Sahil Shaik**

- 🌐 GitHub: [@Sahilshk07](https://github.com/Sahilshk07)
- 💼 LinkedIn: [sahilshaik](https://linkedin.com/in/sahilshaik)

---

<p align="center">
  <strong>⭐ If this project helped you, give it a star!</strong><br/>
  <sub>Built with ❤️ by <strong>Sahil Shaik</strong></sub>
</p>
