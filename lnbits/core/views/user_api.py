from typing import Optional

from fastapi import Body, Depends, Response, status
from fastapi.responses import JSONResponse
from loguru import logger

from .. import core_app
from ..crud import create_user, get_user, get_account_by_email
from ..models import createUser
from ..services import load_user, login_manager


@core_app.get("/api/v1/user")
async def user(user=Depends(login_manager)):
    return user


@core_app.post(
    "/api/v1/login", description="Login to the API via the username and password"
)
async def login_endpoint(
    response: Response,
    username: str = Body(),
    password: str = Body(),
    usr: Optional[str] = Body(None),
):
    if usr:
        user = await get_user(usr)
        if not user:
            return Response(status_code=status.HTTP_404_NOT_FOUND)
    else:
        try:
            user = await get_account_by_email(username)
            if not user:
                return Response(status_code=status.HTTP_404_NOT_FOUND)
            _ = await load_user(user.id)
            user.login(password)
        except Exception as exc:
            return Response(status_code=status.HTTP_401_UNAUTHORIZED, content=str(exc))


    access_token = login_manager.create_access_token(data=dict(sub=user.id))
    login_manager.set_cookie(response, access_token)
    return {"access_token": access_token, "token_type": "bearer"}


@core_app.post("/api/v1/logout")
async def logout(response: Response):
    response.delete_cookie("access-token")
    return {"status": "success"}


@core_app.post("/api/v1/register")
async def register_endpoint(
    data: createUser, response: Response
) -> dict[str, str] | Response:
    if data.password != data.password_repeat:
        return JSONResponse(
            {
                "detail": [
                    {
                        "loc": ["body", "password_repeat"],
                        "msg": "passwords do not match",
                    }
                ]
            },
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        )
    try:
        user = await create_user(data)
        access_token = login_manager.create_access_token(data=dict(sub=user.id))
        login_manager.set_cookie(response, access_token)
        return {"access_token": access_token, "token_type": "bearer", "usr": user.id}
    except Exception as exc:
        return JSONResponse(
            {"detail": [{"loc": ["body", "error"], "msg": str(exc)}]},
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        )
