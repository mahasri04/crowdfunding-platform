from datetime import datetime, timezone

from sqlalchemy.orm import Session

from app import models, schemas


def _campaign_status(campaign: models.Campaign) -> str:
    now = datetime.now(timezone.utc).replace(tzinfo=None)
    if campaign.pledged >= campaign.goal:
        return "funded"
    if now > campaign.deadline:
        return "expired_unfunded"
    return "active"


def create_campaign(db: Session, campaign: schemas.CampaignCreate) -> models.Campaign:
    campaign_db = models.Campaign(
        title=campaign.title,
        goal=campaign.goal,
        pledged=0,
        deadline=campaign.deadline.replace(tzinfo=None),
    )
    db.add(campaign_db)
    db.commit()
    db.refresh(campaign_db)
    return campaign_db


def list_campaigns(db: Session) -> list[models.Campaign]:
    return db.query(models.Campaign).order_by(models.Campaign.id.desc()).all()


def get_campaign(db: Session, campaign_id: int) -> models.Campaign | None:
    return db.query(models.Campaign).filter(models.Campaign.id == campaign_id).first()


def pledge_to_campaign(
    db: Session, campaign: models.Campaign, pledge: schemas.PledgeCreate
) -> models.Pledge:
    now = datetime.now(timezone.utc).replace(tzinfo=None)
    if now > campaign.deadline:
        raise ValueError("Campaign deadline has passed; pledges are closed.")
    if campaign.pledged >= campaign.goal:
        raise ValueError("Campaign is already fully funded.")
    if campaign.pledged + pledge.amount > campaign.goal:
        raise ValueError("Pledge exceeds campaign goal and would overfund.")

    pledge_db = models.Pledge(
        campaign_id=campaign.id,
        user_name=pledge.user_name,
        amount=pledge.amount,
    )
    campaign.pledged += pledge.amount
    db.add(pledge_db)
    db.commit()
    db.refresh(pledge_db)
    db.refresh(campaign)
    return pledge_db


def refund_expired_unfunded_campaign(db: Session, campaign: models.Campaign) -> float:
    now = datetime.now(timezone.utc).replace(tzinfo=None)
    if now <= campaign.deadline:
        raise ValueError("Campaign has not expired yet.")
    if campaign.pledged >= campaign.goal:
        raise ValueError("Campaign met its goal; refunds are not allowed.")

    pledges = db.query(models.Pledge).filter(models.Pledge.campaign_id == campaign.id).all()
    total = sum(p.amount for p in pledges)
    for pledge in pledges:
        db.delete(pledge)
    campaign.pledged = 0
    db.commit()
    db.refresh(campaign)
    return total


def status_for_campaign(campaign: models.Campaign) -> str:
    return _campaign_status(campaign)
