from pydantic import BaseModel,Field

class CreateUserRequest(BaseModel):
    user_name: str
    email: str
    first_name: str
    last_name: str
    password: str
    role: str