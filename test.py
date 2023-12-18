from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
import pymysql

from datetime import datetime, timedelta
from typing import Annotated

from fastapi import Depends, FastAPI, HTTPException, status, Request
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from passlib.context import CryptContext
from pydantic import BaseModel

from profile_resources import ProfileResource
from login_resources import LoginResource

import uvicorn

# to get a string like this run:
# openssl rand -hex 32
SECRET_KEY = "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30


fake_users_db = {
    "Yuxiao": {
        "username": "yuxiao",
        "full_name": "Yuxiao Fei",
        "email": "yf2633@example.com",
        "hashed_password": "$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW",
        "disabled": False,
    }
}

# connection = pymysql.connect(
#     host='localhost',
#     user='your_username',
#     password='your_password',
#     database='your_database_name',
#     cursorclass=pymysql.cursors.DictCursor
# )


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    uni: str | None = None


class User(BaseModel):
    uni: str
    email: str | None = None
    full_name: str | None = None
    disabled: bool | None = None


class UserInDB(User):
    hashed_password: str


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

app = FastAPI()

templates = Jinja2Templates(directory="templates")


def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password):
    return pwd_context.hash(password)


def get_user(db, username: str):
    if username in db:
        user_dict = db[username]
        return UserInDB(**user_dict)


def authenticate_user(fake_db, username: str, password: str):
    user = get_user(fake_db, username)
    if not user:
        return False
    if not verify_password(password, user.hashed_password):
        return False
    return user


def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


async def get_current_user(token: Annotated[str, Depends(oauth2_scheme)]):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except JWTError:
        raise credentials_exception
    user = get_user(fake_users_db, username=token_data.username)
    if user is None:
        raise credentials_exception
    return user


async def get_current_active_user(
    current_user: Annotated[User, Depends(get_current_user)]
):
    if current_user.disabled:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user


# @app.post("/create_user/", response_model=User)
# async def create_user(user: User):
#     # 插入新用户
#     with connection.cursor() as cursor:
#         sql = "INSERT INTO users (username, email, full_name, disabled) VALUES (%s, %s, %s, %s)"
#         cursor.execute(sql, (user.username, user.email, user.full_name, user.disabled))
#         connection.commit()
#
#     return user

@app.get("/login", response_class=HTMLResponse)
async def login_form(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

@app.post("/login", response_model=Token)
async def login_for_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()]
):
    # user = authenticate_user(fake_users_db, form_data.username, form_data.password)
    print(form_data.username, form_data.password)
    user = LoginResource.get_user_by_uni(form_data.username)
    if user and user['password'] != form_data.password:
        return templates.TemplateResponse("login.html", {"message": "Invalid username or password"})

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user['uni']}, expires_delta=access_token_expires
    )
    redirect_url = f"/profile/{user['uni']}"
    response = RedirectResponse(url=redirect_url)
    response.set_cookie(key="access_token", value=access_token, httponly=True)
    # print(1)
    return response
    # return {"access_token": access_token, "token_type": "bearer"}


# @app.route("/profile/{uni}", methods=["GET", "POST"])
# async def profile_form(request: Request, uni: str):
#     if request.method == "POST":
#         access_token = request.cookies.get("access_token")
#         if not access_token:
#             return RedirectResponse(url="/login")
#
#         result = ProfileResource.get_profile_by_uni(uni)
#         return templates.TemplateResponse("profile.html", {"request": request, "user_info": result})
#
#     elif request.method == "GET":
#         result = ProfileResource.get_profile_by_uni(uni)
#         return templates.TemplateResponse("profile.html", {"request": request, "user_info": result})


@app.post("/profile/{uni}", response_class=HTMLResponse)
async def profile_form(request: Request, uni: str):
    access_token = request.cookies.get("access_token")
    if not access_token:
        return RedirectResponse(url="/login")

    result = ProfileResource.get_profile_by_uni(uni)
    return templates.TemplateResponse("profile.html", {"request": request, "user_info": result})

#
@app.get("/profile/{uni}", response_class=HTMLResponse)
async def profile_form(request: Request, uni: str):
    access_token = request.cookies.get("access_token")
    if not access_token:
        return RedirectResponse(url="/login")

    result = ProfileResource.get_profile_by_uni(uni)
    return templates.TemplateResponse("profile.html", {"request": request, "user_info": result})


@app.get("/users/me/", response_model=User)
async def read_users_me(
    current_user: Annotated[User, Depends(get_current_active_user)]
):
    return current_user


@app.get("/users/me/items/")
async def read_own_items(
    current_user: Annotated[User, Depends(get_current_active_user)]
):
    return [{"item_id": "Foo", "owner": current_user.username}]


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8011)