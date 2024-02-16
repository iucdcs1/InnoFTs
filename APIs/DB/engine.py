import os

from dotenv import load_dotenv
from sqlalchemy import BigInteger, Column, Integer, String, Boolean, PrimaryKeyConstraint, UniqueConstraint, \
    ForeignKeyConstraint, ForeignKey, Table, Time
from sqlalchemy.ext.asyncio import AsyncAttrs, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase, relationship

load_dotenv(".env")
url = os.getenv("SQLALCHEMY_URL")

engine = create_async_engine(url, echo=True)

async_session = async_sessionmaker(engine)


class Base(AsyncAttrs, DeclarativeBase):
    pass


passenger_routes = Table('passenger_routes', Base.metadata,
                         Column('user_id', Integer, ForeignKey('users.id')),
                         Column('route_id', Integer, ForeignKey('routes.id')),
                         Column('amount_of_passengers', Integer, nullable=False))


class User(Base):
    __tablename__ = "users"

    id = Column(Integer)
    telegram_id = Column(BigInteger, nullable=False)
    username = Column(String(100), nullable=False)
    is_admin = Column(Boolean, default=False)

    __table_args__ = (
        PrimaryKeyConstraint('id', name='user_pk'),
        UniqueConstraint('telegram_id')
    )

    routes = relationship("Route", secondary=passenger_routes, back_populates="users")


class Route(Base):
    __tablename__ = "routes"

    id = Column(Integer)
    driver_id = Column(Integer)

    users = relationship("User", secondary=passenger_routes, back_populates="routes")

    place_from_id = Column(Integer)
    place_to_id = Column(Integer)

    available_places = Column(Integer)

    cost = Column(Integer)

    date_field = Column(String(20))
    time_field = Column(Time)

    __table_args__ = (
        PrimaryKeyConstraint('id', name='route_pk'),
        ForeignKeyConstraint(['place_from_id'], ['places.id']),
        ForeignKeyConstraint(['place_to_id'], ['places.id'])
    )


class Place(Base):
    __tablename__ = "places"

    id = Column(Integer)
    name = Column(String(100), nullable=False)

    __table_args__ = (
        PrimaryKeyConstraint('id', name='place_pk'),
        UniqueConstraint('name')
    )


async def db_engine_start():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
