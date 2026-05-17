from sqlalchemy import String, Text, ForeignKey
from sqlalchemy.orm import DeclarativeBase, relationship

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


class Area(Base):
    __tablename__ = 'areas'

    id = sa.Column(String(50), primary_key=True)   # strArea e.g. "Mexican"
    meals = relationship("Meal", back_populates="area")


class Meal(Base):
    __tablename__ = 'meals'

    id = sa.Column(String(10), primary_key=True)   # idMeal from API
    name = sa.Column(String(100))
    thumbnail_url = sa.Column(String(500))
    area_id = sa.Column(String(50), ForeignKey('areas.id'))
    area = relationship("Area", back_populates="meals")
    recipe = relationship("Recipe", back_populates="meal", uselist=False)


class Recipe(Base):
    __tablename__ = 'recipes'

    meal_id = sa.Column(String(10), ForeignKey('meals.id'), primary_key=True)
    instructions = sa.Column(Text)        # maps to CLOB in Oracle
    youtube_url = sa.Column(String(500))
    meal = relationship("Meal", back_populates="recipe")