import sqlalchemy as sa
from sqlalchemy import String, Text, ForeignKey
from sqlalchemy.orm import relationship

from models.base import Base


class Recipe(Base):
    __tablename__ = "recipes"

    meal_id = sa.Column(String(10), ForeignKey("meals.id"), primary_key=True)
    instructions = sa.Column(Text)       # maps to CLOB in Oracle
    youtube_url = sa.Column(String(500))
    meal = relationship("Meal", back_populates="recipe")
