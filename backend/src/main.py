from fastapi import FastAPI, Request, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from .database.session import engine
from .models.task import Task
from .models.user import User
from .models.agent import AgentTask, AgentSession, ToolExecution, ConversationTurn
from .models.chat import Conversation, Message, PendingAction
from sqlmodel import SQLModel
from .routes import tasks
from .routes.auth import router as auth_router
from .routes.users import router as users_router
from .routes.agent import router as agent_router
from .routes.chat import router as chat_router
from .utils.jwt import verify_token

# Note: Tables are managed via Alembic migrations
# SQLModel.metadata.create_all(bind=engine, checkfirst=True)

# Initialize FastAPI app
app = FastAPI(
    title="Hackathon-Todo API",
    description="REST API for the Hackathon-Todo application",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:4000"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routes
app.include_router(tasks.router, prefix="/api/v1", tags=["tasks"])
app.include_router(auth_router, prefix="/api/v1", tags=["auth"])
app.include_router(users_router, prefix="/api/v1", tags=["users"])
app.include_router(agent_router, prefix="/api/v1", tags=["agent"])
app.include_router(chat_router, prefix="/api/v1", tags=["chatbot"])

# Global middleware to verify JWT on all /api/* endpoints
@app.middleware("http")
async def verify_jwt_middleware(request: Request, call_next):
    # Only check for JWT on /api/* endpoints
    if request.url.path.startswith("/api/"):
        # Skip authentication for auth endpoints (login, register)
        if "/auth/" in request.url.path and request.method in ["POST"]:
            if (
                request.url.path.endswith("/auth/login")
                or request.url.path.endswith("/auth/register")
            ):
                response = await call_next(request)
                return response

        # Extract token from Authorization header
        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Missing or invalid Authorization header",
                headers={"WWW-Authenticate": "Bearer"},
            )

        token = auth_header[len("Bearer "):]

        # Verify the token
        try:
            verify_token(token)
        except HTTPException:
            raise
        except Exception:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication token",
                headers={"WWW-Authenticate": "Bearer"},
            )

    response = await call_next(request)
    return response

@app.get("/")
def read_root():
    return {"message": "Welcome to Hackathon-Todo API"}

@app.get("/health")
def health_check():
    return {"status": "healthy", "database": "connected"}