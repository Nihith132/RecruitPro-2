from fastapi import APIRouter, Depends
from typing import Dict, List
from collections import Counter

from database.mongodb import get_async_database
from routes.auth import verify_firebase_token

router = APIRouter(prefix="/api/analytics", tags=["Analytics"])


@router.get("/dashboard")
async def get_dashboard_analytics(uid: str = Depends(verify_firebase_token)) -> Dict:
    """Get dashboard analytics and metrics"""
    db = get_async_database()
    
    # Total counts
    total_candidates = await db.candidates.count_documents({"uid": uid})
    total_jds = await db.job_descriptions.count_documents({"uid": uid})
    
    # High scoring matches (50%+ match score)
    high_scoring_matches = await db.top_scores.count_documents({
        "uid": uid,
        "total_score": {"$gte": 50}
    })
    
    # Total matches processed
    total_matches = await db.top_scores.count_documents({"uid": uid})
    
    # Top 5 candidate-JD matches with highest scores
    top_matches = []
    cursor = db.top_scores.find({"uid": uid}).sort("total_score", -1).limit(5)
    
    async for match in cursor:
        # Get JD details
        jd = await db.job_descriptions.find_one({"jd_id": match.get("jd_id")})
        jd_title = jd.get("job_title", "Unknown JD") if jd else "Unknown JD"
        
        top_matches.append({
            "candidate_name": match.get("name", "Unknown Candidate"),
            "jd_name": jd_title,
            "score": round(match.get("total_score", 0), 1),
            "candidate_id": match.get("candidate_id"),
            "jd_id": match.get("jd_id")
        })
    
    return {
        "total_candidates": total_candidates,
        "total_jds": total_jds,
        "high_scoring_matches": high_scoring_matches,
        "total_matches": total_matches,
        "top_matches": top_matches
    }
