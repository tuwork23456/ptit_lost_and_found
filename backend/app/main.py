from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from app.database.database import engine, Base
from app.database.database import SessionLocal
from app.models.user import User
from app.models.post import Post
from app.core.security import hash_password
from datetime import datetime, timedelta
import random
from pathlib import Path
import os

from app.models import user, post, comment, message, notification, report, saved_post
from app.crud.post_crud import purge_removed_posts_older_than

from app.routers.auth_router import router as auth_router
from app.routers.post_router import router as post_router
from app.routers.comment_router import router as comment_router

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],  # Cho phép GET, POST, PUT, DELETE...
    allow_headers=["*"],  # Cho phép các header như Authorization, Content-Type
)


def _ensure_comment_reply_column() -> None:
    try:
        with engine.connect() as conn:
            rows = conn.exec_driver_sql("PRAGMA table_info(comments)").fetchall()
            cols = {str(r[1]) for r in rows}
            if "parent_comment_id" not in cols:
                conn.exec_driver_sql(
                    "ALTER TABLE comments ADD COLUMN parent_comment_id INTEGER REFERENCES comments(id)"
                )
                conn.commit()
    except Exception:
        pass


def _normalize_legacy_image_paths() -> None:
    """Normalize old image paths to consistent `/uploads/<file>` format."""
    try:
        with engine.begin() as conn:
            rows = conn.exec_driver_sql("SELECT id, image FROM posts").fetchall()
            for row in rows:
                post_id = int(row[0])
                raw = str(row[1] or "").strip()
                if not raw:
                    continue

                normalized = raw.replace("\\", "/")
                if normalized.startswith("http://") or normalized.startswith("https://") or normalized.startswith("data:image/"):
                    continue
                if "/uploads/" in normalized and not normalized.startswith("/uploads/"):
                    normalized = "/uploads/" + normalized.split("/uploads/")[-1]
                elif normalized.startswith("uploads/"):
                    normalized = "/" + normalized
                else:
                    # Keep non-empty unknown formats untouched.
                    continue

                if normalized != raw:
                    conn.exec_driver_sql(
                        "UPDATE posts SET image = ? WHERE id = ?",
                        (normalized, post_id),
                    )
    except Exception:
        pass


def _ensure_message_context_columns() -> None:
    """Add message context columns for pinned-post chat banner."""
    try:
        with engine.connect() as conn:
            rows = conn.exec_driver_sql("PRAGMA table_info(messages)").fetchall()
            cols = {str(r[1]) for r in rows}
            if "message_type" not in cols:
                conn.exec_driver_sql(
                    "ALTER TABLE messages ADD COLUMN message_type TEXT NOT NULL DEFAULT 'text'"
                )
            if "post_id" not in cols:
                conn.exec_driver_sql("ALTER TABLE messages ADD COLUMN post_id INTEGER")
            if "post_title" not in cols:
                conn.exec_driver_sql("ALTER TABLE messages ADD COLUMN post_title TEXT")
            conn.commit()
    except Exception:
        pass


def _ensure_user_is_active_column() -> None:
    try:
        with engine.connect() as conn:
            rows = conn.exec_driver_sql("PRAGMA table_info(users)").fetchall()
            cols = {str(r[1]) for r in rows}
            if "is_active" not in cols:
                conn.exec_driver_sql("ALTER TABLE users ADD COLUMN is_active BOOLEAN DEFAULT 1")
                conn.commit()
    except Exception:
        pass


def _purge_removed_posts_on_startup() -> None:
    """Auto hard-delete old REMOVED posts after retention period."""
    db = SessionLocal()
    try:
        keep_days = int(os.getenv("REMOVED_POST_RETENTION_DAYS", "14"))
        purge_removed_posts_older_than(db, keep_days)
    except Exception:
        pass
    finally:
        db.close()


_ensure_comment_reply_column()
_ensure_message_context_columns()
_ensure_user_is_active_column()
Base.metadata.create_all(bind=engine)
_normalize_legacy_image_paths()
_purge_removed_posts_on_startup()

from app.routers.message_router import router as message_router
from app.routers.notification_router import router as notification_router
from app.routers.user_router import router as user_router
from app.routers.report_router import router as report_router
from app.routers.saved_post_router import router as saved_post_router
from fastapi import WebSocket, WebSocketDisconnect
from app.core.websocket import manager

app.include_router(auth_router)
app.include_router(post_router)
app.include_router(comment_router)
app.include_router(message_router)
app.include_router(notification_router)
app.include_router(user_router)
app.include_router(report_router)
app.include_router(saved_post_router)

upload_dir = Path(__file__).resolve().parent / "uploads"
upload_dir.mkdir(parents=True, exist_ok=True)
app.mount("/uploads", StaticFiles(directory=str(upload_dir)), name="uploads")


def _seed_demo_posts_if_empty() -> None:
    """Auto-seed demo data so the feed always has content for testing."""
    db = SessionLocal()
    try:
        has_posts = db.query(Post).first()
        if has_posts:
            return

        demo_users: list[User] = []
        for i in range(1, 5):
            username = f"demo_user_{i}"
            existing = db.query(User).filter(User.username == username).first()
            if existing:
                demo_users.append(existing)
                continue
            user = User(
                username=username,
                email=f"{username}@ptit.edu.vn",
                password_hash=hash_password("123456"),
                role="USER",
            )
            db.add(user)
            db.flush()
            demo_users.append(user)

        categories = ["The sinh vien", "Vi/Bop", "Dien thoai", "Chia khoa", "Balo/Tui xach"]
        locations = ["Nha A1", "Cang tin", "Thu vien", "San truong", "Nha xe"]
        contacts = ["0912000001", "0912000002", "0912000003", "0912000004"]
        sample_images = [
            "https://picsum.photos/seed/ptit-01/900/600",
            "https://picsum.photos/seed/ptit-02/900/600",
            "https://picsum.photos/seed/ptit-03/900/600",
            "https://picsum.photos/seed/ptit-04/900/600",
            "https://picsum.photos/seed/ptit-05/900/600",
            "https://picsum.photos/seed/ptit-06/900/600",
            "https://picsum.photos/seed/ptit-07/900/600",
            "https://picsum.photos/seed/ptit-08/900/600",
        ]

        now = datetime.utcnow()
        for i in range(12):
            post_type = "LOST" if i % 2 == 0 else "FOUND"
            category = random.choice(categories)
            location = random.choice(locations)
            title = f"Mat {category} tai {location}" if post_type == "LOST" else f"Nhat duoc {category} tai {location}"
            post = Post(
                title=title,
                description=f"Tin demo #{i + 1}: can doi chieu thong tin tai {location}.",
                type=post_type,
                category=category,
                location=location,
                contact=random.choice(contacts),
                image=sample_images[i % len(sample_images)],
                views=random.randint(0, 120),
                user_id=demo_users[i % len(demo_users)].id,
                created_at=now - timedelta(minutes=i * 7),
            )
            db.add(post)

        db.commit()
    finally:
        db.close()


_seed_demo_posts_if_empty()

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