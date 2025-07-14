from typing import Annotated

from deps import SessionDep
from fastapi import Depends
from fastapi.security import OAuth2PasswordRequestForm
from services.auth_service import AuthService


class AuthController():
    def login_for_access_token(self, form_data: Annotated[OAuth2PasswordRequestForm, Depends()], 
                               session: SessionDep):
        auth_service = AuthService()
        return auth_service.login_for_access_token(form_data, session)