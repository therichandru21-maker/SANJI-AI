from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import RedirectResponse
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from google.auth.transport import requests
from google.oauth2 import id_token
from jose import jwt
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.config import GOOGLE_CLIENT_ID, JWT_SECRET
from app.database import get_db
from app.models import User


router = APIRouter(
    prefix="/auth",
    tags=["Authentication"],
)

security = HTTPBearer()


ALGORITHM = "HS256"
TOKEN_EXPIRE_HOURS = 24


class GoogleLoginRequest(BaseModel):
    credential: str


def create_access_token(user_id: int):
    expire = datetime.now(timezone.utc) + timedelta(
        hours=TOKEN_EXPIRE_HOURS
    )

    payload = {
        "sub": str(user_id),
        "exp": expire,
    }

    return jwt.encode(
        payload,
        JWT_SECRET,
        algorithm=ALGORITHM,
    )


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db),
):
    token = credentials.credentials

    try:
        payload = jwt.decode(
            token,
            JWT_SECRET,
            algorithms=[ALGORITHM],
        )

        user_id = payload.get("sub")

        if not user_id:
            raise HTTPException(
                status_code=401,
                detail="Invalid authentication token.",
            )

    except Exception:
        raise HTTPException(
            status_code=401,
            detail="Invalid or expired authentication token.",
        )

    user = db.query(User).filter(
        User.id == int(user_id)
    ).first()

    if not user:
        raise HTTPException(
            status_code=401,
            detail="User not found.",
        )

    return user


@router.post("/google")
def google_login(
    request: GoogleLoginRequest,
    db: Session = Depends(get_db),
):
    try:
        google_user = id_token.verify_oauth2_token(
            request.credential,
            requests.Request(),
            GOOGLE_CLIENT_ID,
        )

    except Exception:
        raise HTTPException(
            status_code=401,
            detail="Invalid Google credential.",
        )

    google_sub = google_user.get("sub")
    email = google_user.get("email")
    name = google_user.get("name")
    picture = google_user.get("picture")

    if not google_sub or not email:
        raise HTTPException(
            status_code=400,
            detail="Google account information is incomplete.",
        )

    user = db.query(User).filter(
        User.google_sub == google_sub
    ).first()

    if not user:
        user = User(
            google_sub=google_sub,
            email=email,
            name=name,
            picture=picture,
        )

        db.add(user)
        db.commit()
        db.refresh(user)

    else:
        user.email = email
        user.name = name
        user.picture = picture
        user.last_login_at = datetime.now(timezone.utc)

        db.commit()
        db.refresh(user)

    access_token = create_access_token(user.id)

    return {
        "success": True,
        "access_token": access_token,
        "token_type": "bearer",
        "user": {
            "id": user.id,
            "email": user.email,
            "name": user.name,
            "picture": user.picture,
        },
    }


@router.get("/me")
def get_me(
    current_user: User = Depends(get_current_user),
):
    return {
        "success": True,
        "user": {
            "id": current_user.id,
            "email": current_user.email,
            "name": current_user.name,
            "picture": current_user.picture,
        },
    }