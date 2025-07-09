from typing import Annotated

from controllers.token_controller import TokenController
from deps import SessionDep
from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm

router = APIRouter()
session = SessionDep


@router.post("/token", tags=["token"])
def login_for_access_token(form_data: Annotated[OAuth2PasswordRequestForm, Depends()], 
                            session: SessionDep):
    return TokenController.login_for_access_token(form_data, session)