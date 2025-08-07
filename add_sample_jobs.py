#!/usr/bin/env python3
"""
Script to add sample job data to the running backend server.
This helps test the frontend functionality.
"""

import requests
import json
from datetime import datetime

# Backend API base URL
BASE_URL = "http://localhost:8001"

# Sample job data
sample_jobs = [
    {
        "title": "Senior Software Engineer",
        "description": "We are looking for a Senior Software Engineer to join our innovative team. You will be responsible for designing, developing, and maintaining scalable web applications using modern technologies. The ideal candidate has strong experience with React, Node.js, and cloud platforms.",
        "required_skills": ["Python", "React", "Node.js", "AWS", "PostgreSQL"],
        "location": "San Francisco, CA",
        "experience_level": "senior",
        "employment_type": "full-time",
        "salary_range": "$120,000 - $160,000",
        "company_name": "TechCorp Solutions"
    },
    {
        "title": "Frontend Developer",
        "description": "Join our dynamic frontend team to build beautiful, responsive user interfaces. You'll work with the latest React technologies, implement pixel-perfect designs, and ensure excellent user experience across all devices.",
        "required_skills": ["JavaScript", "React", "CSS3", "HTML5", "TypeScript"],
        "location": "New York, NY",
        "experience_level": "mid",
        "employment_type": "full-time",
        "salary_range": "$80,000 - $110,000",
        "company_name": "Design Studio Inc"
    },
    {
        "title": "Data Scientist Intern",
        "description": "Excellent opportunity for students to gain hands-on experience in data science. You'll work on real projects involving machine learning, data analysis, and visualization using Python and modern ML frameworks.",
        "required_skills": ["Python", "Pandas", "Scikit-learn", "Jupyter", "SQL"],
        "location": "Austin, TX",
        "experience_level": "entry",
        "employment_type": "internship",
        "salary_range": "$20/hour",
        "company_name": "DataTech Analytics"
    },
    {
        "title": "DevOps Engineer",
        "description": "We need a DevOps Engineer to help streamline our deployment processes and maintain our cloud infrastructure. Experience with Docker, Kubernetes, and CI/CD pipelines is essential.",
        "required_skills": ["Docker", "Kubernetes", "AWS", "Jenkins", "Linux"],
        "location": "Seattle, WA",
        "experience_level": "mid",
        "employment_type": "full-time",
        "salary_range": "$95,000 - $130,000",
        "company_name": "CloudOps Solutions"
    },
    {
        "title": "Full Stack Developer",
        "description": "Looking for a versatile Full Stack Developer who can work on both frontend and backend. You'll be building features end-to-end using modern web technologies and frameworks.",
        "required_skills": ["JavaScript", "React", "Node.js", "MongoDB", "Express"],
        "location": "Remote",
        "experience_level": "mid",
        "employment_type": "full-time",
        "salary_range": "$85,000 - $115,000",
        "company_name": "RemoteFirst Tech"
    }
]

def create_sample_employer():
    """Create a sample employer account to post jobs."""
    employer_data = {
        "full_name": "John Doe",
        "organization_name": "Sample Tech Company",
        "organization_email": "john@sampletech.com",
        "phone_number": "+1-555-0123",
        "password": "password123"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/auth/register/employer", json=employer_data)
        if response.status_code == 201:
            print("✓ Sample employer created successfully")
            return employer_data["organization_email"]
        else:
            print(f"⚠ Employer creation failed: {response.text}")
            return None
    except Exception as e:
        print(f"⚠ Error creating employer: {e}")
        return None

def login_employer(email):
    """Login as the sample employer to get auth token."""
    login_data = {
        "email": email,
        "password": "password123"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/auth/login", json=login_data)
        if response.status_code == 200:
            data = response.json()
            token = data.get("access_token")
            print("✓ Employer login successful")
            return token
        else:
            print(f"⚠ Login failed: {response.text}")
            return None
    except Exception as e:
        print(f"⚠ Error logging in: {e}")
        return None

def create_job(job_data, token):
    """Create a job posting using the auth token."""
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/jobs/", json=job_data, headers=headers)
        if response.status_code == 201:
            return True
        else:
            print(f"⚠ Job creation failed: {response.text}")
            return False
    except Exception as e:
        print(f"⚠ Error creating job: {e}")
        return False

def main():
    print("🚀 Adding sample jobs to the AI Job Portal backend...")
    
    # Check if backend is running
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=5)
        if response.status_code != 200:
            print("❌ Backend is not responding. Please make sure it's running on localhost:8001")
            return
    except requests.exceptions.RequestException:
        print("❌ Cannot connect to backend. Please make sure it's running on localhost:8001")
        return
    
    print("✓ Backend is running")
    
    # Try to create employer, or login if already exists
    employer_email = create_sample_employer()
    if not employer_email:
        # Employer might already exist, try to login with existing email
        employer_email = "john@sampletech.com"
        print("ℹ️ Using existing employer account")
    
    token = login_employer(employer_email)
    if not token:
        print("❌ Failed to login as employer")
        return
    
    # Create sample jobs
    created_count = 0
    for i, job in enumerate(sample_jobs, 1):
        print(f"Creating job {i}/{len(sample_jobs)}: {job['title']}")
        if create_job(job, token):
            created_count += 1
            print(f"✓ Created: {job['title']}")
        else:
            print(f"❌ Failed to create: {job['title']}")
    
    print(f"\n🎉 Successfully created {created_count}/{len(sample_jobs)} sample jobs!")
    print("You can now test the frontend at http://localhost:3000")

if __name__ == "__main__":
    main()
