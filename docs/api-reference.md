# 📡 API Reference — AI Career Copilot

**Base URL:** `http://localhost:5000` (local) or your Cloud Run URL

All API endpoints return JSON. Authenticated endpoints require an active session cookie.

---

## 🔐 Authentication

### `GET /api/user`
Check current authentication status.

**Response:**
```json
{
  "authenticated": true,
  "email": "user@example.com"
}
```

---

### `POST /api/signup`
Create a new user account.

**Request Body:**
```json
{
  "email": "user@example.com",
  "password": "securePassword123"
}
```

**Response (201):**
```json
{
  "message": "Signup successful",
  "email": "user@example.com"
}
```

**Error (400):**
```json
{
  "error": "Email already registered"
}
```

---

### `POST /api/login`
Authenticate an existing user.

**Request Body:**
```json
{
  "email": "user@example.com",
  "password": "securePassword123"
}
```

**Response (200):**
```json
{
  "message": "Login successful",
  "email": "user@example.com"
}
```

---

### `POST /api/logout`
🔒 *Requires authentication*

End the current session.

**Response:**
```json
{
  "message": "Logged out successfully"
}
```

---

## 📄 Resume Processing

### `POST /api/upload_resume`
Upload and analyze a PDF resume.

**Request:** `multipart/form-data`

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `resume` | File (PDF) | ✅ | The resume PDF file |
| `mock_mode` | String | ⬜ | `"true"` to use mock data |

**Response (200):**
```json
{
  "message": "Resume processed successfully",
  "text_preview": "First 500 characters of resume...",
  "full_text": "Complete extracted text...",
  "analysis": {
    "skills": ["Python", "JavaScript", "React"],
    "experience_summary": "Motivated developer...",
    "education": ["B.Tech Computer Science - 2024"],
    "job_roles": ["Full Stack Developer", "Backend Engineer"],
    "missing_skills": ["Kubernetes", "GraphQL"],
    "improvements": ["Add quantifiable metrics..."],
    "ats_score": 72,
    "strengths": ["Strong technical skills..."],
    "weaknesses": ["Lacks leadership examples..."],
    "career_level": "Entry-level",
    "recommended_domains": ["SaaS", "FinTech"]
  },
  "mock_mode": false
}
```

---

## 🎯 Career Analysis

### `POST /api/analyze_career`
Run a comprehensive career analysis against a target role.

**Request Body:**
```json
{
  "resume_text": "Full resume text...",
  "target_role": "Frontend Developer",
  "mock_mode": false
}
```

**Response (200):**
```json
{
  "role_match": {
    "match_percentage": 74,
    "readiness_level": "Needs Upskilling",
    "skill_gap_analysis": [
      {
        "skill": "System Design",
        "gap_level": "High",
        "how_to_bridge": "Study DDIA book..."
      }
    ]
  },
  "roadmap": {
    "roadmap": [
      {
        "week": "Week 1",
        "focus": "Foundation",
        "tasks": ["Read DDIA chapters 1-4..."]
      }
    ],
    "projects_to_build": ["Real-time chat app..."],
    "courses_to_take": ["System Design course..."]
  },
  "linkedin_optimization": {
    "headline_suggestions": ["Aspiring Frontend Developer..."],
    "about_section": "Passionate about building...",
    "skills_to_add": ["System Design", "TypeScript"],
    "post_ideas": ["Share your dev journey..."]
  },
  "jobs": [
    {
      "title": "Frontend Developer",
      "company": "Google",
      "location": "Bangalore, India",
      "match_percentage": 92,
      "apply_link": "https://...",
      "description": "Exciting opportunity...",
      "key_skills": ["React", "JavaScript"]
    }
  ]
}
```

---

## 🧩 Skill Gap Analysis

### `POST /api/skill_gap`
Analyze skill gaps for a specific target role.

**Request Body:**
```json
{
  "target_role": "Data Scientist",
  "current_skills": ["Python", "SQL", "Git"],
  "resume_text": "Optional resume text...",
  "mock_mode": false
}
```

**Response (200):**
```json
{
  "target_role": "Data Scientist",
  "match_percentage": 45,
  "matched_skills": ["Python", "SQL"],
  "missing_skills": ["TensorFlow", "PyTorch", "Statistics"],
  "required_skills": ["Python", "SQL", "TensorFlow", "..."],
  "recommendations": [
    {
      "skill": "TensorFlow",
      "priority": "High",
      "resource": "Learn TensorFlow on Coursera"
    }
  ]
}
```

---

## 🎤 Mock Interview

### `POST /api/interview/questions`
Generate interview questions for a role.

**Request Body:**
```json
{
  "role": "Backend Developer",
  "mock_mode": false
}
```

**Response (200):**
```json
{
  "questions": [
    {
      "id": 1,
      "question": "Explain RESTful API design principles.",
      "category": "Technical",
      "difficulty": "Medium"
    }
  ]
}
```

---

### `POST /api/interview/evaluate`
Evaluate a candidate's answer to an interview question.

**Request Body:**
```json
{
  "question": "Explain RESTful API design principles.",
  "answer": "REST stands for...",
  "role": "Backend Developer",
  "mock_mode": false
}
```

**Response (200):**
```json
{
  "score": 7,
  "feedback": "Good understanding of REST principles...",
  "strengths": ["Shows relevant knowledge"],
  "improvements": ["Add specific examples"],
  "sample_answer": "A comprehensive answer would include..."
}
```

---

## 📊 History & Analytics

### `GET /api/history`
🔒 *Requires authentication*

Get the user's career analysis history.

**Response (200):**
```json
[
  {
    "id": 1,
    "target_role": "Frontend Developer",
    "match_percentage": 74,
    "timestamp": "2026-05-08 15:30:00"
  }
]
```

---

### `GET /api/analytics`
🔒 *Requires authentication*

Get aggregated skill gap analytics.

**Response (200):**
```json
{
  "labels": ["System Design", "Kubernetes", "GraphQL"],
  "data": [5, 3, 2]
}
```

---

## 📝 Resume Generator

### `POST /api/generate_resume`
Generate a professional resume from user details.

**Request Body:**
```json
{
  "full_name": "Sahil Shaik",
  "email": "sahil@example.com",
  "phone": "+91-9876543210",
  "location": "Hyderabad, India",
  "linkedin": "linkedin.com/in/sahilshaik",
  "target_role": "Full Stack Developer",
  "summary": "Passionate developer...",
  "skills": "Python, JavaScript, React, Node.js",
  "experience": "2 years in web development...",
  "education": "B.Tech in CS from XYZ University",
  "certifications": "AWS Certified",
  "projects": "AI Career Copilot, E-commerce Platform",
  "mock_mode": false
}
```

**Response (200):**
```json
{
  "resume": {
    "header": {
      "name": "Sahil Shaik",
      "title": "Full Stack Developer",
      "email": "sahil@example.com",
      "phone": "+91-9876543210",
      "location": "Hyderabad, India",
      "linkedin": "linkedin.com/in/sahilshaik"
    },
    "summary": "Results-driven Full Stack Developer...",
    "skills": ["Python", "JavaScript", "React"],
    "experience": [...],
    "education": [...],
    "certifications": [...],
    "projects": [...]
  }
}
```

---

## Error Responses

All endpoints may return these common error formats:

```json
{
  "error": "Descriptive error message"
}
```

| Status Code | Meaning |
|-------------|---------|
| `400` | Bad Request — missing or invalid parameters |
| `401` | Unauthorized — authentication required |
| `500` | Server Error — usually API failures (with mock fallback) |
