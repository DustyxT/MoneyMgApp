from fastapi import APIRouter, HTTPException, UploadFile, File, Form
from pydantic import BaseModel
from pathlib import Path
from typing import Optional
import json
import base64

router = APIRouter(prefix="/api/profile", tags=["profile"])

# Profile data file location
import sys
sys.path.append(str(Path(__file__).parent.parent))
from utils import get_data_path

DATA_DIR = get_data_path()
PROFILE_FILE = DATA_DIR / "profile.json"

class ProfileData(BaseModel):
    name: str = "User"
    picture: Optional[str] = None  # Base64 encoded image

def load_profile() -> dict:
    """Load profile from JSON file or return default."""
    if PROFILE_FILE.exists():
        try:
            with open(PROFILE_FILE, 'r') as f:
                return json.load(f)
        except:
            pass
    return {"name": "User", "picture": None}

def save_profile(data: dict):
    """Save profile to JSON file."""
    with open(PROFILE_FILE, 'w') as f:
        json.dump(data, f, indent=2)

@router.get("")
def get_profile() -> dict:
    """Get user profile data."""
    return load_profile()

@router.put("")
def update_profile(profile: ProfileData) -> dict:
    """Update user profile."""
    try:
        data = {
            "name": profile.name,
            "picture": profile.picture
        }
        save_profile(data)
        return {"success": True, "message": "Profile updated successfully", "profile": data}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/upload-picture")
async def upload_picture(file: UploadFile = File(...)) -> dict:
    """Upload profile picture and return base64 encoded string."""
    try:
        # Read file content
        content = await file.read()
        
        # Validate file size (max 10MB)
        if len(content) > 10 * 1024 * 1024:
            raise HTTPException(status_code=400, detail="File too large. Max size is 10MB.")
        
        # Convert to base64
        base64_encoded = base64.b64encode(content).decode('utf-8')
        
        # Get content type
        content_type = file.content_type or "image/jpeg"
        
        # Create data URL
        data_url = f"data:{content_type};base64,{base64_encoded}"
        
        return {"success": True, "picture": data_url}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
