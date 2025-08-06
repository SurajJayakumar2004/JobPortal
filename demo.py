#!/usr/bin/env python3
"""
Demo script for the AI-Powered Job Portal API.

This script demonstrates the key features of the job portal by simulating
a complete workflow for both students and employers.

Run this after starting the FastAPI server with: uvicorn main:app --reload
"""

import requests
import json
import time
from pathlib import Path

BASE_URL = "http://localhost:8000"

def print_response(response, description):
    """Pretty print API response."""
    print(f"\n{'='*50}")
    print(f"📡 {description}")
    print(f"{'='*50}")
    print(f"Status Code: {response.status_code}")
    
    try:
        data = response.json()
        print(f"Response: {json.dumps(data, indent=2)}")
    except:
        print(f"Response: {response.text}")
    
    return response.json() if response.status_code < 400 else None

def demo_student_workflow():
    """Demonstrate student workflow."""
    print("\n🎓 STUDENT WORKFLOW DEMO")
    print("=" * 60)
    
    # 1. Register student account
    student_data = {
        "email": "john.student@example.com",
        "password": "password123",
        "role": "student",
        "profile": {
            "name": "John Student",
            "phone": "+1-555-0123",
            "skills": ["Python", "JavaScript", "React", "SQL"],
            "interests": ["Software Development", "Data Science"],
            "location": "San Francisco, CA",
            "bio": "Passionate computer science student seeking opportunities"
        }
    }
    
    response = requests.post(f"{BASE_URL}/auth/register", json=student_data)
    registration_result = print_response(response, "Student Registration")
    
    if not registration_result:
        print("❌ Student registration failed!")
        return None
    
    # 2. Login and get token
    login_data = {
        "email": "john.student@example.com",
        "password": "password123"
    }
    
    response = requests.post(f"{BASE_URL}/auth/login", json=login_data)
    login_result = print_response(response, "Student Login")
    
    if not login_result or not login_result.get('success'):
        print("❌ Student login failed!")
        return None
    
    student_token = login_result['data']['access_token']
    headers = {"Authorization": f"Bearer {student_token}"}
    
    # 3. Get user info
    response = requests.get(f"{BASE_URL}/auth/me", headers=headers)
    print_response(response, "Get Student Profile")
    
    # 4. Search for jobs
    response = requests.get(f"{BASE_URL}/jobs?skills=Python&limit=5", headers=headers)
    jobs_result = print_response(response, "Search Jobs")
    
    # 5. Generate career counseling report
    response = requests.post(
        f"{BASE_URL}/counseling/generate?target_role=Software Engineer&interests=AI,Machine Learning",
        headers=headers
    )
    counseling_result = print_response(response, "Generate Career Counseling Report")
    
    # 6. Get skill recommendations
    response = requests.get(
        f"{BASE_URL}/counseling/skill-recommendations?target_role=Data Scientist",
        headers=headers
    )
    print_response(response, "Get Skill Recommendations")
    
    # 7. Get available career paths
    response = requests.get(f"{BASE_URL}/counseling/career-paths", headers=headers)
    print_response(response, "Get Career Paths")
    
    return student_token

