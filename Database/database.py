from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy import Column, Integer, Float, String, DateTime
from datetime import datetime
import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL") #Get url for database

engine = create_async_engine(DATABASE_URL) #Create engine
async_Session = sessionmaker(engine, class_AsyncSession, expire_on_commit=False) #Create session
Base = declarative_base() #Create class Base for inheritance BalanceHistory 

class BalanceHistory(Base):
    """ Create table for tracking balance history """
    __tablename__ = "balance_history"

    id = Column(Integer, primary_key=True, index=True)
    exchange = Column(String, index=True)
    amount_usd = Column(Float)
    timestamp = Column(DateTime, default=datetime.utcnow) 