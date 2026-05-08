"""
AI Career Copilot — AI Service Module
=======================================
Handles all interactions with the Google Gemini 2.5 Flash model.
Each function crafts a structured prompt and returns JSON-formatted
AI-generated career intelligence.

Capabilities:
    - Resume analysis with ATS scoring
    - Role matching with skill gap identification
    - 30-day career roadmap generation
    - LinkedIn profile optimization
    - Interview question generation & answer evaluation
    - Skill gap analysis with learning recommendations
    - Professional resume generation

Author: Sahil Shaik
License: MIT
"""

import os
from google import genai
from google.genai import types
from pydantic import BaseModel, Field
from typing import List, Optional
from dotenv import load_dotenv

load_dotenv() # Ensure env vars are loaded

# Initialize the Gemini client explicitly using the environment variable
api_key = os.environ.get("GEMINI_API_KEY")
client = genai.Client(api_key=api_key)

# Define Pydantic Models for Structured Output
class ResumeAnalysis(BaseModel):
    skills: List[str] = Field(description="List of skills extracted from the resume")
    experience_summary: str = Field(description="A brief summary of the user's experience")
    education: List[str] = Field(description="List of educational qualifications")
    job_roles: List[str] = Field(description="Suggested job roles based on the resume")
    missing_skills: List[str] = Field(description="Common skills missing for the suggested job roles")
    improvements: List[str] = Field(description="Actionable tips to improve the resume formatting and content")
    ats_score: int = Field(description="Estimated ATS score out of 100 based on keyword density, formatting, and impact")
    strengths: List[str] = Field(description="Key strengths identified in the resume")
    weaknesses: List[str] = Field(description="Areas of weakness or lack of experience")
    career_level: str = Field(description="Estimated career level (e.g., Entry-level, Mid-level, Senior)")
    recommended_domains: List[str] = Field(description="Recommended industry domains based on experience")

class SkillGap(BaseModel):
    skill: str
    gap_level: str = Field(description="High, Medium, or Low")
    how_to_bridge: str

class RoleMatching(BaseModel):
    match_percentage: int
    readiness_level: str = Field(description="e.g., Needs Upskilling, Ready, Overqualified")
    skill_gap_analysis: List[SkillGap]

class RoadmapItem(BaseModel):
    week: str
    focus: str
    tasks: List[str]

class CareerRoadmap(BaseModel):
    roadmap: List[RoadmapItem]
    projects_to_build: List[str]
    courses_to_take: List[str]

class LinkedInOptimization(BaseModel):
    headline_suggestions: List[str]
    about_section: str
    skills_to_add: List[str]
    post_ideas: List[str]

def analyze_resume(resume_text: str) -> str:
    prompt = f"""
    You are an expert HR professional and technical recruiter. 
    Analyze the following resume text and extract the required information.
    Provide a critical, realistic ATS score based on best practices.
    
    Output strictly in this JSON format:
    {{
        "skills": ["string"],
        "experience_summary": "string",
        "education": ["string"],
        "job_roles": ["string"],
        "missing_skills": ["string"],
        "improvements": ["string"],
        "ats_score": 0,
        "strengths": ["string"],
        "weaknesses": ["string"],
        "career_level": "string",
        "recommended_domains": ["string"]
    }}
    
    Resume Text:
    {resume_text}
    """
    
    response = client.models.generate_content(
        model='gemini-2.5-flash',
        contents=prompt,
        config=types.GenerateContentConfig(
            response_mime_type="application/json",
        ),
    )
    return response.text

def match_role(resume_text: str, target_role: str) -> str:
    prompt = f"""
    You are an expert career coach. Compare the provided resume against the target role: '{target_role}'.
    Calculate a realistic match percentage and identify skill gaps.
    
    Output strictly in this JSON format:
    {{
        "match_percentage": 0,
        "readiness_level": "Needs Upskilling, Ready, or Overqualified",
        "skill_gap_analysis": [
            {{
                "skill": "string",
                "gap_level": "High, Medium, or Low",
                "how_to_bridge": "string"
            }}
        ]
    }}
    
    Resume Text:
    {resume_text}
    """
    response = client.models.generate_content(
        model='gemini-2.5-flash',
        contents=prompt,
        config=types.GenerateContentConfig(
            response_mime_type="application/json",
        ),
    )
    return response.text

def generate_roadmap(resume_text: str, target_role: str) -> str:
    prompt = f"""
    You are a technical career advisor. Based on the user's resume and their target role '{target_role}',
    create a highly specific, actionable 30-day (4 weeks) career roadmap to help them transition or upskill.
    Include specific project ideas and course topics.
    
    Output strictly in this JSON format:
    {{
        "roadmap": [
            {{
                "week": "Week 1",
                "focus": "string",
                "tasks": ["string"]
            }}
        ],
        "projects_to_build": ["string"],
        "courses_to_take": ["string"]
    }}
    
    Resume Text:
    {resume_text}
    """
    response = client.models.generate_content(
        model='gemini-2.5-flash',
        contents=prompt,
        config=types.GenerateContentConfig(
            response_mime_type="application/json",
        ),
    )
    return response.text

