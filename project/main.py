from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI

from database import create_tables
from devices.router import router as frouter


@asynccontextmanager
async def lifespan(app: FastAPI):
    # await delete_tables()
    create_tables()
    yield

app = FastAPI(lifespan=lifespan)
app.include_router(frouter)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)