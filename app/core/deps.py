from typing import Annotated

from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.exceptions import UnauthorizedException
from app.db.database import get_db
from app.db.redis import is_blacklisted
from app.models.lawyer import Lawyer
from app.models.user import User
from app.services.auth_service import AuthService
from app.services.group_service import GroupService
from app.services.lawyer_service import LawyerService
from app.services.user_service import UserService

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")
oauth2_scheme_lawyer = OAuth2PasswordBearer(tokenUrl="/api/lawyer-auth/login")


def get_auth_service(db: Session = Depends(get_db)) -> AuthService:
    return AuthService(db)


def get_user_service(db: Session = Depends(get_db)) -> UserService:
    return UserService(db)


def get_group_service(db: Session = Depends(get_db)) -> GroupService:
    return GroupService(db)


def get_lawyer_service(db: Session = Depends(get_db)) -> LawyerService:
    return LawyerService(db)


async def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)], db: Session = Depends(get_db)
) -> User:
    if await is_blacklisted(token):
        raise UnauthorizedException("Token has been revoked")

    try:
        payload = jwt.decode(
            token, settings.secret_key, algorithms=[settings.algorithm]
        )
        user_id: int = payload.get("sub")
        token_type: str = payload.get("type")
        if user_id is None or token_type != "normal":
            raise UnauthorizedException("Invalid authentication credentials")
    except JWTError:
        raise UnauthorizedException("Invalid authentication credentials")

    user = db.query(User).filter(User.id == int(user_id)).first()
    if user is None:
        raise UnauthorizedException("User not found")
    return user


async def get_current_lawyer(
    token: Annotated[str, Depends(oauth2_scheme_lawyer)], db: Session = Depends(get_db)
) -> Lawyer:
    if await is_blacklisted(token):
        raise UnauthorizedException("Token has been revoked")

    try:
        payload = jwt.decode(
            token, settings.secret_key, algorithms=[settings.algorithm]
        )
        lawyer_id: int = payload.get("sub")
        token_type: str = payload.get("type")
        if lawyer_id is None or token_type != "lawyer":
            raise UnauthorizedException("Invalid authentication credentials")
    except JWTError:
        raise UnauthorizedException("Invalid authentication credentials")

    lawyer = db.query(Lawyer).filter(Lawyer.id == int(lawyer_id)).first()
    if lawyer is None:
        raise UnauthorizedException("Lawyer not found")
    return lawyer
