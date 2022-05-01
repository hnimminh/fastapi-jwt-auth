import traceback
import uuid
import time
from typing import Union
from fastapi import FastAPI, Request, Response, Depends, HTTPException
from fastapi.encoders import jsonable_encoder
from fastapi.security import HTTPBearer
from sqlalchemy.orm import Session

from config import _APPLICATION, _SWVERSION, _DESCRIPTION
from utils import logger, _request_uuid_ctx_var, get_request_uuid, reqinspect, get_hashed_password, verify_password, generate_jwt_token, validate_jwt_token
from schemas import GeneralRespModel, NewUserModel, UserModel, UserChangePasswordModel, TokenRespModel
from database import SessionLocal, Engine, Base, get_account, create_account, update_account, delete_account


httpapi = FastAPI(title=_APPLICATION, version=_SWVERSION, description=_DESCRIPTION, docs_url='/apidoc', redoc_url=None)

Base.metadata.create_all(bind=Engine)

def dbsession():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@httpapi.middleware('http')
async def tracking(request: Request, call_next) -> Response:
    try:
        start_time = time.time()
        request_uuid = _request_uuid_ctx_var.set(str(uuid.uuid4()))
        client_ip = request.client.host
        method = request.method.lower()
        path = request.url.path
        response = await call_next(request)
        status_code = response.status_code
        process_time = round(time.time() - start_time, 3)
        logger.info(f'module=auth, space=httpapi, request_id={get_request_uuid()}, client_ip={client_ip}, method={method}, path={path}, status_code={status_code}, process_time={process_time}')
        _request_uuid_ctx_var.reset(request_uuid)
        return response
    except:
        pass


def JWTBearer(authcredentials=Depends(HTTPBearer(scheme_name='Authorization'))):
    # a reusable middleware function for specify api
    # validate the jwt token, pass to api or raise error
    if authcredentials:
        if not authcredentials.scheme == "Bearer":
            raise HTTPException(status_code=403, detail="invalid authentication scheme")

        payload = validate_jwt_token(authcredentials.credentials)
        if not payload:
            raise HTTPException(status_code=403, detail="expired token or invalid token")

        # might add the blocklist/backlist here to cover immediate and secure case of
        # change password, deleted/suppend user, permissions ...
        return payload
    else:
        raise HTTPException(status_code=403, detail="invalid authorization")


#---------------------------------------------------------------------------------------------------------------------------
# API VIEW
#---------------------------------------------------------------------------------------------------------------------------

@httpapi.get("/health")
def health():
    return "OK"


@httpapi.post("/auth/register", response_model=GeneralRespModel, status_code=200)
def register(reqbody: NewUserModel, request: Request, response: Response, dbsess: Session = Depends(dbsession)):
    try:
        email = reqbody.email
        password = reqbody.password

        if get_account(dbsess, email):
            response.status_code, result = 409, {'status': 'failed', 'detail': 'existing user'}
            return

        hpassword = get_hashed_password(password)
        create_account(dbsess, email, hpassword)
        response.status_code, result = 200, {'status': 'passed'}
    except Exception as e:
        response.status_code, result = 500, {'status': 'failed', 'detail': 'Internal Server Error'}
        logger.error(f'module=auth, space=httpapi, request_id={get_request_uuid()}, function=user_register, exception={e}, traceback={traceback.format_exc()}')
    finally:
        logger.debug(f'module=auth, space=httpapi, request_id={get_request_uuid()}, function=user_register, request={reqinspect(request)}, body={jsonable_encoder(reqbody)}, result={result}')
        return result


