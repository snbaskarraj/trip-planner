from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Trip
from app.serializers import trip_to_dict

router = APIRouter(prefix="/api/share", tags=["share"])


@router.get("/{token}")
def get_shared_trip(token: str, db: Session = Depends(get_db)):
    """Read-only. No login. Possession of the token is authorization."""
    trip = db.query(Trip).filter(Trip.share_token == token).first()
    if trip is None:
        raise HTTPException(status_code=404, detail="Shared trip not found")
    return trip_to_dict(trip)
