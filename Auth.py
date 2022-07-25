import datetime
from uuid import uuid4

from fastapi import APIRouter, Depends, status
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.responses import RedirectResponse

from confings import username_password_validation, usernames_passwords_collection, cookies_collection, \
    check_cookie_for_sign_or_log_in, username_password_validation_log_in


class Authentication_Router:
    def __init__(self, cookies_expire_time: int, redirect_link_to_client_account):
        self.expire_time = cookies_expire_time
        self.redirect_link = redirect_link_to_client_account
        self.router = APIRouter(dependencies=[Depends(check_cookie_for_sign_or_log_in)])
        self.router.add_api_route("/sign_in", endpoint=self.sign_in, methods=["POST"], tags=["Authentication"],
                                  description="Takes username and password, Checks the usernames and passwords collection in the database for the username, If there was no same username insert the given username and password and set the cookie needed for authentication, Then insert the cookie in the cookies collection, otherwise returns [same username already exist] ",
                                  response_description='redirect the client to the given link, in this case to HomePage')
        self.router.add_api_route("/log_in", self.log_in, methods=['POST'], tags=["Authentication"],
                                  description="takes username and password, checks the database for it, if username and password was correct cookie will be set and inserted in the cookie collection, otherwise returns [username or password is incorrect]",
                                  response_description='redirect the client to the given link, in this case to HomePage')

    async def sign_in(self,
                      form_data: OAuth2PasswordRequestForm | bool = Depends(username_password_validation)):
        info = {"username": form_data.username, "password": form_data.password}
        await usernames_passwords_collection.insert_one(info)
        info["cookie"] = str(uuid4())  # creates a random string
        info["date"] = datetime.datetime.utcnow()  # we need utc datetime for ttl
        await cookies_collection.insert_one(info)
        response = RedirectResponse(self.redirect_link, status_code=status.HTTP_302_FOUND)
        response.set_cookie(key="cookie", value=info["cookie"], expires=self.expire_time)
        return response

    async def log_in(self,
                     form_data: OAuth2PasswordRequestForm | bool = Depends(username_password_validation_log_in)):
        document = {"username": form_data.username, "password": form_data.password, "cookie": str(uuid4()),
                    "date": datetime.datetime.utcnow()}
        response = RedirectResponse(self.redirect_link, status_code=status.HTTP_302_FOUND)
        response.set_cookie(key="cookie", value=document["cookie"], expires=self.expire_time)
        await cookies_collection.insert_one(document)
        return response