@httpapi.post("/auth/login", response_model=Union[TokenRespModel, GeneralRespModel], status_code=200)
def login(reqbody: UserModel, request: Request, response: Response, dbsess: Session = Depends(dbsession)):
    try:
        email = reqbody.email
        password = reqbody.password
        _account = get_account(dbsess, email)

        if not _account:
            response.status_code, result = 404, {'status': 'failed', 'detail': 'user not found'}
            return

        if not verify_password(password, _account.hpassword):
            response.status_code, result = 403, {'status': 'failed', 'detail': 'wrong password or email address'}
            return

        token = generate_jwt_token(email)
        response.status_code, result = 200, {'status': 'passed', 'token': token}
    except Exception as e:
        response.status_code, result = 500, {'status': 'failed', 'detail': 'Internal Server Error'}
        logger.error(f'module=auth, space=httpapi, requestid={get_request_uuid()}, function=user_login, exception={e}, traceback={traceback.format_exc()}')
    finally:
        logger.debug(f'module=auth, space=httpapi, requestid={get_request_uuid()}, function=user_login, request={reqinspect(request)}, body={jsonable_encoder(reqbody)}, result={result}')
        return result


@httpapi.put("/auth/users", status_code=200, response_model=GeneralRespModel, dependencies=[Depends(JWTBearer)])
def change_password(reqbody: UserChangePasswordModel, request: Request, response: Response, dbsess: Session = Depends(dbsession), jwtpayload=Depends(JWTBearer)):
    try:
        email = reqbody.email
        current_password = reqbody.current_password
        new_password = reqbody.new_password
        jwtemail = jwtpayload.get('email')

        if email != jwtemail:
            response.status_code, result = 400, {'status': 'failed', 'detail': 'bad request'}
            return

        # use these code for this time to check if user is still active
        # but consider to use token blocklist or similar thing for deleted/logged-out user.
        _account = get_account(dbsess, email)
        if not _account:
            response.status_code, result = 404, {'status': 'failed', 'detail': 'user not found'}
            return

        if not verify_password(current_password, _account.hpassword):
            response.status_code, result = 403, {'status': 'failed', 'detail': 'current password is not corect'}
            return

        hpassword = get_hashed_password(new_password)
        update_account(dbsess, _account, hpassword)
        response.status_code, result = 200, {'status': 'passed'}
    except Exception as e:
        response.status_code, result = 500, {'status': 'failed', 'detail': 'Internal Server Error'}
        logger.error(f'module=auth, space=httpapi, request_id={get_request_uuid()}, function=change_password, exception={e}, traceback={traceback.format_exc()}')
    finally:
        logger.debug(f'module=auth, space=httpapi, request_id={get_request_uuid()}, function=change_password, request={reqinspect(request)}, body={jsonable_encoder(reqbody)}, result={result}')
        return result


@httpapi.delete("/auth/users", status_code=200, response_model=GeneralRespModel, dependencies=[Depends(JWTBearer)], include_in_schema=False)
def delete_user(reqbody: UserModel, request: Request, response: Response, dbsess: Session = Depends(dbsession), jwtpayload=Depends(JWTBearer)):
    try:
        email = reqbody.email
        password = reqbody.password
        jwtemail = jwtpayload.get('email')

        if email != jwtemail:
            response.status_code, result = 400, {'status': 'failed', 'detail': 'bad request'}
            return

        _account = get_account(dbsess, email)
        if not _account:
            response.status_code, result = result = 200, {'status': 'passed'}
            return

        if not verify_password(password, _account.hpassword):
            response.status_code, result = 403, {'status': 'failed', 'detail': 'password is not corect'}
            return

        delete_account(dbsess, _account)
        response.status_code, result = 200, {'status': 'passed'}
    except Exception as e:
        response.status_code, result = 500, {'status': 'failed', 'detail': 'Internal Server Error'}
        logger.error(f'module=auth, space=httpapi, request_id={get_request_uuid()}, function=delete_user, exception={e}, traceback={traceback.format_exc()}')
    finally:
        logger.debug(f'module=auth, space=httpapi, request_id={get_request_uuid()}, function=delete_user, request={reqinspect(request)}, body={jsonable_encoder(reqbody)}, result={result}')
        return result
