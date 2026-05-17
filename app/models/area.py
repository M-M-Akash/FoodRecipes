import sqlalchemy as sa
from sqlalchemy import String
from sqlalchemy.orm import relationship

from models.base import Base


class Area(Base):
    __tablename__ = "areas"

    id = sa.Column(String(50), primary_key=True)  # strArea e.g. "Mexican"
    meals = relationship("Meal", back_populates="area")
