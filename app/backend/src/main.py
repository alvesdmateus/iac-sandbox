"""FastAPI application entry point."""
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import socketio

from .config import settings


# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


# Socket.IO server
sio = socketio.AsyncServer(
    async_mode="asgi",
    cors_allowed_origins=settings.CORS_ORIGINS,
    logger=settings.DEBUG,
    engineio_logger=settings.DEBUG,
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events."""
    logger.info("Starting Infrastructure Visualization API...")
    logger.info(f"Infra directory: {settings.INFRA_DIR}")
    yield
    logger.info("Shutting down Infrastructure Visualization API...")


# Create FastAPI app
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    debug=settings.DEBUG,
    lifespan=lifespan,
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return JSONResponse(
        content={
            "status": "healthy",
            "version": settings.APP_VERSION,
            "infra_dir": str(settings.INFRA_DIR),
        }
    )


# API version endpoint
@app.get("/api/v1/status")
async def api_status():
    """API status endpoint."""
    return JSONResponse(
        content={
            "status": "operational",
            "version": settings.APP_VERSION,
            "features": {
                "stacks": True,
                "deployments": True,
                "files": True,
                "websocket": True,
            },
        }
    )


# Import and include routers
from .api import stacks, files

app.include_router(stacks.router, prefix="/api/v1", tags=["stacks"])
app.include_router(files.router, prefix="/api/v1", tags=["files"])


# Mount Socket.IO app
socket_app = socketio.ASGIApp(
    socketio_server=sio,
    other_asgi_app=app,
    socketio_path="/ws/socket.io",
)


# Socket.IO event handlers
@sio.event
async def connect(sid, environ):
    """Handle client connection."""
    logger.info(f"Client connected: {sid}")
    await sio.emit("connection:confirmed", {"sid": sid}, room=sid)


@sio.event
async def disconnect(sid):
    """Handle client disconnection."""
    logger.info(f"Client disconnected: {sid}")


@sio.event
async def subscribe_stack(sid, data):
    """Subscribe client to stack updates."""
    stack_name = data.get("stackName")
    if stack_name:
        await sio.enter_room(sid, f"stack:{stack_name}")
        logger.info(f"Client {sid} subscribed to stack: {stack_name}")
        await sio.emit(
            "subscription:confirmed",
            {"type": "stack", "stackName": stack_name},
            room=sid,
        )


@sio.event
async def subscribe_deployment(sid, data):
    """Subscribe client to deployment updates."""
    deployment_id = data.get("deploymentId")
    if deployment_id:
        await sio.enter_room(sid, f"deployment:{deployment_id}")
        logger.info(f"Client {sid} subscribed to deployment: {deployment_id}")
        await sio.emit(
            "subscription:confirmed",
            {"type": "deployment", "deploymentId": deployment_id},
            room=sid,
        )


# Export for uvicorn
if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "src.main:socket_app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
        log_level=settings.LOG_LEVEL.lower(),
    )
