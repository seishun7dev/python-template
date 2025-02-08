import uuid
import logging

from typing import AsyncGenerator
from contextlib import asynccontextmanager

from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import FastAPI, Depends, HTTPException, Request


from app.db.models import User, UserCreate
from app.configs.context import request_id_ctx
from app.configs.logs_config import configure_logging
from app.configs.db_config import engine, AsyncSessionLocal

# --------------------------
# Initialize logging configuration
# --------------------------
log_listener = configure_logging()
logger = logging.getLogger(__name__)


# --------------------------
# Application Setup
# --------------------------
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("Application initialized")
    yield
    # Shutdown
    await engine.dispose()
    logger.info("Application shutdown")
    logger.info("Database connection closed")
    log_listener.stop()

app = FastAPI(lifespan=lifespan)

# --------------------------
# Middleware for Request UUID
# --------------------------
@app.middleware("http")
async def add_request_uuid(request: Request, call_next):
    request_id = request.headers.get("X-Request-ID") or str(uuid.uuid4())
    token = request_id_ctx.set(request_id)
    response = await call_next(request)
    response.headers["X-Request-ID"] = request_id
    request_id_ctx.reset(token)
    return response

# --------------------------
# Dependency Injection
# --------------------------
async def get_db(request: Request) -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
            logger.info("Database session committed")
        except Exception as e:
            await session.rollback()
            logger.error(f"Database error: {str(e)}")
            raise HTTPException(status_code=500, detail="Database error")

# --------------------------
# API Endpoints
# --------------------------
@app.post("/users/", response_model=UserCreate)
async def create_user(
    user: UserCreate, 
    db: AsyncSession = Depends(get_db)
):
    try:
        db_user = User(**user.model_dump())
        db.add(db_user)
        await db.flush()
        await db.refresh(db_user)
        logger.info(f"Created new user: {user.email}")
        return db_user
    except Exception as e:
        logger.error(f"Error creating user: {str(e)}")
        raise HTTPException(status_code=400, detail="Email already exists")

