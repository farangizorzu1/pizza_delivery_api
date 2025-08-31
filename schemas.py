from typing import Optional
from pydantic import BaseModel


class SignUpModel(BaseModel):
    id:Optional[int]
    username:str
    email:str
    password:str
    is_staff:Optional[bool]
    is_active:Optional[bool]
    class Config:
        orm_mode=True
        schema_extra={
            "example": {
                "username": "Farangiz",
                "email": "badbadluck914@gmail.com",
                "password": "password",
                "is_staff": False,
                "is_active": True
            }
        }
class Settings(BaseModel):
    authjwt_secrets_key:str="e813772b2fc850313f3a0f42ec5e11bea4217e47055de237b050afebf1a0054b"


class LoginModel(BaseModel):
    username:str
    password:str

class OrderModel(BaseModel):
    id:Optional[int]
    quantity:int
    order_status:Optional[str]
    pizza_size:Optional[str]
    user_id:Optional[int]

    class Config:
        orm_mode=True
        schema_extra={
            "example": {
                "quantity": 2,
                "pizza_size": "LARGE"


            }
        }

class OrderStatusModel(BaseModel):
    order_status:Optional[str]="PENDING"
    class Config:
        orm_mode=True
        schema_extra={
            "example":{

                "oreder_status":"PENDING"
            }

        }


