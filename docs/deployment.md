# 🚀 Deployment Guide — AI Career Copilot

This guide covers three deployment methods: **Docker (local)**, **Google Cloud Run (production)**, and **bare-metal** for development.

---

## Prerequisites

| Tool | Version | Purpose |
|------|---------|---------|
| Python | 3.11+ | Backend runtime |
| Docker | 20+ | Container builds |
| gcloud CLI | Latest | GCP deployments |
| Git | 2.x | Version control |

---

## 1. Local Development (No Docker)

```bash
# Clone the repository
git clone https://github.com/your-username/ai-career-copilot.git
cd ai-career-copilot

# Create and activate virtual environment
python -m venv venv
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r backend/requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your API keys

# Run the development server
python backend/app.py
```

The app will be available at **http://localhost:5000**

---

## 2. Docker Deployment

### Build the Image

```bash
# Build the Docker image
docker build -t ai-career-copilot .

# Verify the image
docker images | grep ai-career-copilot
```

### Run Locally with Docker

```bash
# Run with environment variables
docker run -d \
  --name career-copilot \
  -p 8080:8080 \
  -e PORT=8080 \
  -e GEMINI_API_KEY=your_api_key_here \
  -e SECRET_KEY=your_secret_key_here \
  ai-career-copilot

# Check logs
docker logs -f career-copilot

# Stop the container
docker stop career-copilot && docker rm career-copilot
```

The app will be available at **http://localhost:8080**

### Docker Compose (Optional)

Create a `docker-compose.yml`:

```yaml
version: '3.8'
services:
  app:
    build: .
    ports:
      - "8080:8080"
    environment:
      - PORT=8080
      - GEMINI_API_KEY=${GEMINI_API_KEY}
      - SECRET_KEY=${SECRET_KEY}
      - ADZUNA_APP_ID=${ADZUNA_APP_ID}
      - ADZUNA_APP_KEY=${ADZUNA_APP_KEY}
    restart: unless-stopped
```

```bash
# Start with docker compose
docker compose up -d

# View logs
docker compose logs -f

# Stop
docker compose down
```

---

## 3. Google Cloud Run Deployment

### Step 1: Authenticate with GCP

```bash
# Login to Google Cloud
gcloud auth login

# Set your project
gcloud config set project YOUR_PROJECT_ID

# Enable required APIs
gcloud services enable run.googleapis.com
gcloud services enable cloudbuild.googleapis.com
gcloud services enable artifactregistry.googleapis.com
```

### Step 2: Deploy to Cloud Run

```bash
# One-command deployment (builds & deploys automatically)
gcloud run deploy ai-career-copilot \
  --source . \
  --port 8080 \
  --region us-central1 \
  --allow-unauthenticated \
  --memory 512Mi \
  --cpu 1 \
  --min-instances 0 \
  --max-instances 3 \
  --timeout 120
```

### Step 3: Set Environment Variables

```bash
# Set secrets via CLI
gcloud run services update ai-career-copilot \
  --region us-central1 \
  --set-env-vars "GEMINI_API_KEY=your_key_here,SECRET_KEY=your_secret_here"

# Or use Secret Manager (recommended for production)
echo -n "your_api_key" | gcloud secrets create gemini-api-key --data-file=-

gcloud run services update ai-career-copilot \
  --region us-central1 \
  --set-secrets "GEMINI_API_KEY=gemini-api-key:latest"
```

### Step 4: Verify Deployment

```bash
# Get the service URL
gcloud run services describe ai-career-copilot \
  --region us-central1 \
  --format "value(status.url)"

# Check service status
gcloud run services list
```

---

## Environment Variables Reference

| Variable | Required | Description |
|----------|----------|-------------|
| `GEMINI_API_KEY` | ✅ Yes | Google Gemini API key for AI features |
| `SECRET_KEY` | ✅ Yes | Flask session encryption key |
| `PORT` | ⬜ Auto | Server port (auto-set by Cloud Run) |
| `ADZUNA_APP_ID` | ⬜ No | Adzuna job API app ID |
| `ADZUNA_APP_KEY` | ⬜ No | Adzuna job API key |

---

## Production Checklist

- [ ] Set strong `SECRET_KEY` (use `python -c "import secrets; print(secrets.token_hex(32))"`)
- [ ] Configure `GEMINI_API_KEY` as a Cloud Run secret
- [ ] Set appropriate memory/CPU limits based on expected traffic
- [ ] Enable Cloud Run auto-scaling (`--min-instances 0 --max-instances 10`)
- [ ] Set up custom domain (optional)
- [ ] Enable Cloud Monitoring and Logging
- [ ] Configure Cloud Armor for DDoS protection (optional)

---

## Troubleshooting

| Issue | Solution |
|-------|----------|
| `RESOURCE_EXHAUSTED` errors | Gemini API quota exceeded — app auto-falls back to mock data |
| Database not persisting | SQLite uses `/tmp` on Cloud Run (ephemeral) — consider Cloud SQL for persistence |
| Container won't start | Check `PORT` env var is set; Cloud Run injects it automatically |
| Slow cold starts | Set `--min-instances 1` to keep one instance warm |
| CORS errors | Verify `CORS(app, supports_credentials=True)` in app.py |
