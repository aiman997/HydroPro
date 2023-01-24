import bcrypt
import datetime
from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.security import HTTPBasic, HTTPBasicCredentials, OAuth2PasswordBearer
from pydantic import BaseModel
from typing import Optional
from fastapi import FastAPI

SECRET_KEY = "mysecretkey"
ALGORITHM = "HS256"

app = FastAPI()
security = HTTPBasic()

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    email: str

class User(BaseModel):
    email: str
    password: str
    rpi_address: str

users_db = []

@app.get("/")
def read_root():
    return {"Hello": "World"}

@app.get("/health")
def read_root():
    return "OK"

async def get_user(credentials: HTTPBasicCredentials):
    for user in users_db:
        if user.email == credentials.username:
            if bcrypt.checkpw(credentials.password.encode(), user.password.encode()):
                return user
    raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email or password")

@app.post("/users/")
async def create_user(user: User):
    hashed_password = bcrypt.hashpw(user.password.encode(), bcrypt.gensalt())
    user.password = hashed_password.decode()

    users_db.append(user)
    return {"email": user.email, "rpi_address": user.rpi_address}

@app.post("/auth")
async def authenticate_user(credentials: HTTPBasicCredentials = Depends(security)):
    user = await get_user(credentials)
    return {"email": user.email, "rpi_address": user.rpi_address}

@app.put("/update-password")
async def update_password(email: str, current_password: str, new_password: str):
    user = get_user(HTTPBasicCredentials(username=email,password=current_password))
    if user:
        hashed_password = bcrypt.hashpw(new_password.encode(), bcrypt.gensalt())
        user.password = hashed_password.decode()
        return {"email": user.email, "message": "password updated successfully"}
    raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email or password")

@app.put("/reset-password")
async def reset_password(email: str, new_password: str, token: str):
    user = get_user(HTTPBasicCredentials(username=email,password=token))
    if user:
        hashed_password = bcrypt.hashpw(new_password.encode(), bcrypt.gensalt())
        user.password = hashed_password.decode()
        return {"email": user.email, "message": "password reset successfully"}
    raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email or token")

def create_access_token(email: str):
    """
    Create a JWT token that contains the user's email as the payload
    """
    expires = datetime.timedelta(minutes=30)
    payload = {"email": email, "exp": datetime.datetime.utcnow() + expires}
    token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM).decode("utf-8")
    return token

@app.post("/request-reset-password")
async def request_reset_password(email: str):
    user = next((user for user in users_db if user.email == email), None)
    if user:
        token = create_access_token(email)
        # send the token to the user's email
        return {"email": email, "message": "password reset token sent"}
    raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email")

def verify_password(plain_password: str, hashed_password: str):
    """
    Verify the plain password against the hashed password
    """
    return plain_password == hashed_password

def create_token(email: str):
    """
    Create a new access token for the user
    """
    return {"access_token": create_access_token(email), "token_type": "bearer"}

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

def get_current_user(token: str = Depends(oauth2_scheme)):
    """
    Get the current user based on the access token
    """
    try:
        payload = decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("email")
        if email is None:
            raise HTTPException(status_code=400, detail="Invalid token")
        return email
    except Exception(e):
        raise HTTPException(status_code=400, detail="Invalid token")    

@app.post("/token")
def login(email: str, password: str):
    """
    Login endpoint
    """
    user = authenticate_user(email, password)
    return create_token(user["email"])
