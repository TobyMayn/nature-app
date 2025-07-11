from datetime import datetime, timedelta, timezone
from typing import Annotated

import jwt
from deps import SessionDep
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from models import Token, Users
from security import ACCESS_TOKEN_EXPIRE_MINUTES, ALGORITHM, SECRET_KEY, pwd_context
from sqlmodel import Session, select


class TokenService:
    def login_for_access_token(self, form_data: Annotated[OAuth2PasswordRequestForm, Depends()], 
                               session: SessionDep):
        user = self.authenticate_user(session, form_data.username, form_data.password)
        if not user:
            raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = self.create_access_token(
            data={"sub": user.username}, expires_delta=access_token_expires
        )
        return Token(access_token=access_token, token_type="bearer")
    
    def verify_password(self, plain_password: str, hashed_password: str):
        return pwd_context.verify(plain_password, hashed_password)
    
    def get_password_hash(self, plain_password: str):
        return pwd_context.hash(plain_password)
    
    def get_user(self, session: Session, username: str):
        statement = select(Users).where(Users.username == username)
        return session.exec(statement).first()
    
    def authenticate_user(self, session: Session, username: str, password: str):
        user = self.get_user(session, username)
        if not user:
            return False
        if not self.verify_password(password, user.password_hash):
            return False
        return user

    def create_access_token(self, data: dict, expires_delta: timedelta | None = None):
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.now(timezone.utc) + expires_delta
        else:
            expire = datetime.now(timezone.utc) + timedelta(minutes=15)
        
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
        return encoded_jwt