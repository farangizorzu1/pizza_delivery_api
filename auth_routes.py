# from calendar import firstweekday
# from ctypes import HRESULT
from http.client import responses

# from encodings.idna import ace_prefix

from fastapi import APIRouter, status, Depends
from schemas import SignUpModel, LoginModel
from  database import Session, engine
from models import User
from fastapi.exceptions import HTTPException
from  werkzeug.security import generate_password_hash, check_password_hash
from  fastapi_jwt_auth import AuthJWT
from fastapi.encoders import  jsonable_encoder
session=Session(bind=engine)

auth_router=APIRouter(
	prefix="/auth",
    tags=['AUTH'])

@auth_router.get("/")


async def hello():
    """
            ## Simple hello world
    """



@auth_router.post("/signup",response_model=SignUpModel, status_code=status.HTTP_201_CREATED)
async  def signup(user:SignUpModel):
    """
        ## Creat a user
           This requres the folllowing
        ---
            "username":"Farangiz",
            "email":"badbadlucks914@gmail.com",
            "password":"password",
            "is_active": True

        ---


        """
    db_email=session.query(User).filter(User.email==user.email).first()

    if db_email is not None:
        return HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
        detail="USER with the  email already exist")
    db_username=session.query(User).filter(User.usename==user.username).first()
    if db_email is not None:
        return HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
        detail="user with the user  already exist")
    new_user=User(
        username=user.username,
        email=user.email,
        password=generate_password_hash(user.password),
        is_active=user.is_active,
        is_staff=user.is_staff

    )
    session.add(new_user)
    session.commit()
    return new_user


#login route

@auth_router.post("/login ", status_code=200)
async  def login(user:LoginModel, Authorize:AuthJWT=Depends()):
    """
            ## Login in user
            ---
                "username":"Farangiz",
                "password":"Password"
            and returns token pair "access and refresh
            ---


            """

    db_user=session.query(User).filter(User.username==user.username).first()
    if db_user and check_password_hash(db_user.password, user.password):
        access_token=Authorize.create_access_token(subject=user.username)
        refresh_token=Authorize.create_refresh_token(subject=user.username)

        response={
            "access":access_token,
            "refresh":refresh_token

        }
        return jsonable_encoder(response)
        # return {"access_token":access_token, "refresh_token":refresh_token}
    raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                        detail="Invalid or Password")



                    #refreshing tokin
@auth_router.get("/refresh")
async def refresh(Authorize:AuthJWT=Depends()):
    """
            ## Refreshing  a  fresh token. It requires an access Token.

            ---
               "Heelooo"

            ---


            """
    try:
        Authorize.jwt_refresh_token_required()
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="Invalid or Expired token")

    concurrent_user=Authorize.get_jwt_subject()

    access_token=Authorize.create_access_token(subject=concurrent_user)
    return {
        "access_token":access_token
    }







