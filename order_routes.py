from asyncio import start_unix_server
from http.client import HTTPException, responses
from statistics import quantiles

from  fastapi.exceptions import HTTPException
from fastapi import APIRouter, Depends, status
from fastapi.openapi.utils import status_code_ranges
from fastapi.params import Depends, Header
from sqlalchemy.sql.functions import current_user

from auth_routes import session
from database import Session, engine
from  fastapi_jwt_auth import AuthJWT
from  models import User, Order
from schemas import OrderModel, OrderStatusModel
from fastapi.encoders import jsonable_encoder


order_router=APIRouter(
	prefix="/orders",
	tags=['ORDERS'])

session=Session(bind=engine)
@order_router.get("/")
async def hello(Authorize:AuthJWT=Depends()):

    """
        ## A simple hello world route,
        This return Hello world
    """

    try:
        Authorize.jwt_required()
    except Exception as e:
        raise  HTTPException(
            status_code= status.HTTP_401_UNAUTHORIZED,
            detail="Invalid Token "

        )
    return {"message": "hello world "}

@order_router.post("/order", status_code=status.HTTP_201_CREATED)
async  def place_order(order:OrderModel, Authorize:AuthJWT=Depends()):
    """
           ## Placing an Order
           This requaristhe following
            - quantity:int
           - pizza_size:str
       """
    try:
        Authorize.jwt_required()
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid Token"

        )
    current_user=Authorize.get_jwt_subject()
    user=session.query(User).filter(User.username==current_user).first()
    new_order=Order(
        pizza_size=order.pizza_size,
        quantity=order.quantity,


    )

    new_order.user=user
    session.add(new_order)
    session.commit()

    responses={
        "pizza_size":new_order.pizza_size,
        "quantity":new_order.quantity,
        "order_status":new_order.order_status
    }
    return jsonable_encoder(responses)


@order_router.get("/orders")
async def get_orders(Authorize:AuthJWT=Depends()):
    """
    ## List all Orders
    THis list all orders made .It can be accessd by superuser


    """
    try:
        Authorize.jwt_required()
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid Token "
        )
    current_user=Authorize.get_jwt_subject()
    user=session.query(User).filter(User.username==current_user).first()
    orders=user.orders

    if user.is_staff:
        orders=session.query(Order).all()
        return jsonable_encoder(orders)
    # else:
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Are not superuser "


    )
@order_router.get("/orders/{id}")
async def get_order_by_id(id:int, Authorize:AuthJWT=Depends()):
    """
        ## Get an orders by its Id
        This gets  an order by its ID is only accessd by a superuser

        """
    try:
        Authorize.jwt_required()
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid Token "

        )
    #
    user=Authorize.get_jwt_subject()
    current_user = session.query(User).filter(User.username==user).first()

    if current_user.is_staff:
        order=session.query(Order).filter(Order.id==id).firs()
        return jsonable_encoder(order)
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="user not alowed tocarry request"

    )
@order_router.get('/user/orders')
async def get_user_orders(Authorize:AuthJWT=Depends()):
    """
        ##  Get a current  user's orders
        This list orders by the currently logged in users


        """
    try:
        Authorize.jwt_required()
        # current_user=Authorize.get_jwt_subject()
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="invalid Token "

        )
    user=Authorize.get_jwt_subject()
    current_user=session.query(User).filter(User.username==user).first()
    orders=current_user.orders
    return jsonable_encoder(orders)


@order_router.get("/user/orders/{id}/",response_model=OrderModel)
async  def get_user_order_by_id(id:int, Authorize:AuthJWT=Depends()):
    """
        ## Get a specific order by the currently loggd in user
        This return an order by ID the currenty logged in user

        """
    try:
        Authorize.jwt_required()

    except Exception  as e :
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid Token"

        )
    subject=Authorize.get_jwt_subject()
    current_user=session.query(User).filter(User.username==subject).first()
    orders=current_user.orders
    for o in orders:
        if o.id==id:
            return o


    raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                        detail="NO order with such id ")


                    #--update Router--order------
@order_router.put("/orders/{id}/")
async  def update_order(id:int, order:OrderModel, Authorize:AuthJWT=Depends()):
    """
        ## Updating an oreder
        This update an order and requires the following fields
        - quantity:int
        - pizza_size:str



        """
    try:
        Authorize.jwt_required()
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid Token "

        )
    order_to_update=session.query(Order).filter(Order.id==id).first() #obyekt yaratilayapdi

    order_to_update.quantity=order.quantity
    order_to_update.pizza_size=order.pizza_size
    session.commit()
    response = {
        "id": order_to_update.id,
        "quantity": order_to_update.quantiy,
        "pizza_size": order_to_update.pizza_size,
        "order_status": order_to_update.order_status,

    }
    return jsonable_encoder(order_to_update)



@order_router.patch("/order/update/{id}/")
async def ipdate_order_status(id:int,
    order:OrderStatusModel,
    Authorize:AuthJWT=Depends()):
    """
        ## Updating an order's status
        This is for updating a orders status and requires order_status

        """
    try:
        Authorize.jwt_required()
    except Exception as e :
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid Token"

        )
    username=Authorize.get_jwt_subject()
    current_user=session.query(User).filter(User.username==username).first()
    if current_user.is_staff:
        order_to_update=session.query(Order).filter(Order.id==id).first()


        order_to_update.order_status=order.order_status
        session.commit()
        response={
            "id":order_to_update.id,
            "quantity":order_to_update.quantiy,
            "pizza_size":order_to_update.pizza_size,
            "order_status":order_to_update.order_status,


        }
        return jsonable_encoder(response)

@order_router.delete("/orders/{id}/", status_code=status.HTTP_204_NO_CONTENT)
async def delete_order(id:int, Authorize:AuthJWT=Depends()):
    """
        ## Delete an Order
        this deletes an order by its ID


        """

    try:
        Authorize.jwt_required()
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid Token"

        )
    order_to_delete=session.query(Order).filter(Order.id==id).first()
    session.delete(order_to_delete)
    session.commit()

    return order_to_delete

