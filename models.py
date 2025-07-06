from pydantic import BaseModel

class User(BaseModel):
    username: str
    phone: str
    password: str
