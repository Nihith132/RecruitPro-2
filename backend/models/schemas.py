from pydantic import BaseModel, Field, EmailStr
from typing import List, Optional, Dict
from datetime import datetime


class Candidate(BaseModel):
    """Candidate model with all extracted information"""
    candidate_id: str = Field(..., description="Unique candidate identifier")
    uid: str = Field(..., description="User ID (Firebase UID)")
    file_hash: Optional[str] = None  # SHA256 hash for duplicate detection
    name: Optional[str] = "Unknown"  # Changed to Optional with default
    email: Optional[EmailStr] = None
    contact: Optional[str] = None
    location: Optional[str] = None
    designation: Optional[str] = None
    experience: Optional[str] = None
    education: Optional[str] = None
    skills: List[str] = Field(default_factory=list)
    certifications: List[str] = Field(default_factory=list)
    projects: List[str] = Field(default_factory=list)
    key_achievements: List[str] = Field(default_factory=list)
    professional_summary: Optional[str] = None
    profile_type: Optional[str] = None  # fresher, junior, mid, senior, principal
    resume_url: Optional[str] = None
    resume_filename: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class JobDescription(BaseModel):
    """Job Description model"""
    jd_id: str = Field(..., description="Unique JD identifier")
    uid: str = Field(..., description="User ID (Firebase UID)")
    file_hash: Optional[str] = None  # SHA256 hash for duplicate detection
    job_title: Optional[str] = "Untitled Position"  # Changed to Optional with default
    company: Optional[str] = None
    location: Optional[str] = None
    job_type: Optional[str] = None  # Full-time, Part-time, Contract
    experience_required: Optional[str] = None
    required_skills: List[str] = Field(default_factory=list)
    preferred_skills: List[str] = Field(default_factory=list)
    responsibilities: List[str] = Field(default_factory=list)
    qualifications: List[str] = Field(default_factory=list)
    description: Optional[str] = None
    jd_url: Optional[str] = None
    jd_filename: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class CandidateScore(BaseModel):
    """Scoring result for a candidate against a JD"""
    uid: str
    candidate_id: str
    jd_id: str
    name: str
    email: Optional[str] = None
    contact: Optional[str] = None
    designation: Optional[str] = None
    experience: Optional[str] = None
    education: Optional[str] = None
    location: Optional[str] = None
    resume_url: Optional[str] = None
    profile_type: Optional[str] = None
    
    # Scores (0-100)
    skills_score: float = Field(..., ge=0, le=100)
    skills_explanation: str
    experience_score: float = Field(..., ge=0, le=100)
    experience_explanation: str
    education_score: float = Field(..., ge=0, le=100)
    education_explanation: str
    certifications_score: float = Field(..., ge=0, le=100)
    certifications_explanation: str
    
    # Matched skills
    skills_matched: List[str] = Field(default_factory=list)
    skills_related: List[str] = Field(default_factory=list)
    skills_missing: List[str] = Field(default_factory=list)
    
    key_achievements: List[str] = Field(default_factory=list)
    
    # Weighted total score
    total_score: Optional[float] = None
    
    created_at: datetime = Field(default_factory=datetime.utcnow)


class WeightProfile(BaseModel):
    """Weight configuration for scoring"""
    profile_type: str  # fresher, junior, mid, senior, principal
    skills_weight: float = Field(..., ge=0, le=1)
    experience_weight: float = Field(..., ge=0, le=1)
    education_weight: float = Field(..., ge=0, le=1)
    certifications_weight: float = Field(..., ge=0, le=1)


class ExportRequest(BaseModel):
    """Export request model"""
    format: str = Field(..., description="csv or json")
    candidate_ids: Optional[List[str]] = None
    jd_ids: Optional[List[str]] = None
