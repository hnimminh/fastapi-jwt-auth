from pydantic import BaseModel, Field, root_validator, validator
from typing import Optional
from enum import Enum

from utils import check_email_format, check_password_format


class ResultEnum(str, Enum):
    passed = 'passed'
    failed = 'failed'


class GeneralRespModel(BaseModel):
    status: Optional[ResultEnum] = Field(description='result of request')
    detail: Optional[str] = Field(description='detail error description')


class TokenRespModel(GeneralRespModel):
    token: str = Field(description='session token')


def validate_email(email):
    if not check_email_format(email):
        raise ValueError('invalid email format')
    return email


def validate_password(password):
    if not check_password_format(password):
        raise ValueError('the password require length 8-32 characters, at least one letter and one number and one special characters')
    return password


class UserModel(BaseModel):
    email: str = Field('email address of user', max_length=254)
    password: str = Field('password of user', max_length=32, min_length=8)
    # validate inputs
    # not validate the password since password policy format could changed.
    _validemail = validator('email', allow_reuse=True)(validate_email)


class NewUserModel(UserModel):
    # inherit from UserModel with extra step of validate password format
    _validpassword = validator('password', allow_reuse=True)(validate_password)


class UserChangePasswordModel(BaseModel):
    email: str = Field('email address of user', max_length=254)
    current_password: str = Field('current password of user', max_length=32, min_length=8)
    new_password: str = Field('current password of user', max_length=32, min_length=8)
    # validate inputs
    # not validate the current password since password policy format could changed.
    _validemail = validator('email')(validate_email)
    _validpassword = validator('new_password')(validate_password)
