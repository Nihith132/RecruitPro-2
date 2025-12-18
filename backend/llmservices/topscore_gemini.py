import os
import json
from dotenv import load_dotenv
from typing import List, Dict
from groq import Groq

load_dotenv()
client = Groq(api_key=os.getenv("GROQ_API_KEY"))


def analyze_multiple_resumes_structured(job_text: str, candidates: List[Dict]) -> List[Dict]:
    """
    Enhanced resume scoring with:
    - Weighted scoring criteria
    - Semantic skills matching
    - Bias mitigation
    - Better experience classification
    - Edge case handling
    """
    
    response_schema = {
        "type": "object",
        "properties": {
            "candidates": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                "uid": {"type": "string"},
                "candidate_id": {"type": "string"},
                "name": {"type": "string"},
                "contact": {"type": "string"},
                "email": {"type": "string"},
                "education": {"type": "string"},
                "location": {"type": "string"},
                "designation": {"type": "string"},
                "experience": {"type": "string"},
                "resume_url": {"type": "string"},
                "profile_type": {"type": "string"},
                "skills_score": {"type": "number", "minimum": 0, "maximum": 100},
                "skills_explanation": {"type": "string"},
                "experience_score": {"type": "number", "minimum": 0, "maximum": 100},
                "experience_explanation": {"type": "string"},
                "education_score": {"type": "number", "minimum": 0, "maximum": 100},
                "education_explanation": {"type": "string"},
                "certifications_score": {"type": "number", "minimum": 0, "maximum": 100},
                "certifications_explanation": {"type": "string"},
                "skills_matched": {"type": "array", "items": {"type": "string"}},
                "skills_related": {"type": "array", "items": {"type": "string"}},
                "skills_missing": {"type": "array", "items": {"type": "string"}},
                "key_achievements": {"type": "array", "items": {"type": "string"}},
            },
            "required": [
                "uid", "candidate_id", "name", "contact", "email", "education", "experience", "location",
                "designation", "resume_url", "profile_type", "skills_score", "skills_explanation",
                "experience_score", "experience_explanation", "education_score", "education_explanation",
                "certifications_score", "certifications_explanation", "skills_matched", "skills_related",
                "skills_missing", "key_achievements"
            ]
                }
            }
        },
        "required": ["candidates"]
    }

    prompt = f"""
You are an expert recruitment analyst. Evaluate candidates against the job description with enhanced scoring methodology.

🚨 BIAS PREVENTION RULES:

1. Education Scoring:
   - Score based on DEGREE LEVEL and FIELD relevance ONLY
   - DO NOT favor: Ivy League, top-tier universities, specific countries
   - Treat online degrees, bootcamps, self-taught equally if relevant

2. Name/Gender/Location:
   - IGNORE: Name origins, gender indicators, age, nationality
   - Focus ONLY on: Skills, experience, achievements

3. Career Gaps:
   - DO NOT penalize gaps < 2 years
   - If gap > 2 years, check for: freelance, side projects, upskilling
   - Mention gaps neutrally: "2-year career break, returned with updated skills"

4. Certifications:
   - Score based on RELEVANCE, not cost/prestige
   - Free certifications (Coursera, Google) = paid (AWS, Microsoft) if relevant

5. Language:
   - If resume has minor grammar/spelling errors, DO NOT lower scores
   - Focus on technical content, not writing quality

---

Job Description:
{job_text}

Candidates:
{json.dumps(candidates, indent=2)}

---

SCORING METHODOLOGY (0-100 for each category):

**Skills Scoring Breakdown:**
- Core skills match (50%): Are required skills present?
- Depth of experience (30%): Years using each skill?
- Recency (20%): Used in last 2 years?

Scoring Rubric:
- 90-100: Excellent match. All key requirements met with strong evidence
- 70-89: Good match. Most important criteria covered, minor gaps
- 50-69: Moderate match. Partially meets expectations, missing key items
- 30-49: Weak match. Only a few relevant elements present
- 0-29: Very poor or no alignment

**Experience Scoring:**
- Analyze: previous roles, titles, domains, seniority, tools
- Match against: job responsibilities, industry context
- Consider: years of experience, job function, progression
- Score higher for: aligned roles with strong duration

**Education Scoring:**
- Check: degree(s), field of study, institution(s), graduation year(s)
- Compare to: job requirements
- Score higher for: exact or higher degree levels and relevant fields
- Edge cases: If no formal degree, score as 50 (neutral), check for certifications/bootcamps

**Certifications Scoring:**
- Evaluate: relevance and validity to the role
- Score based on: match and industry recognition

---

PROFILE CLASSIFICATION:

Based on total years of experience:
- 0-1 years: "fresher"
- 2-5 years: "junior_professional"
- 6-10 years: "mid_level_professional"
- 11-15 years: "senior_professional"
- 16+ years: "principal_engineer"

Adjust classification UP if title contains:
- "Lead", "Senior", "Principal" → +1 level
- "Manager", "Director", "VP" → +2 levels
- "Architect", "Staff Engineer" → +1 level

---

SKILLS MATCHING RULES:

1. Exact Match:
   - Resume: "Python", JD: "Python" → ✅ Match

2. Synonym Match:
   - Resume: "JS", JD: "JavaScript" → ✅ Match
   - Resume: "ML", JD: "Machine Learning" → ✅ Match
   - Resume: "React.js", JD: "React" → ✅ Match

3. Hierarchical Match (implied skills):
   - Resume: "React", JD: "JavaScript" → ✅ Match (React implies JS)
   - Resume: "TensorFlow", JD: "Deep Learning" → ✅ Match
   - Resume: "AWS Lambda", JD: "Serverless" → ✅ Match

4. Cluster Match (related skills):
   - Resume: "PyTorch", JD: "TensorFlow" → Add to skills_related (both deep learning)
   - Mention in explanation: "Has PyTorch (similar to required TensorFlow)"

5. Version Match:
   - Resume: "Python 3.11", JD: "Python" → ✅ Match (mention version in explanation)

Output Format:
{{
  "skills_matched": ["Python", "React (implies JavaScript)", "AWS Lambda (serverless)"],
  "skills_related": ["PyTorch (similar to TensorFlow)"],
  "skills_missing": ["Docker", "Kubernetes"]
}}

---

EXPLANATION FORMAT (make explanations actionable):

❌ BAD: "Good Python skills"
✅ GOOD: "Strong Python skills demonstrated through 5 years experience, including recent projects: 
         - Built ML pipeline using TensorFlow (2023)
         - Developed REST APIs with FastAPI (2024)
         Matches JD requirement for Python backend development."

For each score category, explain:
1. WHAT matched (specific items)
2. WHY it's a match (relevance to JD)
3. GAPS (what's missing, if any)
4. EVIDENCE (cite resume sections, projects, years)

---

EDGE CASES:

1. Missing Education:
   - If no degree mentioned, score education as 50 (neutral)
   - Check for: certifications, bootcamps, self-taught projects as alternatives
   - Explanation: "No formal degree listed, but has Google Cloud certification and 5 years industry experience"

2. Bootcamp Graduates:
   - Treat coding bootcamps as equivalent to Associate's degree in CS
   - Score based on: bootcamp reputation + post-bootcamp experience

3. Career Gaps:
   - If gap > 1 year, check for:
     - Freelance projects
     - GitHub contributions
     - Side businesses
     - Upskilling (courses, certifications)
   - Mention neutrally: "2-year gap (2020-2022), used time for AWS certification"

4. Freelance/Contract Work:
   - Count freelance years as regular experience
   - Multiple short contracts = continuous experience (don't penalize)

5. Overqualified Candidates:
   - If candidate has 15 years exp for a 5 year role:
     - Still score high (they meet requirements)
     - Flag in explanation: "Exceeds experience requirement (15 vs 5 years). May seek higher compensation."

6. Career Changers:
   - If recent career change (e.g., teacher → developer):
     - Focus on NEW field skills (not old career)
     - Score based on: bootcamp, projects, internships in new field

---

Return a valid JSON object with a "candidates" array matching the schema. Be thorough, fair, and evidence-based in your evaluations.

Example output format:
{{
  "candidates": [
    {{
      "uid": "...",
      "candidate_id": "...",
      "name": "...",
      ...
    }},
    {{
      "uid": "...",
      "candidate_id": "...",
      "name": "...",
      ...
    }}
  ]
}}

Schema: {json.dumps(response_schema)}
"""

    try:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",  # Fast and accurate Groq model
            messages=[
                {
                    "role": "system",
                    "content": "You are an expert technical recruiter. Analyze candidates objectively and return ONLY valid JSON without markdown formatting."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=0.4,  # Slightly higher for nuanced scoring
            max_tokens=8000,  # Need more tokens for multiple candidates
            response_format={"type": "json_object"}
        )
        
        # Parse the JSON response
        result_text = response.choices[0].message.content
        print(f"AI Response (first 500 chars): {result_text[:500]}")  # Debug logging
        
        result = json.loads(result_text)
        print(f"Parsed result keys: {result.keys() if isinstance(result, dict) else 'List'}")  # Debug logging
        
        # Handle both array and object with array property
        if isinstance(result, list):
            parsed = result
        elif isinstance(result, dict) and "candidates" in result:
            parsed = result["candidates"]
        elif isinstance(result, dict) and "scores" in result:
            parsed = result["scores"]
        else:
            # Try to find the array in the result
            for key, value in result.items():
                if isinstance(value, list) and len(value) > 0:
                    print(f"Found array in key '{key}' with {len(value)} items")  # Debug logging
                    parsed = value
                    break
            else:
                # If no array found, log the structure and return error
                print(f"ERROR: Could not find candidate array in result. Keys: {list(result.keys())}")
                print(f"Full result: {result}")
                return [{
                    "error": f"Invalid AI response format. Expected array or object with 'candidates'/'scores' key. Got keys: {list(result.keys())}",
                    "candidate_id": candidates[0]["candidate_id"] if candidates else "unknown",
                    "name": candidates[0].get("name", "Unknown") if candidates else "Unknown"
                }]
        
        if not parsed or len(parsed) == 0:
            print("WARNING: Parsed result is empty")
            return [{
                "error": "AI returned empty results",
                "candidate_id": candidates[0]["candidate_id"] if candidates else "unknown",
                "name": candidates[0].get("name", "Unknown") if candidates else "Unknown"
            }]
        
        print(f"Successfully parsed {len(parsed)} candidate scores")
        return parsed
    except json.JSONDecodeError as e:
        print(f"JSON Decode Error: {e}")
        print(f"Response text: {result_text if 'result_text' in locals() else 'Not available'}")
        return [{
            "error": f"Failed to parse AI response as JSON: {str(e)}",
            "candidate_id": candidates[0]["candidate_id"] if candidates else "unknown",
            "name": candidates[0].get("name", "Unknown") if candidates else "Unknown"
        }]
    except Exception as e:
        print(f"Unexpected error in analyze_multiple_resumes_structured: {e}")
        import traceback
        traceback.print_exc()
        return [{
            "error": str(e),
            "candidate_id": candidates[0]["candidate_id"] if candidates else "unknown",
            "name": candidates[0].get("name", "Unknown") if candidates else "Unknown"
        }]
