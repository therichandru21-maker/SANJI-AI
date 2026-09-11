import logging

from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.agent.agent import SanjiAgent
from app.auth.routes import get_current_user
from app.auth.routes import router as auth_router
from app.conversations.routes import router as conversations_router
from app.database import Base, engine, get_db
from app.models import Conversation, Message, User


# =========================================================
# Logging
# =========================================================

logging.basicConfig(
    level=logging.INFO,
    format=(
        "%(asctime)s | "
        "%(levelname)s | "
        "%(name)s | "
        "%(message)s"
    ),
)

logger = logging.getLogger("sanji.api")


# =========================================================
# Database
# =========================================================

Base.metadata.create_all(bind=engine)


# =========================================================
# FastAPI Application
# =========================================================

app = FastAPI(
    title="SANJI AI",
    description="Autonomous General-Purpose AI Workflow Agent",
    version="2.0.0",
)


# =========================================================
# CORS
# =========================================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        # Local development
        "http://localhost:5173",
        "http://127.0.0.1:5173",

        # Live Render frontend
        "https://sanji-ai-1.onrender.com",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# =========================================================
# Routers
# =========================================================

app.include_router(auth_router)
app.include_router(conversations_router)


# =========================================================
# SANJI AI Agent
# =========================================================

agent = SanjiAgent()


# =========================================================
# Request Models
# =========================================================

class GoalRequest(BaseModel):
    goal: str = Field(
        ...,
        min_length=1,
        max_length=20000,
    )

    conversation: list[dict] = Field(
        default_factory=list,
    )

    conversation_id: int | None = None


# =========================================================
# Root Endpoint
# =========================================================

@app.get("/")
def root():
    return {
        "name": "SANJI AI",
        "status": "online",
        "version": "2.0.0",
        "message": (
            "Autonomous General-Purpose "
            "AI Agent is ready."
        ),
    }


# =========================================================
# Health Check
# =========================================================

@app.get("/health")
def health():
    return {
        "status": "healthy",
        "service": "SANJI AI",
        "agent_version": "2.0.0",
        "database": "connected",
    }


# =========================================================
# Run AI Agent
# =========================================================

@app.post("/agent/run")
def run_agent(
    request: GoalRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    # -----------------------------------------------------
    # Validate goal
    # -----------------------------------------------------

    goal = request.goal.strip()

    if not goal:
        return {
            "status": "failed",
            "error": "Goal cannot be empty.",
        }

    logger.info(
        "New agent request | user_id=%s | goal=%s",
        current_user.id,
        goal,
    )

    # -----------------------------------------------------
    # Find existing conversation
    # -----------------------------------------------------

    conversation = None

    if request.conversation_id:

        conversation = (
            db.query(Conversation)
            .filter(
                Conversation.id == request.conversation_id,
                Conversation.user_id == current_user.id,
            )
            .first()
        )

        if not conversation:
            return {
                "status": "failed",
                "error": "Conversation not found.",
            }

    # -----------------------------------------------------
    # Create new conversation
    # -----------------------------------------------------

    if not conversation:

        conversation = Conversation(
            user_id=current_user.id,
            title=goal[:80],
        )

        db.add(conversation)
        db.commit()
        db.refresh(conversation)

        logger.info(
            "Created conversation | id=%s | user_id=%s",
            conversation.id,
            current_user.id,
        )

    # -----------------------------------------------------
    # Save User Message
    # -----------------------------------------------------

    user_message = Message(
        conversation_id=conversation.id,
        role="user",
        content=goal,
    )

    db.add(user_message)
    db.commit()

    # -----------------------------------------------------
    # Run SANJI AI Agent
    # -----------------------------------------------------

    try:

        result = agent.run(
            goal=goal,
            conversation=request.conversation,
        )

    except Exception as error:

        logger.exception(
            "Agent execution failed"
        )

        return {
            "status": "failed",
            "conversation_id": conversation.id,
            "error": str(error),
        }

    # -----------------------------------------------------
    # Get Final Answer
    # -----------------------------------------------------

    final_answer = result.get(
        "final_answer",
        "",
    )

    if not final_answer:

        final_answer = result.get(
            "error",
            "I couldn't complete the request.",
        )

    # -----------------------------------------------------
    # Save Assistant Message
    # -----------------------------------------------------

    assistant_message = Message(
        conversation_id=conversation.id,
        role="assistant",
        content=final_answer,
    )

    db.add(assistant_message)

    # -----------------------------------------------------
    # Update Conversation
    # -----------------------------------------------------

    conversation.updated_at = (
        conversation.updated_at
    )

    db.commit()
    db.refresh(conversation)

    logger.info(
        "Conversation saved | id=%s | user_id=%s",
        conversation.id,
        current_user.id,
    )

    # -----------------------------------------------------
    # Return Agent Result
    # -----------------------------------------------------

    result["conversation_id"] = conversation.id

    return result