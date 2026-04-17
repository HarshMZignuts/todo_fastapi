from fastapi import Depends,HTTPException,Path,APIRouter
from models import Todos,Users
from database import SessionLocal
from typing import Annotated
from sqlalchemy.orm import Session
from starlette import status
from todo_request import TodoRequest
from .auth import bcrypt_context, get_current_user
from passlib.context import CryptContext
from user_verification_request import UserVerification
from user_change_phone_request import ChangePhoneRquest



router = APIRouter(
    prefix= '/user',
    tags=['user']
)
 

def get_db():
    db = SessionLocal() 
    try:
        yield db
    finally:
        db.close()
# Depends is dependancy injection

db_dependancy = Annotated[Session,Depends(get_db)]
user_dependancy = Annotated[dict,Depends(get_current_user)]
bcrypt_context = CryptContext(schemes=['bcrypt'], deprecated='auto')

@router.get("/", status_code=status.HTTP_200_OK)
async def get_user(user: user_dependancy,db:db_dependancy):
    if user is None:
        raise HTTPException(status_code=401,detail='Authentication failed.')
    
    return db.query(Users).filter(Users.id == user.get('id')).first()

@router.put("/password",status_code=status.HTTP_204_NO_CONTENT)
async def change_password(user: user_dependancy,db:db_dependancy
                          ,user_verification: UserVerification):
    
    if user is None:
        raise HTTPException(status_code=401,detail='Authentication failed.')
    
    user_model = db.query(Users).filter(Users.id == user.get('id')).first()

    if not bcrypt_context.verify(user_verification.password,user_model.hashed_password):
        raise HTTPException(status_code=401,detail='Error on password change.')
    
    user_model.hashed_password = bcrypt_context.hash(user_verification.new_password)
    db.add(user_model)
    db.commit()
    

@router.put("/phone",status_code=status.HTTP_204_NO_CONTENT)
async def change_phone_number(user: user_dependancy,db:db_dependancy,change_phone_rquest:ChangePhoneRquest):
    if user is None:
        raise HTTPException(status_code=401,detail='Authentication failed.')
    
    user_model = db.query(Users).filter(Users.id == user.get('id')).first()

    user_model.phone_number = change_phone_rquest.phone_number
    db.add(user_model)
    db.commit()

    #  we can also take phone number in path /phone/{phone_number}
