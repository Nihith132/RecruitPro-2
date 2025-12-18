from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
import io
import csv
import json

from database.mongodb import get_async_database
from models.schemas import ExportRequest
from routes.auth import verify_firebase_token

router = APIRouter(prefix="/api/export", tags=["Export"])


@router.post("/candidates")
async def export_candidates(
    request: ExportRequest,
    uid: str = Depends(verify_firebase_token)
):
    """Export candidates to CSV or JSON"""
    db = get_async_database()
    
    # Get candidates
    query = {"uid": uid}
    if request.ids:
        query["candidate_id"] = {"$in": request.ids}
    
    candidates = []
    async for doc in db.candidates.find(query):
        # Handle education - could be string or list
        education_value = doc.get("education", "")
        if isinstance(education_value, list):
            education_str = ", ".join([f"{e.get('degree', '')} - {e.get('institution', '')}" for e in education_value if isinstance(e, dict)])
        else:
            education_str = str(education_value) if education_value else ""
        
        candidates.append({
            "candidate_id": doc["candidate_id"],
            "name": doc.get("name", ""),
            "email": doc.get("email", ""),
            "contact": doc.get("contact", ""),  # Fixed: use 'contact' not 'phone'
            "skills": ", ".join(doc.get("skills", [])),
            "experience": doc.get("experience", ""),  # Fixed: use 'experience' (string) not 'experience_years' (int)
            "education": education_str,
            "certifications": ", ".join(doc.get("certifications", [])),
            "uploaded_at": doc.get("uploaded_at", "").isoformat() if doc.get("uploaded_at") else ""
        })
    
    if not candidates:
        raise HTTPException(status_code=404, detail="No candidates found")
    
    # Export based on format
    if request.format == "csv":
        output = io.StringIO()
        writer = csv.DictWriter(output, fieldnames=candidates[0].keys())
        writer.writeheader()
        writer.writerows(candidates)
        
        return StreamingResponse(
            iter([output.getvalue()]),
            media_type="text/csv",
            headers={"Content-Disposition": "attachment; filename=candidates.csv"}
        )
    else:  # json
        return StreamingResponse(
            iter([json.dumps(candidates, indent=2)]),
            media_type="application/json",
            headers={"Content-Disposition": "attachment; filename=candidates.json"}
        )


@router.post("/jds")
async def export_jds(
    request: ExportRequest,
    uid: str = Depends(verify_firebase_token)
):
    """Export job descriptions to CSV or JSON"""
    db = get_async_database()
    
    # Get JDs
    query = {"uid": uid}
    if request.ids:
        query["jd_id"] = {"$in": request.ids}
    
    jds = []
    async for doc in db.job_descriptions.find(query):
        jds.append({
            "jd_id": doc["jd_id"],
            "job_title": doc.get("job_title", ""),
            "company": doc.get("company", ""),
            "location": doc.get("location", ""),
            "required_skills": ", ".join(doc.get("required_skills", [])),
            "experience_required": doc.get("experience_required", ""),
            "education_requirements": doc.get("education_requirements", ""),
            "uploaded_at": doc.get("uploaded_at", "").isoformat() if doc.get("uploaded_at") else ""
        })
    
    if not jds:
        raise HTTPException(status_code=404, detail="No job descriptions found")
    
    # Export based on format
    if request.format == "csv":
        output = io.StringIO()
        writer = csv.DictWriter(output, fieldnames=jds[0].keys())
        writer.writeheader()
        writer.writerows(jds)
        
        return StreamingResponse(
            iter([output.getvalue()]),
            media_type="text/csv",
            headers={"Content-Disposition": "attachment; filename=job_descriptions.csv"}
        )
    else:  # json
        return StreamingResponse(
            iter([json.dumps(jds, indent=2)]),
            media_type="application/json",
            headers={"Content-Disposition": "attachment; filename=job_descriptions.json"}
        )
