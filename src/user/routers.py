from fastapi import APIRouter, Depends, status, Request
from sqlalchemy.orm import Session
from src.user.dtos import UserDTO, UserResponse, loginDTO
from src.utils.db import get_db
from src.user.controller import register, loginUser, is_authenticated

user_routers = APIRouter(prefix='/user')

@user_routers.post('/signup', response_model= UserResponse, status_code=status.HTTP_201_CREATED)
def signup(body: UserDTO, db:Session = Depends(get_db)):
    return register(body, db)

@user_routers.get('/login', status_code=status.HTTP_200_OK)
def login(body: loginDTO, db:Session=Depends(get_db)):
    return loginUser(body, db)

@user_routers.post('/authenticate', status_code=status.HTTP_200_OK)
def is_auth(req: Request, db:Session = Depends(get_db)):
    return is_authenticated(req, db)