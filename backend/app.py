"""
AI Career Copilot — Main Application
======================================
Flask application server that serves the frontend, handles authentication,
and exposes REST API endpoints for AI-powered career analysis features.

Features:
    - Resume upload & AI analysis (ATS scoring, skill extraction)
    - Career matching against target roles
    - Skill gap analysis
    - Mock interview with AI evaluation
    - Career roadmap generation
    - LinkedIn profile optimization
    - Resume generation

Author: Sahil Shaik
License: MIT
"""

import os
import sys
import json
import re
from datetime import datetime
from flask import Flask, request, jsonify, send_from_directory, session
from flask_cors import CORS
from dotenv import load_dotenv
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from collections import Counter

# Add the root directory to sys.path so 'backend' module can be found
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def safe_json_loads(json_str, default=None):
    if default is None:
        default = {}
    try:
        # Strip markdown json block wrappers if present
        clean_str = re.sub(r'```json\n|\n```', '', json_str).strip()
        clean_str = re.sub(r'^```\n|```$', '', clean_str).strip()
        return json.loads(clean_str)
    except Exception as e:
        print(f"JSON Parsing Error: {e} | Raw String: {json_str[:200]}")
        return default

# Load environment variables
load_dotenv()

# Import services
from backend.resume_parser import extract_text_from_pdf
from backend.ai_service import (
    analyze_resume, match_role, generate_roadmap, 
    optimize_linkedin, generate_resume, generate_interview_questions,
    evaluate_interview_answer, analyze_skill_gap
)
from backend.job_service import fetch_jobs

app = Flask(__name__, static_folder='../frontend')
CORS(app, supports_credentials=True)

# Configuration
app.secret_key = os.environ.get("SECRET_KEY", "super-secret-dev-key-change-me")
# Use /tmp for DB on Cloud Run (read-only filesystem except /tmp)
db_path = os.path.join('/tmp', 'career_assistant.db') if os.environ.get('PORT') else os.path.join(os.path.dirname(__file__), '..', 'instance', 'career_assistant.db')
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'

# Initialize extensions
db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)

# --- Database Models ---
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    history = db.relationship('History', backref='user', lazy=True)

