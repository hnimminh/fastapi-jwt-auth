from time import time
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session

from config import MYSQL_USER, MYSQL_PASSWORD, MYSQL_DB, MYSQL_HOST, MYSQL_PORT
from utils import logger


if not (MYSQL_USER and MYSQL_PASSWORD and MYSQL_HOST and MYSQL_DB):
    logger.critical('module=auth, space=database, error=Please specify MYSQL_USER, MYSQL_PASSWORD, MYSQL_HOST, MYSQL_DB')
    exit()

DATABASE_URL = f'mysql+pymysql://{MYSQL_USER}:{MYSQL_PASSWORD}@{MYSQL_HOST}:{MYSQL_PORT}/{MYSQL_DB}'

# create a sql engine instance
Engine = create_engine(DATABASE_URL, pool_pre_ping=True)

# create a declarativeMeta instance
Base = declarative_base()

# create SessionLocal class from sessionmaker factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=Engine)


class AccountBase(Base):
    __tablename__ = 'accounts'
    id = Column(Integer, primary_key=True, index=True)
    # even the is rft limit email max lenght is 254 but below is valid as well
    # 64 for the username + 1 for @ + 254 for the domain name, safer to support this point.
    # https://dba.stackexchange.com/questions/37014/in-what-data-type-should-i-store-an-email-address-in-database
    email = Column(String(320), unique=True, index=True)
    # bcrypt output max lenght is 60 bytes
    # string type is good enough with compare hashes on python layer
    hpassword = Column(String(60))


def get_account(dbsess: Session, email: str):
    return dbsess.query(AccountBase).filter(AccountBase.email == email).first()


def create_account(dbsess: Session, email: str, hpassword: str):
    account = AccountBase(email=email, hpassword=hpassword)
    dbsess.add(account)
    dbsess.commit()
    dbsess.refresh(account)


def update_account(dbsess: Session, account: AccountBase, hpassword: str):
    setattr(account, 'hpassword', hpassword)
    dbsess.add(account)
    dbsess.commit()
    dbsess.refresh(account)


def delete_account(db: Session, account: AccountBase):
    db.delete(account)
    db.commit()
