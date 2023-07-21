from typing import Any, List

from fastapi import FastAPI, Depends, Form, Cookie
from fastapi.responses import Response
from fastapi.requests import Request
from fastapi.security import OAuth2PasswordBearer
from jose import jwt
import json
from sqlalchemy.orm import Session
from . import database
from fastapi.exceptions import HTTPException
from .flowers_repository import FlowerRequest, FlowersRepository
from .users_repository import UserRequest, UserResponse, UsersRepository
from .purchases_repository import PurchasesRepository, PurchaseResponse

app = FastAPI()

database.Base.metadata.create_all(bind=database.engine)

purchases_repository = PurchasesRepository()
flowers_repository = FlowersRepository()
users_repository = UsersRepository()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")


def create_access_token(user_id):
    body = {"user_id": user_id}
    token = jwt.encode(body, "flower", algorithm="HS256")
    return token


def decode_access_token(token):
    data = jwt.decode(token, "flower", algorithms=["HS256"])
    return data["user_id"]


def get_cart_user_active(request: Request, token: str = Depends(oauth2_scheme)):
    user_cart = request.cookies.get("cart")
    user_cart_json = json.loads(user_cart)
    new_cart = []
    for t in user_cart_json:
        for i, j in t.items():
            if i == token:
                new_cart.append(j)
            break
    return new_cart


def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_current_active_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    user_id = decode_access_token(token)
    user = users_repository.get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid user token")
    return user


@app.post("/signup")
def signup(user: UserRequest, db: Session = Depends(get_db)):
    users_repository.create_user(db, user)
    return {"user-successful":"created"}


@app.post("/login")
def login(username: str = Form(...), password: str = Form(...), db: Session = Depends(get_db)):
    user = users_repository.get_user_by_username(db, username)
    if not user or user.password != password:
        raise HTTPException(status_code=400, detail="Incorrect email or password")
    token = create_access_token(user.id)
    return {"access_token": token, "type": "bearer"}


@app.get("/profile", response_model=UserResponse)
def profile(current_user: UserRequest = Depends(get_current_active_user)):
    return current_user


@app.get("/flowers")
def flowers_get(db: Session = Depends(get_db)):
    return flowers_repository.get_all(db)


@app.post("/flowers")
def flowers_post(flower: FlowerRequest, db: Session = Depends(get_db)):
    flowers_repository.create_flower(db, flower)
    return {"flower-was-successful-added": flower}


@app.post("/cart/items")
def cart_items_post(flower_id: int = Form(...), token: str = Depends(oauth2_scheme), cart: str = Cookie(default="[]"),
                    db: Session = Depends(get_db)):
    cart_json = json.loads(cart)
    flower = flowers_repository.get_flower_by_id(db, flower_id)
    if flower:
        cart_json.append({token: flower.id})
        new_cart = json.dumps(cart_json)
        response = Response('{"msg":"The flower has been successfully added to the basket"}', status_code=200)
        response.set_cookie(key="cart", value=new_cart)
        return response
    return HTTPException(status_code=404, detail="The flower do not found")


@app.get("/cart/items")
def cart_items(request: Request, token: str = Depends(oauth2_scheme), new_cart: list = Depends(get_cart_user_active),
               db: Session = Depends(get_db)):
    flowers = []
    total_cost = 0
    for flower_id in new_cart:
        flower = flowers_repository.get_flower_by_id(db, flower_id)
        flowers.append(flower)
        total_cost += flower.cost
    return {"Cart Flowers": flowers, "Total cost": total_cost}


@app.post("/purchases")
def purchases(request: Request, response: Response, flower_id: int = Form(...), token: str = Depends(oauth2_scheme),
              db: Session = Depends(get_db)):
    if flower_id:
        users_cart = request.cookies.get("cart")
        new_cart = json.loads(users_cart)
        length_before = len(new_cart)
        is_valid = False
        for i in new_cart:
            if flower_id in i.values():
                is_valid = True
        if is_valid:
            for index, flower in enumerate(new_cart):
                for k, v in flower.items():
                    if k == token and v == flower_id:
                        del new_cart[index]
                    break
                if len(new_cart) != length_before:
                    break

            response.delete_cookie(key="cart")

            cart = json.dumps(new_cart)
            response.set_cookie(key="cart", value=cart)
            purchases_repository.save_purchases(db,
                                                PurchaseResponse(user_id=decode_access_token(token),
                                                                 flower_id=flower_id))
            return {"Message": "Successful bought"}
        else:
            return HTTPException(status_code=404, detail="The flower cant found")
    return HTTPException(status_code=404, detail="The flower cant found")


@app.get("/purchases")
def purchases_get(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    user_id = decode_access_token(token)
    purchases_items = purchases_repository.get_all_user_purchases(db, user_id)
    flowers = []
    for f_id in purchases_items:
        flower = flowers_repository.get_flower_by_id(db, f_id.flower_id)
        flowers.append(flower)
    return {"purchases_id": purchases_items.all(), "flowers": flowers}


@app.get("/users/get-all")
def get_all_users(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    superuser = users_repository.get_user_by_id(db, decode_access_token(token))
    if superuser.is_superuser:
        users = users_repository.get_all_users(db)
        return users
    return HTTPException(status_code=404, detail="U are not superuser")


@app.post("/users/make-superuser")
def make_superuser(token: str = Depends(oauth2_scheme), user_id: int = Form(), db: Session = Depends(get_db)):
    superuser = users_repository.get_user_by_id(db, decode_access_token(token))
    if superuser and superuser.is_superuser:
        get_user = users_repository.get_user_by_id(db, user_id)
        if get_user:
            get_user.is_superuser = True
            user = users_repository.update_user_to_superuser(db, user_id, get_user)
            return {f"user-{user.username}":"was superuser"}
        return HTTPException(status_code=404, detail="Not user with the id")
    return HTTPException(status_code=404, detail="U are not superuser")
