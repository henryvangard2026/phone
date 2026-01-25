from datetime import datetime, timedelta
from jose import jwt, JWTError
from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer

import fastapiphone as fapi

SECRET_KEY = "Tv1975$$"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

ADMIN = 'MighteeXXX'
PW = 'pXXX$$'


# create access token
def createAccessToken(data: dict, expires_minutes: int = ACCESS_TOKEN_EXPIRE_MINUTES):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=expires_minutes)
    to_encode.update({"exp": expire})
    
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


# require token
def requireToken(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        raise HTTPException(status_code=401, detail="ERROR:  Invalid or expired token.")


# login endpoint
@app.post("/login")
def login(username: str, password: str):
    # Replace with real user validation later
    if username != ADMIN or password != PW:
        raise HTTPException(status_code=401, detail="ERROR:  Invalid username or password.")

    token = create_access_token({"sub": username})
    return {"access_token": token, "token_type": "bearer"}


# get all phones
@app.get("/phones", response_model=List[PhoneRead])
def getPhones(db: SQLASession = Depends(getDB),token: dict = Depends(require_token)):
    return db.query(ph.Phone).all()
