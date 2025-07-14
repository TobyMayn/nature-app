from typing import Annotated

from controllers.auth_controller import AuthController
from deps import SessionDep
from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm

router = APIRouter()
session = SessionDep


@router.post("/auth/login", tags=["token"])
def login_for_access_token(form_data: Annotated[OAuth2PasswordRequestForm, Depends()], 
                            session: SessionDep):
    auth_controller = AuthController()
    return auth_controller.login_for_access_token(form_data, session)