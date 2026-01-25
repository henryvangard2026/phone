#
#  FASTAPI:  Workstation Phone Management
#

# 1/17/26:  added 'r' to howtorun variable

#
# STATUS:  Completed!  1/17/26
#

howtorun = r"""

#
# HOWTO:
# 
# uvicorn fastapiphone:app --reload
#
# INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
#

Use curl to test endpoints.  Do not have to use Postman or Swagger/docs!


# get all phones
curl http://127.0.0.1:8000/phones

# get phone by ID
curl http://127.0.0.1:8000/phones/id/1000

# get phone by IMEI, "imei":"998877665544332211-1016"
curl http://127.0.0.1:8000/phones/imei/998877665544332211-1016

# get phone by serial number, "serial_number":"AA556677BB-1022"
curl http://127.0.0.1:8000/phones/serial_number/AA556677BB-1022

# get phone by workstation, "workstation":"WS1023"
curl http://127.0.0.1:8000/phones/workstation/WS1023

# OR
#
# you could go to:  http://127.0.0.1:8000/docs

"""


from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session as SQLASession

from typing import List

from pydantic import BaseModel

#from phone import Base, engine, Session, Phone, capPhoneDetails, seedTestPhones

import phone as ph


# JWT:  JSON Web Token
# ################################################

from datetime import datetime, timedelta
from jose import jwt, JWTError
from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer


SECRET_KEY = "XXX1975$$"
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


# PhoneCreate class for updating a phone endpoint:
# ################################################
    
class PhoneCreate(BaseModel):
    brand: str
    model: str
    os: str
    os_version: str
    serial_number: str
    imei: str
    status: str
    workstation: str


# PhoneUpdate class for updating a phone endpoint:
# ################################################

class PhoneUpdate(BaseModel):
    brand: str | None = None
    model: str | None = None
    os: str | None = None
    os_version: str | None = None
    serial_number: str | None = None
    imei: str | None = None
    status: str | None = None
    workstation: str | None = None
    
    
# PhoneRead class for reading a phone endpoint:
# ################################################

class PhoneRead(BaseModel):
    id: int
    brand: str
    model: str
    os: str
    os_version: str
    serial_number: str
    imei: str
    status: str
    workstation: str

    class Config:
        orm_mode = True


# create a session to the DB
def getDB():
    db_session = ph.Session()
    try:
        yield db_session
    finally:
        db_session.close()


# delete all phones 
def deleteAllPhones():
    db_session = ph.Session()
    try:
        db_session.query(ph.Phone).delete()
        db_session.commit()
    finally:
        db_session.close()

    
# create an instance of FASTAPI
# ###############################################

app = FastAPI()
    
    
# setup the database 
@app.on_event("startup")
def setupDB():
    ph.Base.metadata.create_all(ph.engine)

    db_session = ph.Session()

    if db_session.query(ph.Phone).count() == 0:
        ph.seedTestPhones()
        db_session.commit()

    db_session.close()
    

# endpoints:
# ###############################################

"""
# login endpoint without form 
@app.post("/login")
def login(username: str, password: str):
    # Replace with real user validation later
    if username != ADMIN or password != PW:
        raise HTTPException(status_code=401, detail="ERROR:  Invalid username or password.")

    token = create_access_token({"sub": username})
    return {"access_token": token, "token_type": "bearer"}
"""

# login with form
from fastapi import Form

@app.post("/login")
def login(username: str = Form(...), password: str = Form(...)):
    if username != ADMIN or password != PW:
        raise HTTPException(status_code=401, detail="ERROR:  Invalid username or password.")

    token = createAccessToken({"sub": username})
    return {"access_token": token, "token_type": "bearer"}


# VIEW ALL phones endpoint
@app.get("/phones", response_model=List[PhoneRead])
def getPhones(db: SQLASession = Depends(getDB), token: dict = Depends(requireToken)):
    return db.query(ph.Phone).all()


