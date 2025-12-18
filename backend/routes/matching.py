from fastapi import APIRouter, HTTPException, Depends, Body
from typing import List
from datetime import datetime
import uuid

from database.mongodb import get_async_database
from models.schemas import CandidateScore, WeightProfile
from llmservices.topscore_gemini import analyze_multiple_resumes_structured
from routes.auth import verify_firebase_token

router = APIRouter(prefix="/api", tags=["Matching"])


@router.get("/top-matches/{jd_id}", response_model=List[CandidateScore])
async def get_top_matches(
    jd_id: str,
    min_score: float = 0,  # Minimum score threshold (0-100)
    limit: int = 100,
    uid: str = Depends(verify_firebase_token)
):
    """Get top matching candidates for a job description with optional score filter"""
    db = get_async_database()
    
    # Verify JD exists and belongs to user
    jd = await db.job_descriptions.find_one({"jd_id": jd_id, "uid": uid})
    if not jd:
        raise HTTPException(status_code=404, detail="Job description not found")
    
    # Get scored candidates with score filter
    query = {
        "jd_id": jd_id, 
        "uid": uid,
        "total_score": {"$gte": min_score}  # Filter by minimum score
    }
    
    # Debug logging
    print(f"Querying top_scores with: jd_id={jd_id}, uid={uid}, min_score={min_score}")
    total_count = await db.top_scores.count_documents({"jd_id": jd_id, "uid": uid})
    print(f"Total documents for this JD and user: {total_count}")
    
    # Check if any documents exist without score filter
    sample_doc = await db.top_scores.find_one({"jd_id": jd_id, "uid": uid})
    if sample_doc:
        print(f"Sample document keys: {list(sample_doc.keys())}")
        print(f"Sample total_score value: {sample_doc.get('total_score', 'MISSING')}")
    else:
        print("No documents found for this JD and user at all!")
    
    cursor = db.top_scores.find(query).sort("total_score", -1).limit(limit)
    scores = []
    
    async for doc in cursor:
        doc["_id"] = str(doc["_id"])
        scores.append(CandidateScore(**doc))
    
    print(f"Returning {len(scores)} candidates after filtering")
    return scores


@router.post("/match")
async def match_candidates(
    jd_id: str = Body(...),
    candidate_ids: List[str] = Body(None),
    weight_profile: WeightProfile = Body(None),
    uid: str = Depends(verify_firebase_token)
):
    """Match specific candidates with a job description"""
    db = get_async_database()
    
    # Get JD
    jd = await db.job_descriptions.find_one({"jd_id": jd_id, "uid": uid})
    if not jd:
        raise HTTPException(status_code=404, detail="Job description not found")
    
    # Get candidates
    query = {"uid": uid}
    if candidate_ids:
        query["candidate_id"] = {"$in": candidate_ids}
    
    candidates_cursor = db.candidates.find(query)
    candidates = []
    async for candidate in candidates_cursor:
        candidates.append(candidate)
    
    if not candidates:
        raise HTTPException(status_code=404, detail="No candidates found")
    
    # Prepare resumes for scoring
    resumes = [{
        "candidate_id": c["candidate_id"],
        "name": c.get("name", "Unknown"),
        "email": c.get("email", ""),
        "skills": c.get("skills", []),
        "experience": c.get("experience", ""),  # Fixed: use 'experience' not 'experience_years'
        "education": c.get("education", []),
        "certifications": c.get("certifications", [])
    } for c in candidates]
    
    # Extract JD text (you might want to store this during upload)
    jd_text = f"""
    Job Title: {jd.get('job_title', '')}
    Required Skills: {', '.join(jd.get('required_skills', []))}
    Experience: {jd.get('experience_required', '')}
    Education: {jd.get('education_requirements', '')}
    Description: {jd.get('description', '')}
    """
    
    # Analyze with AI
    print(f"Sending {len(resumes)} candidates to AI for analysis")  # Debug logging
    scores = analyze_multiple_resumes_structured(jd_text, resumes)
    print(f"Received {len(scores) if isinstance(scores, list) else 'invalid'} scores from AI")  # Debug logging
    
    # Check if scores is valid
    if not scores or not isinstance(scores, list):
        error_msg = f"AI analysis failed: returned {type(scores).__name__} instead of list"
        print(f"ERROR: {error_msg}")
        raise HTTPException(status_code=500, detail=error_msg)
    
    if len(scores) == 0:
        error_msg = "AI analysis returned empty results. This may be due to API rate limits or processing errors."
        print(f"ERROR: {error_msg}")
        raise HTTPException(status_code=500, detail=error_msg)
    
    # Check for error in response - check first item carefully
    if len(scores) > 0:
        first_item = scores[0]
        if isinstance(first_item, dict) and "error" in first_item:
            error_detail = first_item.get('error', 'Unknown error')
            print(f"ERROR: AI analysis error: {error_detail}")
            raise HTTPException(status_code=500, detail=f"AI analysis error: {error_detail}")
    
    # Store or update scores
    for score in scores:
        # Skip invalid entries
        if not isinstance(score, dict):
            print(f"WARNING: Skipping non-dict score entry: {type(score)}")
            continue
            
        # Skip error entries
        if "error" in score:
            print(f"WARNING: Skipping error entry: {score.get('error')}")
            continue
            
        # Compute weighted total score: Skills 50%, Experience 30%, Education 15%, Certs 5%
        total_score = (
            score.get("skills_score", 0) * 0.50 +
            score.get("experience_score", 0) * 0.30 +
            score.get("education_score", 0) * 0.15 +
            score.get("certifications_score", 0) * 0.05
        )
        
        score_data = {
            "score_id": str(uuid.uuid4()),
            "jd_id": jd_id,
            "candidate_id": score["candidate_id"],
            "created_at": datetime.utcnow(),
            "total_score": total_score,  # Add computed total score
            **score,  # Spread operator to add all AI fields
            "uid": uid  # MUST BE LAST - override any uid from AI response
        }
        
        print(f"Saving score for candidate {score.get('name', 'Unknown')}: total_score={total_score}")
        
        # Update if exists, insert if not
        result = await db.top_scores.update_one(
            {"jd_id": jd_id, "candidate_id": score["candidate_id"]},
            {"$set": score_data},
            upsert=True
        )
        print(f"  - {'Inserted' if result.upserted_id else 'Updated'} document")
    
    return {"message": f"Matched {len(scores)} candidates successfully", "scores": scores}
