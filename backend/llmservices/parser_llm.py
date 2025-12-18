import os
import json
import re
from dotenv import load_dotenv
from groq import Groq

load_dotenv()
client = Groq(api_key=os.getenv("GROQ_API_KEY"))


def clean_and_validate_data(parsed: dict) -> dict:
    """Clean and validate extracted resume data"""
    
    # Clean name - remove titles, extra spaces
    name = parsed.get("name", "").strip()
    name = re.sub(r'\b(Mr\.|Mrs\.|Ms\.|Dr\.|Prof\.)\s*', '', name, flags=re.IGNORECASE)
    name = re.sub(r'\s+', ' ', name)  # Remove multiple spaces
    
    # Clean email
    email = parsed.get("email", "")
    if email:
        email = email.lower().strip()
        # Validate email format
        if not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', email):
            email = None
    else:
        email = None
    
    # Clean phone number
    contact = parsed.get("contact", "").strip()
    if contact:
        # Extract only digits and common separators
        contact = re.sub(r'[^\d\s\-\+\(\)]+', '', contact)
        contact = re.sub(r'\s+', ' ', contact).strip()
    
    # Clean skills - remove duplicates, normalize
    skills = parsed.get("skills", [])
    if skills:
        skills = [s.strip() for s in skills if s.strip()]
        skills = list(dict.fromkeys(skills))  # Remove duplicates while preserving order
        # Normalize common abbreviations
        normalized_skills = []
        skill_mappings = {
            'js': 'JavaScript', 'ts': 'TypeScript', 'py': 'Python',
            'ml': 'Machine Learning', 'ai': 'Artificial Intelligence',
            'dl': 'Deep Learning', 'nlp': 'Natural Language Processing',
            'css3': 'CSS', 'html5': 'HTML', 'reactjs': 'React',
            'nodejs': 'Node.js', 'nextjs': 'Next.js'
        }
        for skill in skills:
            normalized = skill_mappings.get(skill.lower(), skill)
            normalized_skills.append(normalized)
        skills = list(dict.fromkeys(normalized_skills))
    
    # Clean experience string
    experience = parsed.get("experience", "").strip()
    if experience:
        # Standardize format
        experience = re.sub(r'\s+', ' ', experience)
    
    return {
        "name": name or "Unknown",
        "email": email,
        "contact": contact or "",
        "location": parsed.get("location", "").strip(),
        "designation": parsed.get("designation", "").strip(),
        "experience": experience,
        "education": parsed.get("education", "").strip(),
        "skills": skills,
        "certifications": [c.strip() for c in parsed.get("certifications", []) if c.strip()],
        "projects": [p.strip() for p in parsed.get("projects", []) if p.strip()],
        "key_achievements": [a.strip() for a in parsed.get("key_achievements", []) if a.strip()],
        "professional_summary": parsed.get("professional_summary", "").strip()
    }


