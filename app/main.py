from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .database import engine, Base
from .routers import auth, user, server, channel, websocket

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Chat Application API",
    description="Discord-like chat application with JWT authentication",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Change this to specific origins in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router)
app.include_router(user.router)
app.include_router(server.router)
app.include_router(channel.router)
app.include_router(websocket.router)


@app.get("/")
def root():
    return {
        "message": "Welcome to Chat Application API",
        "docs": "/docs",
        "redoc": "/redoc"
    }


@app.get("/health")
def health_check():
    return {"status": "healthy"}