def optimize_linkedin(resume_text: str) -> str:
    prompt = f"""
    You are an expert personal branding coach. Based on this resume, suggest optimizations for the user's LinkedIn profile.
    Provide compelling headlines, a well-written 'About' section, missing skills to add, and ideas for engaging posts.
    
    Output strictly in this JSON format:
    {{
        "headline_suggestions": ["string"],
        "about_section": "string",
        "skills_to_add": ["string"],
        "post_ideas": ["string"]
    }}
    
    Resume Text:
    {resume_text}
    """
    response = client.models.generate_content(
        model='gemini-2.5-flash',
        contents=prompt,
        config=types.GenerateContentConfig(
            response_mime_type="application/json",
        ),
    )
    return response.text

def generate_resume(user_data: dict) -> str:
    prompt = f"""
    You are an expert resume writer and career coach. Generate a professional, ATS-optimized resume based on the following user details.
    Make it compelling with strong action verbs and quantified achievements where possible.
    
    User Details:
    - Full Name: {user_data.get('full_name', 'N/A')}
    - Email: {user_data.get('email', 'N/A')}
    - Phone: {user_data.get('phone', 'N/A')}
    - Location: {user_data.get('location', 'N/A')}
    - LinkedIn: {user_data.get('linkedin', 'N/A')}
    - Target Role: {user_data.get('target_role', 'N/A')}
    - Professional Summary (brief): {user_data.get('summary', 'N/A')}
    - Skills: {user_data.get('skills', 'N/A')}
    - Work Experience: {user_data.get('experience', 'N/A')}
    - Education: {user_data.get('education', 'N/A')}
    - Certifications: {user_data.get('certifications', 'N/A')}
    - Projects: {user_data.get('projects', 'N/A')}
    
    Output strictly in this JSON format:
    {{
        "header": {{
            "name": "string",
            "title": "string",
            "email": "string",
            "phone": "string",
            "location": "string",
            "linkedin": "string"
        }},
        "summary": "A compelling 2-3 sentence professional summary",
        "skills": ["string"],
        "experience": [
            {{
                "title": "string",
                "company": "string",
                "duration": "string",
                "bullets": ["string - use strong action verbs and metrics"]
            }}
        ],
        "education": [
            {{
                "degree": "string",
                "institution": "string",
                "year": "string"
            }}
        ],
        "certifications": ["string"],
        "projects": [
            {{
                "name": "string",
                "description": "string",
                "tech_stack": ["string"]
            }}
        ]
    }}
    """
    response = client.models.generate_content(
        model='gemini-2.5-flash',
        contents=prompt,
        config=types.GenerateContentConfig(
            response_mime_type="application/json",
        ),
    )
    return response.text

def generate_interview_questions(role: str) -> str:
    prompt = f"""
    You are an expert technical interviewer and HR professional. Generate 8 interview questions 
    for the role of '{role}'. Include a mix of behavioral and technical questions with varying difficulty.
    
    Output strictly in this JSON format:
    {{
        "questions": [
            {{
                "id": 1,
                "question": "string",
                "category": "Technical or Behavioral",
                "difficulty": "Easy, Medium, or Hard"
            }}
        ]
    }}
    """
    response = client.models.generate_content(
        model='gemini-2.5-flash',
        contents=prompt,
        config=types.GenerateContentConfig(
            response_mime_type="application/json",
        ),
    )
    return response.text

def evaluate_interview_answer(question: str, answer: str, role: str) -> str:
    prompt = f"""
    You are an expert interview coach evaluating a candidate's response for a '{role}' position.
    
    Question: {question}
    Candidate's Answer: {answer}
    
    Evaluate the answer and provide constructive feedback.
    
    Output strictly in this JSON format:
    {{
        "score": 0,
        "feedback": "Overall assessment string",
        "strengths": ["string"],
        "improvements": ["string"],
        "sample_answer": "A brief model answer outline"
    }}
    
    Score should be 1-10 where:
    1-3: Poor, 4-5: Below Average, 6-7: Good, 8-9: Excellent, 10: Outstanding
    """
    response = client.models.generate_content(
        model='gemini-2.5-flash',
        contents=prompt,
        config=types.GenerateContentConfig(
            response_mime_type="application/json",
        ),
    )
    return response.text

def analyze_skill_gap(resume_text: str, target_role: str, current_skills: list) -> str:
    skills_str = ", ".join(current_skills) if current_skills else "Not specified"
    prompt = f"""
    You are a career advisor. Analyze the skill gap between the candidate's current skills and the requirements 
    for the target role '{target_role}'.
    
    Current Skills: {skills_str}
    Resume Context: {resume_text[:1000] if resume_text else 'Not provided'}
    
    Output strictly in this JSON format:
    {{
        "target_role": "{target_role}",
        "match_percentage": 0,
        "matched_skills": ["string"],
        "missing_skills": ["string"],
        "required_skills": ["string"],
        "recommendations": [
            {{
                "skill": "string",
                "priority": "High, Medium, or Low",
                "resource": "string"
            }}
        ]
    }}
    """
    response = client.models.generate_content(
        model='gemini-2.5-flash',
        contents=prompt,
        config=types.GenerateContentConfig(
            response_mime_type="application/json",
        ),
    )
    return response.text
