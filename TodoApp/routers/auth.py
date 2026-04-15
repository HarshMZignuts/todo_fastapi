from datetime import datetime, timedelta, timezone

from fastapi import APIRouter,Depends,HTTPException
from database import SessionLocal
from typing import Annotated
from sqlalchemy.orm import Session
from starlette import status
from create_user_request import CreateUserRequest,Token
from models import Users
from passlib.context import CryptContext
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from jose import jwt,JWTError




router = APIRouter()
SECRET_KEY = 'aa81594dab604b072d6aa5afefc1d5c07b641a6490999d9407e66685d35750ad'
ALGORITHM = 'HS256'

bcrypt_context = CryptContext(schemes=['bcrypt'], deprecated='auto')
oauth2_bearer = OAuth2PasswordBearer(tokenUrl='token')


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
    return user

def create_access_token(user_name:str,user_id:int,expires_delta:timedelta):

    encode = {'sub': user_name, 'id': user_id}
    expires = datetime.now(timezone.utc) + expires_delta
    encode.update({'exp':expires})
    return jwt.encode(encode,SECRET_KEY,algorithm=ALGORITHM)

async def get_current_user(token: Annotated[str,Depends(oauth2_bearer)]):
    try:
        payload = jwt.decode(token,SECRET_KEY,algorithms=[ALGORITHM])
        user_name: str = payload.get('sub')
        user_id: str = payload.get('id')
        if user_name is None or user_id is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail='Could not validate user.')
        return {'user_name': user_name, 'id' : user_id}
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail='Could not validate user.')


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

@router.post("/token",response_model=Token)
async def login_for_access_token(form_data: Annotated[OAuth2PasswordRequestForm,Depends()],
                                 db: db_dependancy):
    user = authenticate_user(form_data.username,form_data.password,db)
    if not user:
        return 'Failed Authentication'
    
    token = create_access_token(user.user_name,user.id,timedelta(minutes=20))
    return {'access_token':token, 'token_type': 'bearer'}