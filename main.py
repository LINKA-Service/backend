from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import auth, groups, messages, users, websocket
from app.db.redis import close_redis, get_redis


@asynccontextmanager
async def lifespan(app: FastAPI):
    await get_redis()
    yield
    await close_redis()


app = FastAPI(title="LINKA Backend API", version="0.1.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix="/api/auth", tags=["auth"])
app.include_router(users.router, prefix="/api/users", tags=["users"])
app.include_router(groups.router, prefix="/api/groups", tags=["groups"])
app.include_router(messages.router, prefix="/api/messages", tags=["messages"])
app.include_router(websocket.router, prefix="/api/ws", tags=["websocket"])


@app.get("/")
async def root():
    return {"message": "LINKA Backend API"}


@app.get("/health")
async def health():
    return {"status": "healthy"}
