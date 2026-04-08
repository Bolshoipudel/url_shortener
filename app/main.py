import string
import random
from contextlib import asynccontextmanager

from fastapi import FastAPI, Depends, HTTPException, Request
from fastapi.responses import RedirectResponse
from sqlalchemy import update
from sqlalchemy.orm import Session

from app.database import Base, engine, get_db
from app.models import Link
from app.schemas import ShortenRequest, ShortenResponse, StatsResponse


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(title="URL Shortener", lifespan=lifespan)

SHORT_ID_LENGTH = 6
ALPHABET = string.ascii_letters + string.digits


def generate_short_id(length: int = SHORT_ID_LENGTH) -> str:
    return "".join(random.choices(ALPHABET, k=length))


@app.post("/shorten", response_model=ShortenResponse)
def shorten(body: ShortenRequest, request: Request, db: Session = Depends(get_db)):
    short_id = generate_short_id()
    while db.query(Link).filter(Link.short_id == short_id).first():
        short_id = generate_short_id()

    link = Link(short_id=short_id, original_url=str(body.url))
    db.add(link)
    db.commit()
    db.refresh(link)

    base_url = str(request.base_url).rstrip("/")
    return ShortenResponse(short_id=short_id, short_url=f"{base_url}/{short_id}")


@app.get("/stats/{short_id}", response_model=StatsResponse)
def stats(short_id: str, db: Session = Depends(get_db)):
    link = db.query(Link).filter(Link.short_id == short_id).first()
    if not link:
        raise HTTPException(status_code=404, detail="Link not found")
    return StatsResponse(
        short_id=link.short_id, original_url=link.original_url, clicks=link.clicks
    )


@app.get("/{short_id}")
def redirect(short_id: str, db: Session = Depends(get_db)):
    link = db.query(Link).filter(Link.short_id == short_id).first()
    if not link:
        raise HTTPException(status_code=404, detail="Link not found")
    db.execute(
        update(Link).where(Link.short_id == short_id).values(clicks=Link.clicks + 1)
    )
    db.commit()
    return RedirectResponse(url=link.original_url, status_code=307)
