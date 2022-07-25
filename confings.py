from motor.motor_asyncio import AsyncIOMotorClient
from fastapi.security import OAuth2PasswordRequestForm
from fastapi import Depends, Request, HTTPException, status
from pydantic import BaseModel

recaptcha_site_key = "secret"
recaptcha_secret_key = "secret"

cookie_expire_time: int = 30    # also expire time for mongodb ttl index, which should be created before running the application

# database and collections:
mongo_client = AsyncIOMotorClient('mongodb://localhost:27017')
db = mongo_client["db"]
usernames_passwords_collection = db["usernames and passwords"]
cookies_collection = db["cookies"]


class AccountInfo(BaseModel):
    username: str
    password: str


async def username_password_validation(form_data: OAuth2PasswordRequestForm = Depends()):
    result = await usernames_passwords_collection.find_one({"username": form_data.username})
    if result:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="same username already exist")
    return form_data


async def username_password_validation_log_in(form_data: OAuth2PasswordRequestForm = Depends()):
    result = await usernames_passwords_collection.find_one(
        {"username": form_data.username, "password": form_data.password})
    if result:
        return form_data
    raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="username or password is incorrect")


async def check_cookie(request: Request):
    result = await cookies_collection.find_one(request.cookies)
    if not result or request.cookies == {}:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
    return request.cookies


async def check_cookie_for_sign_or_log_in(request: Request):
    result = await cookies_collection.find_one(request.cookies)
    if result and request.cookies != {}:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    return request.cookies
