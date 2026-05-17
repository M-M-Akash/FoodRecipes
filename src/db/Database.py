from sqlalchemy import String
from sqlalchemy.orm import DeclarativeBase

from sqlalchemy_utils import UUIDType
from sqlalchemy.dialects.oracle import TIMESTAMP
import uuid
import sqlalchemy as sa



# Create a SQLAlchemy engine


class Base(DeclarativeBase):
    pass


class FoodCategory(Base):
    __tablename__ = 'food'

    # Pass `binary=False` to fallback to CHAR instead of BINARY
    id = sa.Column(
        UUIDType(binary=False),
        primary_key=True,
        default=uuid.uuid4
    )
    name = sa.Column(
        String(30)
    )
    reference = sa.Column(
        String(30)
    )
    created_at = sa.Column(
        TIMESTAMP(0)
    )
    updated_at = sa.Column(
        TIMESTAMP(0)
    )