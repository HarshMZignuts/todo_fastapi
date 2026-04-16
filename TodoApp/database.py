from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

# for sqllite3 db for local use
#SQLALCHEMY_DATABASE_URL = 'sqlite:///./todosapp.db' 
# for postgres db connection
SQLALCHEMY_DATABASE_URL = 'postgresql://postgres:ztlab112@localhost/TodoApplicationDataBase'  
# for MySql db connection
#SQLALCHEMY_DATABASE_URL = 'mysql+pymysql://root:ztlab112@127.0.0.1:3306/TodoApplicationDatabase' 

engine = create_engine(SQLALCHEMY_DATABASE_URL) #connect_args={'check_same_thread': False} this use only for sqllite3

SessionLocal = sessionmaker(autocommit= False, autoflush= False,bind=engine)

Base = declarative_base()

