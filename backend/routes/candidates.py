from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from fastapi.responses import StreamingResponse
from typing import List
import io
import uuid
import hashlib
from datetime import datetime
from bson import ObjectId

from database.mongodb import get_async_database, get_gridfs
from models.schemas import Candidate
from llmservices.parser_llm import parse_resume
from routes.auth import verify_firebase_token
from utils.file_extractor import extract_text_from_upload, is_supported_file

router = APIRouter(prefix="/api/candidates", tags=["Candidates"])


def generate_file_hash(content: bytes) -> str:
    """Generate SHA256 hash of file content for duplicate detection"""
    return hashlib.sha256(content).hexdigest()


@router.post("/upload", response_model=List[Candidate])
async def upload_candidates(
    files: List[UploadFile] = File(...),
    uid: str = Depends(verify_firebase_token)
):
    """
    Upload multiple candidate resumes with AI parsing
    Supports: PDF, DOCX, TXT, Images (JPG, PNG) - including scanned documents
    Prevents duplicate uploads based on file content hash and candidate email
    """
    db = get_async_database()
    fs = get_gridfs()
    candidates = []
    skipped_files = []
    
    for file in files:
        try:
            # Validate file type
            if not is_supported_file(file.filename):
                raise HTTPException(
                    status_code=400,
                    detail=f"Unsupported file format: {file.filename}. Supported: PDF, DOCX, TXT, JPG, PNG"
                )
            
            # Read file content once
            file_content = await file.read()
            
            # Generate file hash for duplicate detection
            file_hash = generate_file_hash(file_content)
            
            # Check for duplicate file hash
            existing_by_hash = await db.candidates.find_one({
                "uid": uid,
                "file_hash": file_hash
            })
            
            if existing_by_hash:
                print(f"Skipping duplicate file (by hash): {file.filename}")
                skipped_files.append({
                    "filename": file.filename,
                    "reason": "Duplicate file - same content already uploaded"
                })
                continue
            
            # Extract text using enhanced extractor (with OCR support)
            print(f"Extracting text from {file.filename}...")
            # Reset file pointer for text extraction
            file.file.seek(0)
            resume_text = await extract_text_from_upload(file)
            
            if not resume_text or len(resume_text.strip()) < 50:
                raise HTTPException(
                    status_code=400,
                    detail=f"Could not extract sufficient text from {file.filename}. Please ensure the file is readable."
                )
            
            print(f"Extracted {len(resume_text)} characters from {file.filename}")
            
            # Parse with AI first to get email for duplicate check
            print(f"Parsing resume with AI: {file.filename}")
            parsed_data = parse_resume(resume_text)
            print(f"Parsed data for {file.filename}: Name={parsed_data.get('name')}, Email={parsed_data.get('email')}, Skills={len(parsed_data.get('skills', []))}")
            
            # Check for duplicate by email (if email exists and is valid)
            if parsed_data.get('email'):
                existing_by_email = await db.candidates.find_one({
                    "uid": uid,
                    "email": parsed_data['email']
                })
                
                if existing_by_email:
                    print(f"Skipping duplicate candidate (by email): {parsed_data.get('email')}")
                    skipped_files.append({
                        "filename": file.filename,
                        "reason": f"Candidate with email {parsed_data['email']} already exists"
                    })
                    continue
            
            # Store file in GridFS
            file_id = await fs.upload_from_stream(
                file.filename,
                io.BytesIO(file_content),
                metadata={"content_type": file.content_type, "uploaded_by": uid}
            )
            
            # Create candidate document with file hash
            candidate_data = {
                "candidate_id": str(uuid.uuid4()),
                "uid": uid,
                "file_id": str(file_id),
                "file_hash": file_hash,  # Store hash for duplicate detection
                "resume_filename": file.filename,
                "uploaded_at": datetime.utcnow(),
                **parsed_data
            }
            
            result = await db.candidates.insert_one(candidate_data)
            candidate_data["_id"] = str(result.inserted_id)
            candidates.append(Candidate(**candidate_data))
            
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error processing {file.filename}: {str(e)}")
    
    # If some files were skipped, include that info in response headers
    if skipped_files:
        print(f"Upload complete. Uploaded: {len(candidates)}, Skipped: {len(skipped_files)}")
        for skipped in skipped_files:
            print(f"  - {skipped['filename']}: {skipped['reason']}")
    
    return candidates


