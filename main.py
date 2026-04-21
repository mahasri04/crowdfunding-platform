from datetime import datetime, timezone

from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from app import crud, schemas
from app.database import get_db

app = FastAPI(title="Crowdfunding Platform API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def root() -> dict[str, str]:
    return {
        "message": "Crowdfunding Platform API is running.",
        "docs": "/docs",
        "health": "/health",
    }


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/campaigns/", response_model=schemas.CampaignOut, status_code=status.HTTP_201_CREATED)
def create_campaign(campaign: schemas.CampaignCreate, db: Session = Depends(get_db)) -> schemas.CampaignOut:
    now = datetime.now(timezone.utc).replace(tzinfo=None)
    if campaign.deadline.replace(tzinfo=None) <= now:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Deadline must be in the future.",
        )

    result = crud.create_campaign(db, campaign)
    return schemas.CampaignOut(
        id=result.id,
        title=result.title,
        goal=result.goal,
        pledged=result.pledged,
        deadline=result.deadline,
        status=crud.status_for_campaign(result),
    )


@app.get("/campaigns/", response_model=list[schemas.CampaignOut])
def get_campaigns(db: Session = Depends(get_db)) -> list[schemas.CampaignOut]:
    campaigns = crud.list_campaigns(db)
    return [
        schemas.CampaignOut(
            id=c.id,
            title=c.title,
            goal=c.goal,
            pledged=c.pledged,
            deadline=c.deadline,
            status=crud.status_for_campaign(c),
        )
        for c in campaigns
    ]


@app.post("/campaigns/{campaign_id}/pledge", response_model=schemas.PledgeOut, status_code=status.HTTP_201_CREATED)
def pledge(campaign_id: int, payload: schemas.PledgeCreate, db: Session = Depends(get_db)) -> schemas.PledgeOut:
    campaign = crud.get_campaign(db, campaign_id)
    if campaign is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Campaign not found.")
    try:
        pledge_row = crud.pledge_to_campaign(db, campaign, payload)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    return pledge_row


@app.post("/campaigns/{campaign_id}/refunds", response_model=schemas.RefundSummary)
def refund(campaign_id: int, db: Session = Depends(get_db)) -> schemas.RefundSummary:
    campaign = crud.get_campaign(db, campaign_id)
    if campaign is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Campaign not found.")
    try:
        total = crud.refund_expired_unfunded_campaign(db, campaign)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    return schemas.RefundSummary(campaign_id=campaign_id, total_refunded=total)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
