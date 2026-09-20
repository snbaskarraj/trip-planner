from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.deps import get_day_or_404
from app.services import weather

router = APIRouter(tags=["conditions"])


@router.get("/api/days/{day_id}/conditions")
async def get_day_conditions(day_id: int, db: Session = Depends(get_db)):
    """Always 200 on vendor failure. The wrapper, not this router, talks to the vendor."""
    day = get_day_or_404(db, day_id)
    return await weather.get_day_conditions(day.trip.destination, day.date)
