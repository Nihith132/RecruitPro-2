from fastapi import Header, HTTPException
from firebase_admin import auth as firebase_auth


async def verify_firebase_token(authorization: str = Header(None)) -> str:
    """Verify Firebase ID token and return UID"""
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=401, 
            detail="Missing or invalid authorization header"
        )
    
    token = authorization.split("Bearer ")[1]
    try:
        decoded_token = firebase_auth.verify_id_token(token)
        return decoded_token["uid"]
    except Exception as e:
        raise HTTPException(
            status_code=401, 
            detail=f"Invalid token: {str(e)}"
        )
