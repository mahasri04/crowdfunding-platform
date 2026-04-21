from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class CampaignCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=255)
    goal: float = Field(..., gt=0)
    deadline: datetime


class CampaignOut(BaseModel):
    id: int
    title: str
    goal: float
    pledged: float
    deadline: datetime
    status: str

    model_config = ConfigDict(from_attributes=True)


class PledgeCreate(BaseModel):
    user_name: str = Field(..., min_length=1, max_length=255)
    amount: float = Field(..., gt=0)


class PledgeOut(BaseModel):
    id: int
    campaign_id: int
    user_name: str
    amount: float

    model_config = ConfigDict(from_attributes=True)


class RefundSummary(BaseModel):
    campaign_id: int
    total_refunded: float
