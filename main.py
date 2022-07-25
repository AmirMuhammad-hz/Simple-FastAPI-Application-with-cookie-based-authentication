from fastapi import FastAPI, Request, Depends, HTTPException, status
from fastapi.responses import RedirectResponse
import uvicorn

from Auth import Authentication_Router
from confings import check_cookie, AccountInfo, cookies_collection, cookie_expire_time


class Server_Application:

    def __init__(self):
        auth_class = Authentication_Router(cookie_expire_time, "http://127.0.0.1:8000/HomePage")
        self.app = FastAPI()
        self.app.include_router(router=auth_class.router, prefix='/auth')
        self.app.add_api_route("/log_out", self.log_out, methods=["GET"], response_description='redirects to HomePage',
                               description="if the client was authorized, his/her cookie will be deleted and he/she will be redirected to HomePage, otherwise returns 404 status code")
        self.app.add_api_route("/HomePage", endpoint=self.hello, methods=["GET"])
        self.app.add_api_route("/my_account", endpoint=self.account_information, methods=["GET"],
                               response_model=AccountInfo,
                               description="if the client was authorized, returns client info, otherwise returns 401 status code")

    async def hello(self):
        return "hello"

    async def account_information(self, cookie: dict = Depends(check_cookie)):
        result = await cookies_collection.find_one(cookie)
        del result["_id"], result["date"], result["cookie"]
        return AccountInfo(**result)

    async def log_out(self, request: Request):
        result = await cookies_collection.find_one(request.cookies)
        if request.cookies == {} or not result:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
        response = RedirectResponse("http://127.0.0.1:8000/HomePage")
        response.delete_cookie("cookie")
        await cookies_collection.delete_one(request.cookies)
        return response


Application = Server_Application()
app = Application.app

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
