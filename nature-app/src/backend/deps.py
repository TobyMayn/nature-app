from collections.abc import Generator
from typing import Annotated

import jwt
from database.db import engine
from fastapi import Depends, HTTPException, status
from jwt.exceptions import InvalidTokenError
from models import Users
from security import ALGORITHM, SECRET_KEY, oauth2_scheme
from sqlmodel import Session, select


def get_db() -> Generator[Session, None, None]:
    with Session(engine) as session:
        yield session


SessionDep = Annotated[Session, Depends(get_db)]


async def get_current_user(session: SessionDep, token: Annotated[str, Depends(oauth2_scheme)]) -> Users:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get("sub")
        if username is None:
            raise credentials_exception
    except InvalidTokenError:
        raise credentials_exception
    user = session.exec(select(Users).where(Users.username == username)).first()
    if user is None:
        raise credentials_exception
    return user