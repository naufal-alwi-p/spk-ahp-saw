from fastapi import FastAPI, Depends
from sqlmodel import Session, select
from database import get_session
from model.database_model import Kriteria, Perbandingan_Kriteria
from typing import Annotated
import view

app = FastAPI(
    docs_url=None,
    redoc_url=None,
    openapi_url=None
)

SessionDatabase = Annotated[Session, Depends(get_session)]

@app.get("/")
def dashboard():
    return view.dashboard()
