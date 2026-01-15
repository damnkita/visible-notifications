import random
import uuid
from contextlib import asynccontextmanager

from fastapi import FastAPI


@asynccontextmanager
async def lifespan(app: FastAPI):
    yield


app = FastAPI(lifespan=lifespan)


@app.post("/events")
async def events():
    return {"hi": 123}


@app.get("/audit/{user_id}")
async def audit(user_id: uuid.UUID):
    return random.randrange(15)
