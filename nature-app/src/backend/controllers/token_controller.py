from typing import Annotated

from deps import SessionDep
from fastapi import Depends
from fastapi.security import OAuth2PasswordRequestForm
from services.token_service import TokenService


class TokenController():
    def login_for_access_token(self, form_data: Annotated[OAuth2PasswordRequestForm, Depends()], 
                               session: SessionDep):
        return TokenService.login_for_access_token(form_data, session)