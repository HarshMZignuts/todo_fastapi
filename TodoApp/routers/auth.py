from fastapi import APIRouter,Depends
from database import SessionLocal
from typing import Annotated
from sqlalchemy.orm import Session
from starlette import status
from create_user_request import CreateUserRequest
from models import Users
from passlib.context import CryptContext
from fastapi.security import OAuth2PasswordRequestForm


router = APIRouter()

bcrypt_context = CryptContext(schemes=['bcrypt'], deprecated='auto')


def get_db():
    db = SessionLocal() 
    try:
        yield db
    finally:
        db.close()
# Depends is dependancy injection

db_dependancy = Annotated[Session,Depends(get_db)]

def authenticate_user(user_name:str,password:str,db):
    user = db.query(Users).filter(Users.user_name == user_name).first()
    if not user:
        return False
    if not bcrypt_context.verify(password,user.hashed_password):
        return False
    return True

@router.post("/auth",status_code=status.HTTP_201_CREATED)
async def create_user(db:db_dependancy,
                      create_user_request:CreateUserRequest):
    create_user_model = Users(
        email = create_user_request.email,
        user_name = create_user_request.user_name,
        first_name = create_user_request.first_name,
        last_name = create_user_request.last_name,
        role = create_user_request.role,
        hashed_password = bcrypt_context.hash(create_user_request.password),
        is_active = True
    )

    db.add(create_user_model)
    db.commit()

@router.post("/token")
async def login_for_access_token(form_data: Annotated[OAuth2PasswordRequestForm,Depends()],
                                 db: db_dependancy):
    user = authenticate_user(form_data.username,form_data.password,db)
    if not user:
        return 'Failed Authentication'
    return 'Successful Authentication'