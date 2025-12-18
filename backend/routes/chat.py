from fastapi import APIRouter, Depends, Body
from typing import List, Dict
import re

from llmservices.chat_llm import chat_ai
from routes.auth import verify_firebase_token
from database.mongodb import get_async_database

router = APIRouter(prefix="/api", tags=["Chat"])


async def smart_context_retrieval(message: str, uid: str) -> List[Dict]:
    """
    Smart context retrieval - only fetch relevant data based on query
    This minimizes token usage while providing accurate responses
    """
    db = get_async_database()
    context = []
    
    message_lower = message.lower()
    
    # Skill-based queries: "who knows python", "candidates with react"
    skill_patterns = [
        r'who (?:knows?|has) (\w+)',
        r'candidates? (?:with|having|knowing) (\w+)',
        r'find .*?(\w+) (?:skill|developer|engineer)',
    ]
    
    for pattern in skill_patterns:
        match = re.search(pattern, message_lower)
        if match:
            skill = match.group(1).capitalize()
            # Find candidates with this skill
            candidates = await db.candidates.find({
                "uid": uid,
                "skills": {"$regex": skill, "$options": "i"}
            }).limit(10).to_list(10)
            
            if candidates:
                context.append({
                    "type": "Candidates with Skill",
                    "data": [
                        {
                            "name": c.get("name"),
                            "skills": c.get("skills", []),
                            "experience": c.get("experience"),
                            "designation": c.get("designation"),
                            "candidate_id": c.get("candidate_id")
                        }
                        for c in candidates
                    ]
                })
            return context
    
    # Experience-based queries: "5+ years", "senior candidates"
    if re.search(r'\d+\+?\s*years?', message_lower) or 'senior' in message_lower or 'junior' in message_lower:
        # Get all candidates with experience info
        candidates = await db.candidates.find({
            "uid": uid,
            "experience": {"$exists": True}
        }).limit(15).to_list(15)
        
        if candidates:
            context.append({
                "type": "Candidates by Experience",
                "data": [
                    {
                        "name": c.get("name"),
                        "experience": c.get("experience"),
                        "designation": c.get("designation"),
                        "skills": c.get("skills", [])[:5],  # Top 5 skills only
                        "candidate_id": c.get("candidate_id")
                    }
                    for c in candidates
                ]
            })
        return context
    
    # JD-specific queries: "job description", "jd for", "requirements for"
    if any(keyword in message_lower for keyword in ['job description', 'jd for', 'requirements', 'position']):
        jds = await db.job_descriptions.find({"uid": uid}).limit(5).to_list(5)
        
        if jds:
            context.append({
                "type": "Job Descriptions",
                "data": [
                    {
                        "job_title": jd.get("job_title"),
                        "company": jd.get("company"),
                        "location": jd.get("location"),
                        "experience_required": jd.get("experience_required"),
                        "required_skills": jd.get("required_skills", []),
                        "jd_id": jd.get("jd_id")
                    }
                    for jd in jds
                ]
            })
        return context
    
    # Match score queries: "best matches", "top candidates", "highest scores"
    if any(keyword in message_lower for keyword in ['best match', 'top candidate', 'highest score', 'top match', 'score']):
        matches = await db.top_scores.find({"uid": uid}).sort("total_score", -1).limit(10).to_list(10)
        
        if matches:
            # Get JD details to provide context
            jd_map = {}
            for match in matches:
                jd_id = match.get("jd_id")
                if jd_id and jd_id not in jd_map:
                    jd = await db.job_descriptions.find_one({"jd_id": jd_id, "uid": uid})
                    if jd:
                        jd_map[jd_id] = {
                            "job_title": jd.get("job_title"),
                            "company": jd.get("company"),
                            "experience_required": jd.get("experience_required")
                        }
            
            context.append({
                "type": "Candidate Scores & Matches",
                "data": [
                    {
                        "candidate_name": m.get("name"),
                        "candidate_id": m.get("candidate_id"),
                        "email": m.get("email"),
                        "designation": m.get("designation"),
                        "experience": m.get("experience"),
                        "jd_id": m.get("jd_id"),
                        "jd_info": jd_map.get(m.get("jd_id"), {}),
                        "total_score": round(m.get("total_score", 0), 1),
                        "skills_score": round(m.get("skills_score", 0), 1),
                        "experience_score": round(m.get("experience_score", 0), 1),
                        "education_score": round(m.get("education_score", 0), 1),
                        "certifications_score": round(m.get("certifications_score", 0), 1),
                        "skills_matched": m.get("skills_matched", []),
                        "skills_related": m.get("skills_related", []),
                        "skills_missing": m.get("skills_missing", []),
                        "skills_explanation": m.get("skills_explanation", ""),
                        "experience_explanation": m.get("experience_explanation", ""),
                        "education_explanation": m.get("education_explanation", ""),
                        "certifications_explanation": m.get("certifications_explanation", "")
                    }
                    for m in matches
                ]
            })
        return context
    
    # Specific candidate score lookup: "what is [name]'s score", "how did [name] perform"
    name_match = re.search(r'(?:what is|how did|show me|tell me about) ([A-Z][a-z]+ [A-Z][a-z]+)', message)
    if name_match:
        candidate_name = name_match.group(1)
        # Find candidate scores
        matches = await db.top_scores.find({
            "uid": uid,
            "name": {"$regex": candidate_name, "$options": "i"}
        }).to_list(10)
        
        if matches:
            # Get JD details
            jd_map = {}
            for match in matches:
                jd_id = match.get("jd_id")
                if jd_id and jd_id not in jd_map:
                    jd = await db.job_descriptions.find_one({"jd_id": jd_id, "uid": uid})
                    if jd:
                        jd_map[jd_id] = {
                            "job_title": jd.get("job_title"),
                            "company": jd.get("company")
                        }
            
            context.append({
                "type": f"Scores for {candidate_name}",
                "data": [
                    {
                        "candidate_name": m.get("name"),
                        "jd_info": jd_map.get(m.get("jd_id"), {"job_title": "Unknown Position"}),
                        "total_score": round(m.get("total_score", 0), 1),
                        "skills_score": round(m.get("skills_score", 0), 1),
                        "experience_score": round(m.get("experience_score", 0), 1),
                        "education_score": round(m.get("education_score", 0), 1),
                        "certifications_score": round(m.get("certifications_score", 0), 1),
                        "skills_matched": m.get("skills_matched", []),
                        "skills_missing": m.get("skills_missing", []),
                        "skills_explanation": m.get("skills_explanation"),
                        "experience_explanation": m.get("experience_explanation"),
                        "education_explanation": m.get("education_explanation"),
                        "certifications_explanation": m.get("certifications_explanation")
                    }
                    for m in matches
                ]
            })
            return context
    
    # Candidate count queries: "how many candidates", "total candidates"
    if any(keyword in message_lower for keyword in ['how many', 'total', 'count']):
        candidate_count = await db.candidates.count_documents({"uid": uid})
        jd_count = await db.job_descriptions.count_documents({"uid": uid})
        match_count = await db.top_scores.count_documents({"uid": uid})
        
        context.append({
            "type": "System Statistics",
            "data": {
                "total_candidates": candidate_count,
                "total_job_descriptions": jd_count,
                "total_matches_processed": match_count
            }
        })
        return context
    
    # Generic candidate query - return summary of recent candidates
    if any(keyword in message_lower for keyword in ['candidate', 'resume', 'applicant']):
        candidates = await db.candidates.find({"uid": uid}).limit(8).to_list(8)
        
        if candidates:
            context.append({
                "type": "Recent Candidates",
                "data": [
                    {
                        "name": c.get("name"),
                        "designation": c.get("designation"),
                        "experience": c.get("experience"),
                        "skills": c.get("skills", [])[:5],
                        "candidate_id": c.get("candidate_id")
                    }
                    for c in candidates
                ]
            })
        return context
    
    return context


@router.post("/chat")
async def chat(
    message: str = Body(..., embed=True),
    context: List[Dict] = Body(None),
    uid: str = Depends(verify_firebase_token)
):
    """
    AI chat assistant with smart context retrieval
    Automatically fetches relevant candidate/JD data from MongoDB based on query
    """
    try:
        # Get smart context from database
        db_context = await smart_context_retrieval(message, uid)
        
        # Merge with conversation context (if provided)
        conversation_context = context or []
        full_context = db_context + conversation_context
        
        # Call AI with enriched context
        response = await chat_ai(message, full_context)
        return {"response": response}
    except Exception as e:
        print(f"Chat error: {str(e)}")
        return {"response": f"⚠️ I encountered an error while processing your request. Please try again."}

