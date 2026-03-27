from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.database.database import engine, Base

from app.models import user, post, comment, message, notification, report

from app.routers.auth_router import router as auth_router
from app.routers.post_router import router as post_router
from app.routers.comment_router import router as comment_router

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],  # Cho phép GET, POST, PUT, DELETE...
    allow_headers=["*"],  # Cho phép các header như Authorization, Content-Type
)

Base.metadata.create_all(bind=engine)

from app.routers.message_router import router as message_router
from app.routers.notification_router import router as notification_router
from app.routers.user_router import router as user_router
from app.routers.report_router import router as report_router
from fastapi import WebSocket, WebSocketDisconnect
from app.core.websocket import manager

app.include_router(auth_router)
app.include_router(post_router)
app.include_router(comment_router)
app.include_router(message_router)
app.include_router(notification_router)
app.include_router(user_router)
app.include_router(report_router)

# WebSocket Endpoint
@app.websocket("/ws/{user_id}")
async def websocket_endpoint(websocket: WebSocket, user_id: int):
    await manager.connect(websocket, user_id)
    try:
        while True:
            # Giữ kết nối mở, đợi data từ client gởi lên (cần thiết để duy trì kết nối)
            data = await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(user_id)