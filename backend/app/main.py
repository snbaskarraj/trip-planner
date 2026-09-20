from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.config import settings
from app.database import Base, engine
from app.routers import activities, conditions, days, share, trips
from app.validation import DomainError

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Trip Planner", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[o.strip() for o in settings.cors_origins.split(",") if o.strip()],
    allow_origin_regex=r"https://.*\.vercel\.app",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(DomainError)
async def domain_error_handler(_request, exc: DomainError):
    return JSONResponse(
        status_code=400,
        content={"detail": exc.message, "code": exc.code},
    )


@app.get("/health")
def health():
    return {"status": "ok"}


app.include_router(trips.router)
app.include_router(days.router)
app.include_router(activities.router)
app.include_router(share.router)
app.include_router(conditions.router)