def demo_employer_workflow():
    """Demonstrate employer workflow."""
    print("\n🏢 EMPLOYER WORKFLOW DEMO")
    print("=" * 60)
    
    # 1. Register employer account
    employer_data = {
        "email": "hr@techcorp.com",
        "password": "password123",
        "role": "employer",
        "profile": {
            "name": "Tech Corp Inc.",
            "phone": "+1-555-0456",
            "skills": [],
            "interests": ["Technology", "Innovation"],
            "location": "San Francisco, CA",
            "bio": "Leading technology company building the future"
        }
    }
    
    response = requests.post(f"{BASE_URL}/auth/register", json=employer_data)
    registration_result = print_response(response, "Employer Registration")
    
    if not registration_result:
        print("❌ Employer registration failed!")
        return None
    
    # 2. Login and get token
    login_data = {
        "email": "hr@techcorp.com",
        "password": "password123"
    }
    
    response = requests.post(f"{BASE_URL}/auth/login", json=login_data)
    login_result = print_response(response, "Employer Login")
    
    if not login_result or not login_result.get('success'):
        print("❌ Employer login failed!")
        return None
    
    employer_token = login_result['data']['access_token']
    headers = {"Authorization": f"Bearer {employer_token}"}
    
    # 3. Create job posting
    job_data = {
        "title": "Senior Python Developer",
        "description": "We are seeking an experienced Python developer to join our growing team. You will work on exciting projects involving AI, machine learning, and web development. The ideal candidate has 3+ years of Python experience, knowledge of Django/FastAPI, and experience with cloud platforms.",
        "required_skills": ["Python", "Django", "FastAPI", "AWS", "PostgreSQL", "Docker"],
        "location": "San Francisco, CA",
        "experience_level": "senior",
        "employment_type": "full-time",
        "salary_range": "$120,000 - $160,000",
        "company_name": "Tech Corp Inc."
    }
    
    response = requests.post(f"{BASE_URL}/jobs", json=job_data, headers=headers)
    job_result = print_response(response, "Create Job Posting")
    
    if not job_result or not job_result.get('success'):
        print("❌ Job posting creation failed!")
        return None
    
    job_id = job_result['data']['job']['id']
    
    # 4. Get job details
    response = requests.get(f"{BASE_URL}/jobs/{job_id}", headers=headers)
    print_response(response, "Get Job Details")
    
    # 5. List all jobs posted by employer
    response = requests.get(f"{BASE_URL}/jobs", headers=headers)
    print_response(response, "List All Jobs")
    
    # 6. Get candidates for the job (this will be empty since no one applied yet)
    response = requests.get(f"{BASE_URL}/jobs/{job_id}/candidates", headers=headers)
    print_response(response, "Get Job Candidates")
    
    return employer_token, job_id

def demo_application_workflow(student_token, job_id):
    """Demonstrate application workflow."""
    print("\n📝 APPLICATION WORKFLOW DEMO")
    print("=" * 60)
    
    student_headers = {"Authorization": f"Bearer {student_token}"}
    
    # Note: In a real scenario, the student would upload a resume first
    # For this demo, we'll simulate that the resume upload step was completed
    
    print("📄 Note: In a real scenario, the student would upload a resume using:")
    print("POST /resumes/upload with multipart/form-data")
    print("For this demo, we'll continue with other endpoints...")
    
    # 1. List applications (should be empty)
    response = requests.get(f"{BASE_URL}/applications", headers=student_headers)
    print_response(response, "List Student Applications")
    
    # 2. Show public job listing
    response = requests.get(f"{BASE_URL}/jobs/{job_id}")
    print_response(response, "View Job as Public User")

def demo_health_and_docs():
    """Demonstrate health check and documentation endpoints."""
    print("\n🔍 SYSTEM ENDPOINTS DEMO")
    print("=" * 60)
    
    # 1. Health check
    response = requests.get(f"{BASE_URL}/health")
    print_response(response, "Health Check")
    
    # 2. Root endpoint
    response = requests.get(f"{BASE_URL}/")
    print_response(response, "Root Endpoint")
    
    print(f"\n📚 API Documentation available at:")
    print(f"   • Interactive docs: {BASE_URL}/docs")
    print(f"   • Alternative docs: {BASE_URL}/redoc")

def main():
    """Run the complete demo."""
    print("🚀 AI-POWERED JOB PORTAL API DEMO")
    print("=" * 60)
    print("This demo shows the key features of the job portal API.")
    print("Make sure the server is running: uvicorn main:app --reload")
    print()
    
    try:
        # Test if server is running
        response = requests.get(f"{BASE_URL}/health", timeout=5)
        if response.status_code != 200:
            print("❌ Server is not responding correctly!")
            return
    except requests.exceptions.RequestException:
        print("❌ Cannot connect to server!")
        print("Please start the server with: uvicorn main:app --reload")
        return
    
    print("✅ Server is running! Starting demo...\n")
    
    # Run demos
    student_token = demo_student_workflow()
    employer_token, job_id = demo_employer_workflow()
    
    if student_token and job_id:
        demo_application_workflow(student_token, job_id)
    
    demo_health_and_docs()
    
    print("\n🎉 DEMO COMPLETED!")
    print("=" * 60)
    print("Key features demonstrated:")
    print("✅ User registration and authentication")
    print("✅ Job posting and management")
    print("✅ Career counseling and skill recommendations")
    print("✅ Job search and filtering")
    print("✅ API documentation endpoints")
    print("\nNext steps:")
    print("• Upload a resume using the /resumes/upload endpoint")
    print("• Apply to jobs using the /applications endpoint") 
    print("• Explore the interactive API docs at /docs")

if __name__ == "__main__":
    main()
