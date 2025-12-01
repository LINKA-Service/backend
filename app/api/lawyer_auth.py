from datetime import datetime, timedelta, timezone
from typing import Annotated

from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import jwt
from sqlalchemy.exc import IntegrityError

from app.core.config import settings
from app.core.deps import get_db
from app.core.exceptions import ConflictException, UnauthorizedException
from app.db.redis import add_to_blacklist
from app.schemas.lawyer import (
    LawyerCreate,
    LawyerResponse,
    LawyerToken,
    PasswordChange,
    StatusResponse,
)
from app.services.lawyer_service import LawyerService
from sqlalchemy.orm import Session

router = APIRouter()
oauth2_scheme_lawyer = OAuth2PasswordBearer(tokenUrl="/api/lawyer-auth/login")


def get_lawyer_service(db: Session = Depends(get_db)) -> LawyerService:
    return LawyerService(db)


@router.post("/register", response_model=LawyerResponse)
async def register(
    lawyer: LawyerCreate,
    lawyer_service: Annotated[LawyerService, Depends(get_lawyer_service)],
):
    try:
        return lawyer_service.create_lawyer(lawyer=lawyer)
    except IntegrityError:
        raise ConflictException("Lawyername already registered")


@router.post("/login", response_model=LawyerToken)
async def login(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    lawyer_service: Annotated[LawyerService, Depends(get_lawyer_service)],
):
    lawyer = lawyer_service.authenticate_lawyer(
        form_data.username, form_data.password
    )
    if not lawyer:
        raise UnauthorizedException("Incorrect lawyername or password")

    access_token_expires = timedelta(minutes=settings.access_token_expire_minutes)
    access_token = lawyer_service.create_access_token(
        data={"sub": str(lawyer.id), "type": "lawyer"}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}


@router.post("/logout", response_model=StatusResponse)
async def logout(
    token: Annotated[str, Depends(oauth2_scheme_lawyer)],
):
    try:
        payload = jwt.decode(
            token, settings.secret_key, algorithms=[settings.algorithm]
        )
        exp = payload.get("exp")
        now = datetime.now(timezone.utc).timestamp()
        expires_in = (
            max(int(exp - now), 60)
            if exp
            else settings.access_token_expire_minutes * 60
        )

        await add_to_blacklist(token, expires_in)

    except Exception:
        pass

    return {"message": "Successfully logged out"}


@router.post("/change-password", response_model=StatusResponse)
async def change_password(
    password_data: PasswordChange,
    token: Annotated[str, Depends(oauth2_scheme_lawyer)],
    lawyer_service: Annotated[LawyerService, Depends(get_lawyer_service)],
):
    from jose import JWTError
    from app.models.lawyer import Lawyer

    try:
        payload = jwt.decode(
            token, settings.secret_key, algorithms=[settings.algorithm]
        )
        lawyer_id: int = payload.get("sub")
        if lawyer_id is None or payload.get("type") != "lawyer":
            raise UnauthorizedException("Invalid authentication credentials")
    except JWTError:
        raise UnauthorizedException("Invalid authentication credentials")

    lawyer_service.change_password(
        lawyer_id=int(lawyer_id),
        current_password=password_data.current_password,
        new_password=password_data.new_password,
    )
    return {"message": "Password changed successfully"}
