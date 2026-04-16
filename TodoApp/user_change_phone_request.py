from pydantic import BaseModel,Field
class ChangePhoneRquest(BaseModel):
    phone_number: str = Field()