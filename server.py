import sys
import hashlib
import re
import asyncio
import aiopg

import uvicorn
import jwt
from pydantic import BaseModel
from fastapi import FastAPI, Response, status
from fastapi.encoders import jsonable_encoder
from fastapi.middleware.cors import CORSMiddleware


PG_HOST = "localhost"
PG_DATABASE = "test_db"
PG_USER = "root"
PG_PASSWORD = "root"


SECERT_KEY = "SECERT_KEY"
ALGORITHM ="HS256"
ACCESS_TOKEN_EXPIRES_MINUTES = 800


app = FastAPI()

origins = {
    "http://localhost",
    "http://localhost:3000",
}

app.add_middleware(
   CORSMiddleware,
    allow_origins = origins,
    allow_credentials =True,
    allow_methods = ["*"],
    allow_headers= ["*"],
)

class RegisterItem(BaseModel):
    username: str
    password: str
    name: str


class LoginItem(BaseModel):
    username: str
    password: str

class AuthorizedItem(BaseModel):
    username: str
    token: str

class Token(BaseModel):
    username: str
    id: int


app.tokens : dict[str, Token] = {}


def hash_func(s: str):
    res = hashlib.md5(s.encode('utf-8')).hexdigest()
    return res

def check_str(s: str) -> bool:
    if (len(s) > 50 or s.find(";") >= 0
            or re.findall(r"(create|drop|select|insert|update|delete)", s)):
        return False
    return True


dsn = f'dbname={PG_DATABASE} user={PG_USER} password={PG_PASSWORD} host={PG_HOST}'

async def query(query: str):
    async with aiopg.connect(dsn) as con:
        async with con.cursor() as cursor:
            await cursor.execute(query)
            result = []
            async for row in cursor:
                result.append(row)
            return result


@app.get("/")
def read_root():
    # response.status_code = status.HTTP_201_CREATED
    return {"Hello": "World"}


@app.post("/user/register")
async def user_register(r: RegisterItem):
    data = jsonable_encoder(r)
    username_ = data["username"]
    password_hash_ = hash_func(data["password"])
    name_ = data["name"]

    if not check_str(username_) or not check_str(password_hash_) or not check_str(name_):
        return {"message": "possible SQL injection in parameters"}

    result = await asyncio.gather(
        query(f"""
        select *
        from test_schema.backend_api_register_user(
            username_ := '{username_}',
            password_hash_ := '{password_hash_}',
            name_ := '{name_}'
        )
        """),
    )
    first_row = result[0][0]
    d = {"password_hash": password_hash_}
    if first_row[0] == "ok":
        encoded_jwt = jwt.encode(d, SECERT_KEY, algorithm=ALGORITHM)
        app.encoded_jwt = encoded_jwt

        t = Token(username=username_, id=first_row[1])
        app.tokens[encoded_jwt] = t
        return {"token": encoded_jwt}
    else:
        return {"message": first_row[0]}


@app.post("/login")
async def login(l: LoginItem):
    data = jsonable_encoder(l)
    username_ = data["username"]
    password_hash_ = hash_func(data["password"])

    if not check_str(username_) or not check_str(password_hash_):
        return {"message": "possible SQL injection in parameters"}

    result = await asyncio.gather(
        query(f"""
        select *
        from test_schema.backend_api_login_user(
            username_ := '{username_}',
            password_hash_ := '{password_hash_}'
        )
        """),
    )
    first_row = result[0][0]
    d = {"password_hash": password_hash_}
    if first_row[0] == "ok":
        encoded_jwt = jwt.encode(d, SECERT_KEY, algorithm=ALGORITHM)
        app.encoded_jwt = encoded_jwt

        t = Token(username=username_, id=first_row[1])
        app.tokens[encoded_jwt] = t

        return {"token": encoded_jwt}
    else:
        return {"message": first_row[0]}


@app.get("/user/get/{token}")
async def user_get(token: str):
    if token not in app.tokens.keys():
        return {"message": "unknown token"}

    x = app.tokens[token]
    id = x.id
    result = await asyncio.gather(
        query(f"""
        select *
        from test_schema.backend_api_get_profile_by_id(id_ := {id})
        """),
    )
    first_row = result[0][0]
    if first_row[0] == "ok":
        return {"name": first_row[1]}
    else:
        return {"message": first_row[1]}


def receive_signal(signalNumber, frame):
    print("Received:", signalNumber)
    sys.exit()

@app.on_event("startup")
async def startup_event():
    import signal
    signal.signal(signal.SIGINT, receive_signal)


if __name__ == "__main__":
    uvicorn.run(app, port=8223, host="0.0.0.0")
