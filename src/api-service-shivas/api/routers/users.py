from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import logging
from ..utils.user_manager import UserManager

# Initialize Router and User Manager
router = APIRouter()
user_manager = UserManager(bucket_name="innit_articles_bucket")

# Define a schema for the register request
class RegisterRequest(BaseModel):
    username: str
    password: str

class LoginRequest(BaseModel):
    username: str
    password: str

class MetadataUpdateRequest(BaseModel):
    username: str
    metadata: dict

class MetadataResponse(BaseModel):
    username: str
    metadata: dict


@router.post("/register")
def register_user(request: RegisterRequest):
    """Register a new user."""
    try:
        user_manager.register_user(request.username, request.password, {})
        return {"message": "User registered successfully"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/login")
def login_user(request: LoginRequest):
    """Authenticate user with username and password."""
    username = request.username
    password = request.password
    logging.info(f"Login attempt for username: {username}")
    try:
        token = user_manager.authenticate_user(username, password)
        logging.info(f"User '{username}' authenticated successfully")
        return {"message": "Login successful", "token": token}
    except Exception as e:
        logging.error(f"Authentication failed for '{username}': {str(e)}")
        raise HTTPException(status_code=401, detail="Invalid credentials")

@router.patch("/update-metadata")
def update_metadata(request: MetadataUpdateRequest):
    """Update user metadata."""
    try:
        user_manager.update_metadata(request.username, request.metadata)
        return {"message": "Metadata updated successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    

@router.get("/get-metadata", response_model=MetadataResponse)
def get_metadata(username: str):
    """Fetch user metadata."""
    try:
        metadata = user_manager.get_metadata(username)
        return {"username": username, "metadata": metadata}
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))