def parse_resume(resume_text: str) -> dict:
    """
    Extract structured information from resume text
    Returns candidate data in standardized format
    """
    
    response_schema = {
        "type": "object",
        "properties": {
            "name": {"type": "string"},
            "email": {"type": "string"},
            "contact": {"type": "string"},
            "location": {"type": "string"},
            "designation": {"type": "string"},
            "experience": {"type": "string"},
            "education": {"type": "string"},
            "skills": {"type": "array", "items": {"type": "string"}},
            "certifications": {"type": "array", "items": {"type": "string"}},
            "projects": {"type": "array", "items": {"type": "string"}},
            "key_achievements": {"type": "array", "items": {"type": "string"}},
            "professional_summary": {"type": "string"}
        },
        "required": ["name", "email", "skills"]
    }

    prompt = f"""
Extract structured information from this resume. Be thorough and accurate. This may be a student or entry-level resume.

Resume Text:
{resume_text}

CRITICAL INSTRUCTIONS:

1. **NAME EXTRACTION:**
   - Look for the name at the top of the resume
   - Remove titles like Mr., Mrs., Ms., Dr.
   - Full name only, no designations or degrees

2. **CONTACT INFORMATION:**
   - Email: Extract valid email address (must contain @)
   - Phone: Extract phone number (include country code if present)
   - Location: City, State/Country

3. **DESIGNATION/TITLE:**
   - For students: Extract degree pursuing (e.g., "B.Tech Computer Science Student")
   - For professionals: Current or most recent job title
   - For freshers: "Fresh Graduate" or degree completed

4. **EXPERIENCE:**
   - For students: Include internships, projects, volunteer work
   - Format: "X years Y months" or "Fresher" or "X month internship"
   - Calculate total duration from all work experience

5. **EDUCATION:**
   - Extract ALL degrees with institution names and years
   - Format: "Degree, Institution, Year (GPA/Percentage if available)"
   - Include ongoing education
   - Example: "B.Tech in Computer Science, MIT, 2024 (CGPA: 8.5/10)"

6. **SKILLS - VERY IMPORTANT:**
   - Extract ALL technical skills mentioned
   - Include: Programming languages, frameworks, tools, technologies
   - Separate by commas in the text
   - Normalize abbreviations: JS→JavaScript, ML→Machine Learning, etc.
   - Include soft skills if mentioned
   - Look in: Skills section, project descriptions, coursework

7. **CERTIFICATIONS:**
   - Extract all certifications with issuing organization
   - Format: "Certificate Name, Issuing Organization, Year"
   - Include online courses (Coursera, Udemy, etc.)

8. **PROJECTS:**
   - Extract ALL projects with brief descriptions
   - Format: "Project Name: Brief description of what it does"
   - Include technologies used if mentioned
   - Include academic projects, personal projects, hackathons

9. **KEY ACHIEVEMENTS:**
   - Quantifiable accomplishments (numbers, percentages)
   - Awards, honors, scholarships
   - Publications, patents
   - Competition wins, hackathon prizes
   - Leadership roles

10. **PROFESSIONAL SUMMARY:**
    - Create a 2-3 sentence overview
    - Highlight: education level, key skills, experience type
    - Example: "Final year Computer Science student with expertise in Machine Learning and Python. Completed 2 internships and 5+ academic projects. Strong foundation in data structures and algorithms."

SPECIAL HANDLING FOR STUDENTS:
- If "student" or "pursuing" is mentioned, note in designation
- Include coursework as skills if relevant
- Internships count as experience
- Academic projects are important - extract all
- Include GPA/CGPA if above 7.0/10 or 3.0/4.0

Return ONLY valid JSON matching this schema, no markdown formatting:
{json.dumps(response_schema)}
"""

    try:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",  # Fast and accurate Groq model
            messages=[
                {
                    "role": "system",
                    "content": "You are an expert resume parser specializing in student and entry-level resumes. Extract structured data accurately and return ONLY valid JSON without markdown formatting. Pay special attention to skills, projects, and education details."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=0.1,  # Very low for maximum accuracy
            max_tokens=3000,  # Increased for detailed resumes
            response_format={"type": "json_object"}
        )
        
        # Parse the JSON response
        result_text = response.choices[0].message.content
        parsed = json.loads(result_text)
        
        # Clean and validate the data
        cleaned_data = clean_and_validate_data(parsed)
        
        return cleaned_data
    except Exception as e:
        # Return safe defaults on error
        return {
            "name": "Unknown",
            "email": None,  # None, not empty string for EmailStr
            "contact": "",
            "location": "",
            "designation": "",
            "experience": "",
            "education": "",
            "skills": [],
            "certifications": [],
            "projects": [],
            "key_achievements": [],
            "professional_summary": f"Error parsing resume: {str(e)}"
        }


def parse_job_description(jd_text: str) -> dict:
    """
    Extract structured information from job description text
    Returns JD data in standardized format
    """
    
    response_schema = {
        "type": "object",
        "properties": {
            "job_title": {"type": "string"},
            "company": {"type": "string"},
            "location": {"type": "string"},
            "job_type": {"type": "string"},
            "experience_required": {"type": "string"},
            "required_skills": {"type": "array", "items": {"type": "string"}},
            "preferred_skills": {"type": "array", "items": {"type": "string"}},
            "responsibilities": {"type": "array", "items": {"type": "string"}},
            "qualifications": {"type": "array", "items": {"type": "string"}},
            "description": {"type": "string"}
        },
        "required": ["job_title", "required_skills"]
    }

    prompt = f"""
Extract structured information from this job description. Distinguish between required and preferred.

Job Description Text:
{jd_text}

Instructions:
1. Extract job title, company name, location
2. Job type (Full-time, Part-time, Contract, Remote, Hybrid)
3. Experience required (format: "X-Y years" or "X+ years")
4. Required skills (MUST have)
5. Preferred skills (nice to have, bonus)
6. Key responsibilities (main duties)
7. Qualifications (education, certifications)
8. Full description (comprehensive summary)

Guidelines:
- Clearly separate REQUIRED vs PREFERRED skills
- Normalize skill names (e.g., "JS" → "JavaScript")
- Extract all technical skills mentioned
- For responsibilities, list main job duties
- For qualifications, include education requirements
- If information is missing, use empty string or empty array

Return ONLY valid JSON matching this schema, no markdown formatting:
{json.dumps(response_schema)}
"""

    try:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",  # Fast and accurate Groq model
            messages=[
                {
                    "role": "system",
                    "content": "You are an expert job description parser. Extract structured data from JDs and return ONLY valid JSON without markdown formatting."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=0.2,
            max_tokens=2000,
            response_format={"type": "json_object"}
        )
        
        # Parse the JSON response
        result_text = response.choices[0].message.content
        parsed = json.loads(result_text)
        
        # Ensure required fields have defaults
        return {
            "job_title": parsed.get("job_title", "Untitled Position"),
            "company": parsed.get("company", ""),
            "location": parsed.get("location", ""),
            "job_type": parsed.get("job_type", ""),
            "experience_required": parsed.get("experience_required", ""),
            "required_skills": parsed.get("required_skills", []),
            "preferred_skills": parsed.get("preferred_skills", []),
            "responsibilities": parsed.get("responsibilities", []),
            "qualifications": parsed.get("qualifications", []),
            "description": parsed.get("description", "")
        }
    except Exception as e:
        # Return safe defaults on error
        return {
            "job_title": "Untitled Position",
            "company": "",
            "location": "",
            "job_type": "",
            "experience_required": "",
            "required_skills": [],
            "preferred_skills": [],
            "responsibilities": [],
            "qualifications": [],
            "description": f"Error parsing JD: {str(e)}"
        }