# VIEW one phone by ID
@app.get("/phones/id/{phoneID}", response_model=PhoneRead)
def getPhoneByID(phoneID: int, db: SQLASession =Depends(getDB), token: dict = Depends(requireToken)):
    phone = db.query(ph.Phone).filter(ph.Phone.id == phoneID).first()
    if not phone:
        raise HTTPException(status_code=404, detail=f"Phone with {phoneID} not found!")

    # the phone is found, return it
    return phone


# VIEW one phone by IMEI
@app.get("/phones/imei/{imei}", response_model=PhoneRead)
def getPhoneByIMEI(imei: str, db: SQLASession = Depends(getDB), token: dict = Depends(requireToken)):
    phone = db.query(ph.Phone).filter(ph.Phone.imei == imei.upper()).first()
    if not phone:
        raise HTTPException(status_code=404, detail=f"Phone with IMEI {imei} not found!")
    return phone


# VIEW one phone by Serial Number
@app.get("/phones/serial_number/{serial_number}", response_model=PhoneRead)
def getPhoneBySerial(serial_number: str, db: SQLASession = Depends(getDB), token: dict = Depends(requireToken)):
    phone = db.query(ph.Phone).filter(ph.Phone.serial_number == serial_number.upper()).first()
    if not phone:
        raise HTTPException(status_code=404, detail=f"Phone with serial number {serial_number} not found!")
    return phone


# VIEW one phone by Workstation
@app.get("/phones/workstation/{workstation}", response_model=PhoneRead)
def getPhoneByWorkstation(workstation: str, db: SQLASession = Depends(getDB), token: dict = Depends(requireToken)):
    phone = db.query(ph.Phone).filter(ph.Phone.workstation == workstation.upper()).first()
    if not phone:
        raise HTTPException(status_code=404, detail=f"Phone at workstation {workstation} not found!")
    return phone


# ADD a phone endpoint
@app.post("/add", response_model=PhoneRead)
def addPhone(newphone: PhoneCreate, 
             db: SQLASession = Depends(getDB), 
             token: dict = Depends(requireToken)):

    phone = ph.Phone(
        brand=newphone.brand,
        model=newphone.model,
        os=newphone.os,
        os_version=newphone.os_version,
        serial_number=newphone.serial_number.upper(),
        imei=newphone.imei.upper(),
        status=newphone.status,
        workstation=newphone.workstation.upper()
    )

    # capitalize for uniformity
    ph.capPhoneDetails(phone)

    try:
        db.add(phone)
        db.commit()
        db.refresh(phone)
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))

    return phone


# UPDATE a phone endpoint
@app.put("/update/id/{phoneID}", response_model=PhoneRead)
def updatePhoneByID(phoneID: int, update: PhoneUpdate, db: SQLASession  = Depends(getDB), token: dict = Depends(requireToken)):
    phone = db.query(ph.Phone).filter(ph.Phone.id == phoneID).first()
    
    if not phone:
        raise HTTPException(status_code=404, detail=f"Phone ID {phoneID} not found")

    # apply only updated details of a phone:  the fields/attributes (id, brand, model, ...)
    updates = update.dict(exclude_unset=True)
    for detail, value in updates.items():
        setattr(phone, detail, value)

    # capitalize for uniformity
    ph.capPhoneDetails(phone)

    try:
        db.commit()
        db.refresh(phone)
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))

    return phone
    
    
# DELETE a phone endpoint
@app.delete("/delete/id/{phoneID}")
def deletePhoneByID(phoneID: int, db: SQLASession  = Depends(getDB), token: dict = Depends(requireToken)):
    phone = db.query(ph.Phone).filter(ph.Phone.id == phoneID).first()

    if not phone:
        raise HTTPException(
            status_code=404,
            detail=f"Phone ID {phoneID} not found."
        )

    db.delete(phone)
    db.commit()

    return {"message": f"Phone ID {phoneID} deleted successfully!"}


# main

if __name__ == "__main__":
    print(howtorun)