class History(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    target_role = db.Column(db.String(150), nullable=False)
    match_percentage = db.Column(db.Integer, nullable=False)
    missing_skills = db.Column(db.Text, nullable=False) # Store JSON string of skills
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

with app.app_context():
    db.create_all()

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# --- File Management ---
# Use /tmp for uploads on Cloud Run
UPLOAD_FOLDER = '/tmp/uploads' if os.environ.get('PORT') else os.path.join(os.path.dirname(os.path.dirname(__file__)), 'uploads')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def cleanup_file(filepath):
    try:
        if os.path.exists(filepath):
            os.remove(filepath)
    except Exception as e:
        print(f"Error cleaning up file {filepath}: {e}")

# --- Mock Data Generators ---
def get_mock_analysis():
    return {
        "skills": ["Python", "JavaScript", "React", "Node.js", "Docker", "AWS", "SQL", "Git"],
        "experience_summary": "Motivated software developer with hands-on experience in full-stack web development, cloud services, and database management.",
        "education": ["B.Tech Computer Science - 2024"],
        "job_roles": ["Full Stack Developer", "Backend Engineer", "DevOps Engineer"],
        "missing_skills": ["Kubernetes", "GraphQL", "System Design", "CI/CD Pipelines"],
        "improvements": [
            "Add quantifiable metrics to achievements (e.g., 'Improved load time by 40%')",
            "Include a compelling professional summary at the top",
            "Use stronger action verbs like 'Architected', 'Spearheaded', 'Optimized'",
            "Add relevant certifications section",
            "Tailor keywords to match target job descriptions"
        ],
        "ats_score": 72,
        "strengths": [
            "Strong technical skill diversity across frontend and backend",
            "Hands-on experience with cloud platforms",
            "Demonstrated project-based learning approach"
        ],
        "weaknesses": [
            "Lacks leadership and team management examples",
            "No measurable impact metrics in experience descriptions",
            "Missing industry certifications"
        ],
        "career_level": "Entry-level",
        "recommended_domains": ["SaaS", "FinTech", "E-Commerce", "EdTech"]
    }

def get_mock_career_data(target_role):
    return {
        "role_match": {
            "match_percentage": 74,
            "readiness_level": "Needs Upskilling",
            "skill_gap_analysis": [
                {"skill": "System Design", "gap_level": "High", "how_to_bridge": "Study 'Designing Data-Intensive Applications' and practice on Excalidraw."},
                {"skill": "Kubernetes", "gap_level": "High", "how_to_bridge": "Complete the Kubernetes crash course on KodeKloud and deploy a microservice."},
                {"skill": "GraphQL", "gap_level": "Medium", "how_to_bridge": "Build a GraphQL API with Apollo Server and integrate it with a React frontend."},
                {"skill": "CI/CD", "gap_level": "Medium", "how_to_bridge": "Set up GitHub Actions pipelines for your existing projects."}
            ]
        },
        "roadmap": {
            "roadmap": [
                {"week": "Week 1", "focus": "Foundation & System Design", "tasks": ["Read chapters 1-4 of DDIA", "Watch system design primer videos", "Practice 2 system design problems on paper"]},
                {"week": "Week 2", "focus": "Cloud & DevOps Mastery", "tasks": ["Complete Kubernetes basics course", "Deploy a 3-service app on minikube", "Set up CI/CD with GitHub Actions"]},
                {"week": "Week 3", "focus": "Advanced Backend & APIs", "tasks": ["Build a GraphQL API from scratch", "Implement caching with Redis", "Practice REST vs GraphQL trade-offs"]},
                {"week": "Week 4", "focus": "Portfolio & Interview Prep", "tasks": ["Polish 2 portfolio projects with README & demos", "Practice 10 behavioral interview questions", "Do 3 mock technical interviews"]}
            ],
            "projects_to_build": [
                "Real-time chat application with WebSockets",
                "URL shortener with analytics dashboard",
                "Microservices-based e-commerce platform"
            ],
            "courses_to_take": [
                "Grokking the System Design Interview - Educative",
                "Kubernetes for Developers - KodeKloud",
                "Advanced React Patterns - Frontend Masters"
            ]
        },
        "linkedin_optimization": {
            "headline_suggestions": [
                f"Aspiring {target_role} | Full-Stack Developer | Building Scalable Web Applications",
                f"{target_role} in the Making | Python • React • AWS | Open to Opportunities"
            ],
            "about_section": f"Passionate about building impactful software solutions. Currently upskilling toward a {target_role} role with a focus on system design, cloud architecture, and modern DevOps practices. I believe in learning by building — every project I ship teaches me something new. Open to connecting with fellow developers and mentors in the tech space.",
            "skills_to_add": ["System Design", "Microservices", "Kubernetes", "GraphQL", "Redis"],
            "post_ideas": [
                "Share your journey from student to developer — what surprised you most?",
                "Write about a bug that took you hours to fix and what you learned",
                f"Document your 30-day challenge to become a {target_role}"
            ]
        }
    }

def get_mock_interview_questions(role):
    questions_db = {
        "default": [
            {"id": 1, "question": f"Tell me about a challenging project you worked on as a {role}.", "category": "Behavioral", "difficulty": "Medium"},
            {"id": 2, "question": f"How do you stay updated with the latest trends in your field?", "category": "Behavioral", "difficulty": "Easy"},
            {"id": 3, "question": "Explain the difference between SQL and NoSQL databases. When would you choose one over the other?", "category": "Technical", "difficulty": "Medium"},
            {"id": 4, "question": "Walk me through your approach to debugging a production issue.", "category": "Technical", "difficulty": "Hard"},
            {"id": 5, "question": "Describe a time when you had to learn a new technology quickly. How did you approach it?", "category": "Behavioral", "difficulty": "Medium"},
            {"id": 6, "question": f"What architectures or design patterns do you think are essential for a {role}?", "category": "Technical", "difficulty": "Hard"},
            {"id": 7, "question": "How do you handle disagreements with team members about technical decisions?", "category": "Behavioral", "difficulty": "Medium"},
            {"id": 8, "question": "Explain RESTful API design principles. What makes a good API?", "category": "Technical", "difficulty": "Medium"}
        ]
    }
    return questions_db.get("default", questions_db["default"])

def get_mock_interview_feedback(question, answer):
    word_count = len(answer.split())
    if word_count < 20:
        score = 4
        feedback = "Your answer is too brief. Try to elaborate with specific examples, metrics, and outcomes."
    elif word_count < 50:
        score = 6
        feedback = "Good start! Add more concrete examples and quantifiable results to strengthen your answer."
    else:
        score = 8
        feedback = "Strong answer with good detail. Consider structuring it using the STAR method (Situation, Task, Action, Result) for even more impact."
    
    return {
        "score": score,
        "feedback": feedback,
        "strengths": ["Shows relevant knowledge", "Addresses the question directly"],
        "improvements": ["Add specific metrics or numbers", "Use the STAR method for behavioral questions", "Connect your answer to the target role"],
        "sample_answer": f"A strong response would include: 1) A specific situation or project context, 2) The technical challenge you faced, 3) The concrete actions you took, 4) Measurable results or outcomes achieved."
    }

def get_mock_skill_gap(target_role, current_skills):
    all_role_skills = {
        "default": ["Python", "JavaScript", "React", "Node.js", "SQL", "Git", "Docker", "AWS", "System Design", "CI/CD", "Kubernetes", "TypeScript", "GraphQL", "Redis", "MongoDB"]
    }
    
    required = all_role_skills.get("default")
    current_lower = [s.lower().strip() for s in current_skills]
    
    matched = [s for s in required if s.lower() in current_lower]
    missing = [s for s in required if s.lower() not in current_lower]
    
    match_pct = int((len(matched) / len(required)) * 100) if required else 0
    
    return {
        "target_role": target_role,
        "match_percentage": match_pct,
        "matched_skills": matched,
        "missing_skills": missing,
        "required_skills": required,
        "recommendations": [
            {"skill": s, "priority": "High" if i < 3 else "Medium", "resource": f"Learn {s} on Udemy, Coursera, or official docs"} 
            for i, s in enumerate(missing[:6])
        ]
    }


# --- Frontend Serving ---
@app.route('/')
def serve_index():
    return send_from_directory(app.static_folder, 'index.html')

@app.route('/<path:path>')
def serve_static(path):
    if os.path.exists(os.path.join(app.static_folder, path)):
        return send_from_directory(app.static_folder, path)
    return serve_index()

# --- Auth Endpoints ---
@app.route('/api/user', methods=['GET'])
def get_user():
    if current_user.is_authenticated:
        return jsonify({"authenticated": True, "email": current_user.email})
    return jsonify({"authenticated": False})

@app.route('/api/signup', methods=['POST'])
def signup():
    data = request.json
    email = data.get('email')
    password = data.get('password')
    
    if User.query.filter_by(email=email).first():
        return jsonify({"error": "Email already registered"}), 400
        
    new_user = User(
        email=email,
        password_hash=generate_password_hash(password, method='pbkdf2:sha256')
    )
    db.session.add(new_user)
    db.session.commit()
    login_user(new_user)
    return jsonify({"message": "Signup successful", "email": email})

@app.route('/api/login', methods=['POST'])
def login():
    data = request.json
    email = data.get('email')
    password = data.get('password')
    
    user = User.query.filter_by(email=email).first()
    if not user or not check_password_hash(user.password_hash, password):
        return jsonify({"error": "Invalid email or password"}), 401
        
    login_user(user)
    return jsonify({"message": "Login successful", "email": email})

@app.route('/api/logout', methods=['POST'])
@login_required
def logout():
    logout_user()
    return jsonify({"message": "Logged out successfully"})

# --- App Endpoints ---
@app.route('/api/upload_resume', methods=['POST'])
def upload_resume():
    if 'resume' not in request.files:
        return jsonify({"error": "No resume file provided"}), 400
        
    file = request.files['resume']
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400
        
    if not file.filename.lower().endswith('.pdf'):
        return jsonify({"error": "Only PDF files are supported"}), 400

    # Check for mock mode
    mock_mode = request.form.get('mock_mode', 'false').lower() == 'true'

    filepath = os.path.join(UPLOAD_FOLDER, file.filename)
    try:
        file.save(filepath)
        resume_text = extract_text_from_pdf(filepath)
        
        if mock_mode:
            analysis_data = get_mock_analysis()
        else:
            analysis_json_str = analyze_resume(resume_text)
            analysis_data = safe_json_loads(analysis_json_str)
        
        return jsonify({
            "message": "Resume processed successfully",
            "text_preview": resume_text[:500] + "...", 
            "full_text": resume_text,
            "analysis": analysis_data,
            "mock_mode": mock_mode
        })
    except Exception as e:
        error_msg = str(e)
        print(f"Error processing resume: {error_msg}")
        if "429" in error_msg or "RESOURCE_EXHAUSTED" in error_msg:
            return jsonify({
                "message": "Using mock data (API Limit Reached)",
                "text_preview": "MOCK TEXT PREVIEW...",
                "full_text": "",
                "analysis": get_mock_analysis(),
                "mock_mode": True
            })
        return jsonify({"error": error_msg}), 500
    finally:
        cleanup_file(filepath)

@app.route('/api/analyze_career', methods=['POST'])
def analyze_career():
    data = request.json
    resume_text = data.get('resume_text')
    target_role = data.get('target_role')
    mock_mode = data.get('mock_mode', False)
    
    if not resume_text or not target_role:
        return jsonify({"error": "Both resume_text and target_role are required"}), 400
    
    if mock_mode:
        mock_data = get_mock_career_data(target_role)
        skills = get_mock_analysis()['skills']
        jobs = fetch_jobs(skills, target_role)
        mock_data["jobs"] = jobs
        return jsonify(mock_data)
        
    try:
        import concurrent.futures
        
        with concurrent.futures.ThreadPoolExecutor() as executor:
            future_match = executor.submit(match_role, resume_text, target_role)
            future_roadmap = executor.submit(generate_roadmap, resume_text, target_role)
            future_linkedin = executor.submit(optimize_linkedin, resume_text)
            future_analysis = executor.submit(analyze_resume, resume_text)
            
            role_match_str = future_match.result()
            roadmap_str = future_roadmap.result()
            linkedin_str = future_linkedin.result()
            analysis_str = future_analysis.result()
        
        role_match = safe_json_loads(role_match_str)
        roadmap = safe_json_loads(roadmap_str)
        linkedin = safe_json_loads(linkedin_str)
        
        analysis = safe_json_loads(analysis_str)
        skills = analysis.get('skills', [])
        
        if current_user.is_authenticated:
            missing_skills = [gap['skill'] for gap in role_match.get('skill_gap_analysis', [])]
            new_history = History(
                user_id=current_user.id,
                target_role=target_role,
                match_percentage=role_match.get('match_percentage', 0),
                missing_skills=json.dumps(missing_skills)
            )
            db.session.add(new_history)
            db.session.commit()
        
        jobs = fetch_jobs(skills, target_role)
        
        return jsonify({
            "role_match": role_match,
            "roadmap": roadmap,
            "linkedin_optimization": linkedin,
            "jobs": jobs
        })
    except Exception as e:
        error_msg = str(e)
        print(f"Error in career analysis: {error_msg}")
        
        if "429" in error_msg or "RESOURCE_EXHAUSTED" in error_msg:
            mock_data = get_mock_career_data(target_role)
            jobs = fetch_jobs(["Python", "React"], target_role)
            mock_data["jobs"] = jobs
            
            if current_user.is_authenticated:
                new_history = History(
                    user_id=current_user.id,
                    target_role=target_role,
                    match_percentage=mock_data['role_match']['match_percentage'],
                    missing_skills=json.dumps(["System Design"])
                )
                db.session.add(new_history)
                db.session.commit()
                
            return jsonify(mock_data)
            
        return jsonify({"error": error_msg}), 500

# --- Mock Interview Endpoints ---
@app.route('/api/interview/questions', methods=['POST'])
def get_interview_questions():
    data = request.json
    role = data.get('role', 'Software Developer')
    mock_mode = data.get('mock_mode', False)
    
    if mock_mode:
        return jsonify({"questions": get_mock_interview_questions(role)})
    
    try:
        questions_str = generate_interview_questions(role)
        questions_data = safe_json_loads(questions_str, default={"questions": []})
        return jsonify(questions_data)
    except Exception as e:
        error_msg = str(e)
        print(f"Error generating interview questions: {error_msg}")
        return jsonify({"questions": get_mock_interview_questions(role)})

@app.route('/api/interview/evaluate', methods=['POST'])
def evaluate_answer():
    data = request.json
    question = data.get('question', '')
    answer = data.get('answer', '')
    role = data.get('role', 'Software Developer')
    mock_mode = data.get('mock_mode', False)
    
    if not answer.strip():
        return jsonify({"error": "Please provide an answer"}), 400
    
    if mock_mode:
        return jsonify(get_mock_interview_feedback(question, answer))
    
    try:
        feedback_str = evaluate_interview_answer(question, answer, role)
        feedback_data = safe_json_loads(feedback_str)
        return jsonify(feedback_data)
    except Exception as e:
        error_msg = str(e)
        print(f"Error evaluating answer: {error_msg}")
        return jsonify(get_mock_interview_feedback(question, answer))

# --- Skill Gap Analyzer Endpoint ---
@app.route('/api/skill_gap', methods=['POST'])
def skill_gap():
    data = request.json
    target_role = data.get('target_role', '')
    current_skills = data.get('current_skills', [])
    resume_text = data.get('resume_text', '')
    mock_mode = data.get('mock_mode', False)
    
    if not target_role:
        return jsonify({"error": "Target role is required"}), 400
    
    if mock_mode:
        return jsonify(get_mock_skill_gap(target_role, current_skills))
    
    try:
        gap_str = analyze_skill_gap(resume_text, target_role, current_skills)
        gap_data = safe_json_loads(gap_str)
        return jsonify(gap_data)
    except Exception as e:
        error_msg = str(e)
        print(f"Error analyzing skill gap: {error_msg}")
        return jsonify(get_mock_skill_gap(target_role, current_skills))

# --- History & Analytics ---
@app.route('/api/history', methods=['GET'])
@login_required
def get_history():
    histories = History.query.filter_by(user_id=current_user.id).order_by(History.timestamp.desc()).all()
    results = []
    for h in histories:
        results.append({
            "id": h.id,
            "target_role": h.target_role,
            "match_percentage": h.match_percentage,
            "timestamp": h.timestamp.strftime("%Y-%m-%d %H:%M:%S")
        })
    return jsonify(results)

@app.route('/api/analytics', methods=['GET'])
@login_required
def get_analytics():
    histories = History.query.filter_by(user_id=current_user.id).all()
    all_missing_skills = []
    
    for h in histories:
        try:
            skills = json.loads(h.missing_skills)
            all_missing_skills.extend(skills)
        except:
            pass
            
    if not all_missing_skills:
        return jsonify({"labels": [], "data": []})
        
    counter = Counter(all_missing_skills)
    top_skills = counter.most_common(5)
    
    labels = [item[0] for item in top_skills]
    data = [item[1] for item in top_skills]
    
    return jsonify({"labels": labels, "data": data})

@app.route('/api/generate_resume', methods=['POST'])
def generate_resume_endpoint():
    data = request.json
    if not data:
        return jsonify({"error": "No data provided"}), 400
    
    mock_mode = data.get('mock_mode', False)
    
    if mock_mode:
        mock_resume = {
            "header": {
                "name": data.get("full_name", "John Doe"),
                "title": data.get("target_role", "Software Developer"),
                "email": data.get("email", "john@example.com"),
                "phone": data.get("phone", "+1-555-0123"),
                "location": data.get("location", "San Francisco, CA"),
                "linkedin": data.get("linkedin", "linkedin.com/in/johndoe")
            },
            "summary": f"Results-driven {data.get('target_role', 'professional')} with expertise in {data.get('skills', 'technology')}. Passionate about delivering high-quality solutions and driving measurable impact across cross-functional teams.",
            "skills": [s.strip() for s in data.get("skills", "Python,JavaScript").split(",")][:10],
            "experience": [{"title": data.get("target_role", "Developer"), "company": "Tech Company", "duration": "2022 - Present", "bullets": ["Led development of key features improving user engagement by 35%", "Collaborated with cross-functional teams to deliver projects on time", "Implemented CI/CD pipelines reducing deployment time by 60%"]}],
            "education": [{"degree": "Bachelor of Science in Computer Science", "institution": "University", "year": "2024"}],
            "certifications": ["AWS Certified Solutions Architect"],
            "projects": [{"name": "Portfolio Project", "description": "Built a full-stack application with modern architecture", "tech_stack": ["React", "Node.js", "PostgreSQL"]}]
        }
        return jsonify({"resume": mock_resume})
    
    try:
        resume_json_str = generate_resume(data)
        resume_data = safe_json_loads(resume_json_str)
        return jsonify({"resume": resume_data})
    except Exception as e:
        error_msg = str(e)
        print(f"Error generating resume: {error_msg}")
        if "429" in error_msg or "RESOURCE_EXHAUSTED" in error_msg:
            mock_resume = {
                "header": {
                    "name": data.get("full_name", "John Doe"),
                    "title": data.get("target_role", "Software Developer"),
                    "email": data.get("email", "john@example.com"),
                    "phone": data.get("phone", "+1-555-0123"),
                    "location": data.get("location", "San Francisco, CA"),
                    "linkedin": data.get("linkedin", "linkedin.com/in/johndoe")
                },
                "summary": f"Results-driven {data.get('target_role', 'professional')} with expertise in {data.get('skills', 'technology')}.",
                "skills": [s.strip() for s in data.get("skills", "Python,JavaScript").split(",")][:10],
                "experience": [{"title": data.get("target_role", "Developer"), "company": "Tech Company", "duration": "2022 - Present", "bullets": ["Led development of key features", "Collaborated with cross-functional teams"]}],
                "education": [{"degree": "B.S. Computer Science", "institution": "University", "year": "2024"}],
                "certifications": ["AWS Certified Solutions Architect"],
                "projects": [{"name": "Portfolio Project", "description": "Built a full-stack application", "tech_stack": ["React", "Node.js"]}]
            }
            return jsonify({"resume": mock_resume})
        return jsonify({"error": error_msg}), 500

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    is_production = os.environ.get('PORT') is not None
    app.run(host='0.0.0.0', port=port, debug=not is_production)