@router.get("/", response_model=List[Candidate])
async def get_candidates(
    skip: int = 0,
    limit: int = 100,
    uid: str = Depends(verify_firebase_token)
):
    """Get all candidates with pagination"""
    db = get_async_database()
    cursor = db.candidates.find({"uid": uid}).skip(skip).limit(limit)
    candidates = []
    
    async for doc in cursor:
        doc["_id"] = str(doc["_id"])
        # Clean email field: convert empty string to None for EmailStr validation
        if "email" in doc and doc["email"] == "":
            doc["email"] = None
        candidates.append(Candidate(**doc))
    
    return candidates


@router.get("/{candidate_id}", response_model=Candidate)
async def get_candidate(
    candidate_id: str,
    uid: str = Depends(verify_firebase_token)
):
    """Get a specific candidate by ID"""
    db = get_async_database()
    candidate = await db.candidates.find_one({"candidate_id": candidate_id, "uid": uid})
    
    if not candidate:
        raise HTTPException(status_code=404, detail="Candidate not found")
    
    candidate["_id"] = str(candidate["_id"])
    # Clean email field
    if "email" in candidate and candidate["email"] == "":
        candidate["email"] = None
    return Candidate(**candidate)


@router.delete("/{candidate_id}")
async def delete_candidate(
    candidate_id: str,
    uid: str = Depends(verify_firebase_token)
):
    """Delete a candidate"""
    db = get_async_database()
    fs = get_gridfs()
    
    # Find candidate
    candidate = await db.candidates.find_one({"candidate_id": candidate_id, "uid": uid})
    if not candidate:
        raise HTTPException(status_code=404, detail="Candidate not found")
    
    # Delete file from GridFS
    try:
        file_id = ObjectId(candidate["file_id"])
        await fs.delete(file_id)
    except Exception as e:
        print(f"Warning: Could not delete file from GridFS: {e}")
    
    # Delete candidate document
    await db.candidates.delete_one({"candidate_id": candidate_id})
    
    # Delete associated scores
    await db.top_scores.delete_many({"candidate_id": candidate_id})
    
    return {"message": "Candidate deleted successfully"}


@router.post("/bulk-delete")
async def bulk_delete_candidates(
    candidate_ids: List[str],
    uid: str = Depends(verify_firebase_token)
):
    """Delete multiple candidates"""
    db = get_async_database()
    fs = get_gridfs()
    deleted_count = 0
    
    for candidate_id in candidate_ids:
        candidate = await db.candidates.find_one({"candidate_id": candidate_id, "uid": uid})
        if candidate:
            try:
                file_id = ObjectId(candidate["file_id"])
                await fs.delete(file_id)
            except Exception as e:
                print(f"Warning: Could not delete file from GridFS: {e}")
            
            await db.candidates.delete_one({"candidate_id": candidate_id})
            await db.top_scores.delete_many({"candidate_id": candidate_id})
            deleted_count += 1
    
    return {"deleted_count": deleted_count}


@router.get("/download/{candidate_id}")
async def download_candidate_resume(
    candidate_id: str,
    uid: str = Depends(verify_firebase_token)
):
    """
    Download the original resume file for a candidate
    Returns the raw file (PDF, DOCX, etc.) for viewing
    """
    db = get_async_database()  # Remove await - it's not async
    fs = get_gridfs()
    
    # Get candidate
    candidate = await db.candidates.find_one({"candidate_id": candidate_id})
    if not candidate:
        raise HTTPException(status_code=404, detail="Candidate not found")
    
    # Get file from GridFS
    try:
        file_id = ObjectId(candidate["file_id"])
        grid_out = await fs.open_download_stream(file_id)
        
        # Read file content
        contents = await grid_out.read()
        
        # Get filename and content type
        filename = candidate.get("resume_filename", f"{candidate.get('name', 'resume')}.pdf")
        
        # Determine content type based on file extension
        if filename.lower().endswith('.pdf'):
            content_type = 'application/pdf'
        elif filename.lower().endswith('.docx'):
            content_type = 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
        elif filename.lower().endswith('.doc'):
            content_type = 'application/msword'
        else:
            content_type = 'application/octet-stream'
        
        # Return file as streaming response
        return StreamingResponse(
            io.BytesIO(contents),
            media_type=content_type,
            headers={
                'Content-Disposition': f'inline; filename="{filename}"',
                'Content-Type': content_type
            }
        )
    except Exception as e:
        print(f"Error downloading file: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to download file: {str(e)}")
