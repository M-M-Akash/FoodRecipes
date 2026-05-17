import sqlalchemy as sa
from sqlalchemy import String, ForeignKey
from sqlalchemy.orm import relationship

from models.base import Base


class Meal(Base):
    __tablename__ = "meals"

    id = sa.Column(String(10), primary_key=True)  # idMeal from API
    name = sa.Column(String(100))
    thumbnail_url = sa.Column(String(500))
    area_id = sa.Column(String(50), ForeignKey("areas.id"))
    area = relationship("Area", back_populates="meals")
    recipe = relationship("Recipe", back_populates="meal", uselist=False)
