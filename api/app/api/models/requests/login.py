from pydantic import BaseModel
from typing import Optional

class LoginReq(BaseModel):
    email: str
    password: str
    date_approved: date
    roles: str = "user"
