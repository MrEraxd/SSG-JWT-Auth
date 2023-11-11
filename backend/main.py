from fastapi import FastAPI, Response, Request, HTTPException, Depends
from jose import jwt
from time import time
from typing import Annotated
from pydantic import BaseModel

app = FastAPI(docs_url="/api/docs", openapi_url="/api/docs/openapi.json")


# Definition of user in database it is different
# because we will add permissions to this model
class User(BaseModel):
    username: str
    password: str
    permissions: list[str]


# Definition of data that will come from FE
class LoginUser(BaseModel):
    username: str
    password: str


# This is the same key that you are using in nginx
# it will be used to create and check JWT
JWT_SECRET = "ultra_secret_key"

# Name of the cookie that JWT will be stored at
# this is the same as in nginx
COOKIE_NAME = "AuthToken"

# Exipiry time for token
EXPIRY_TIME_IN_MINUTES = 10

# Base user information, normally this would be stored in database
db_user: User = {
    "username": "kkotfisz",
    "password": "hashed_password",
    "permissions": ["p_orders_r", "p_orders_w"],
}


# Generate JWT with requierd claims
async def generate_token(user: User):
    baseJWT = {
        "sub": user["username"],
        "iat": int(time()),
        "exp": int(time() + EXPIRY_TIME_IN_MINUTES * 60),
    }

    for permission in user["permissions"]:
        # We have to set any non zero value
        baseJWT[permission] = 1

    return jwt.encode(
        baseJWT,
        JWT_SECRET,
    )


# This function should validate token
# using secret key and check expiry date
# If token is valid and not expired return
# decoded token otherwise throw an error
async def validate_token(request: Request):
    try:
        return jwt.decode(request.cookies.get(COOKIE_NAME), JWT_SECRET)
    except:
        raise HTTPException(status_code=401, detail="Provide valid JWT")


# For now we only extract username from JWT
# we are working on assumption that permissions
# are claims with `p_` prefix
async def get_user(claims: Annotated[str, Depends(validate_token)]):
    permissions = []

    for claim in claims:
        if "p_" in claim:
            permissions.append(claim)

    return {"username": claims["sub"], "permissions": permissions}


# This is class that will test if user have required
# permission for this path, in the constructor we assign
# name of the required permission and then raise exception
# Before checking permission we will validate token to be
# sure it is not expired/modified
class PermissionChecker:
    def __init__(
        self,
        requierd_permissions: list[str],
    ):
        self.requierd_permissions = requierd_permissions

    def __call__(
        self,
        auth_token: Annotated[dict | None, Depends(validate_token)],
    ):
        for required_permission in self.requierd_permissions:
            if required_permission not in auth_token:
                raise HTTPException(status_code=403, detail="Forbidden")


# This is path when we will generate access token, this is the
# place when all authentication will happen, we should add here
# checks for user existance password correctnes and it will
# return user data later on we will add permissions
@app.post("/api/auth/login")
async def login(response: Response, credentials: LoginUser):
    if (
        credentials.username != db_user["username"]
        or credentials.password != db_user["password"]
    ):
        raise HTTPException(status_code=400, detail="Wrong credentials")

    response.set_cookie(
        key=COOKIE_NAME, value=await generate_token(db_user), httponly=True
    )

    return {"username": db_user["username"], "permissions": db_user["permissions"]}


# On logout we just have to remove cookie
@app.post("/api/auth/logout")
async def logout(response: Response):
    response.delete_cookie(key=COOKIE_NAME)


# Path that will be availabe only after presenting valid JWT
# it does not check for any specific permissions and returns
# logged in user username
@app.get("/api/auth/me", dependencies=[Depends(validate_token)])
async def logged_user(user: Annotated[list[str], Depends(get_user)]):
    return user


# User will be able to get data from this endpoint only
# after presenting valid JWT with `p_orders_r` claim
@app.get(
    "/api/orders",
    dependencies=[Depends(PermissionChecker(["p_orders_r"]))],
)
async def orders():
    return {"orders": ["order1", "order2"]}
