from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from app.database import Base


class Campaign(Base):
    __tablename__ = "campaigns"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    goal = Column(Float, nullable=False)
    pledged = Column(Float, nullable=False, default=0)
    deadline = Column(DateTime, nullable=False)

    pledges = relationship("Pledge", back_populates="campaign", cascade="all, delete-orphan")


class Pledge(Base):
    __tablename__ = "pledges"

    id = Column(Integer, primary_key=True, index=True)
    campaign_id = Column(Integer, ForeignKey("campaigns.id"), nullable=False, index=True)
    user_name = Column(String, nullable=False)
    amount = Column(Float, nullable=False)

    campaign = relationship("Campaign", back_populates="pledges")
