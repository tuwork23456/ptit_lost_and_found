"""
Tao hoac cap nhat mot tai khoan ADMIN de test (chay tu thu muc backend, venv da cai deps).

  cd backend && source ../.venv/bin/activate && python create_admin.py

Mac dinh:
  email:    admin@ptit.edu.vn   (khong dung @*.test — Pydantic EmailStr / email-validator tu choi domain .test)
  password: Adminptit1
"""
from __future__ import annotations

import os
import sys

# Dam bao import app.* khi chay truc tiep file nay
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.database.database import SessionLocal
from app.models.user import User
from app.core.security import hash_password

DEFAULT_EMAIL = "admin@ptit.edu.vn"
DEFAULT_USERNAME = "admin_ptit"
DEFAULT_PASSWORD = "Adminptit1"
# Domain .test bi email-validator tu choi -> FastAPI tra 422 khi dang nhap voi EmailStr
LEGACY_UNUSABLE_EMAIL = "admin@ptit.test"

# IMPORTANT:
# Khi script chay doc lap, can import toan bo model de SQLAlchemy registry
# resolve duoc cac relationship (Post, Comment, Message, Notification, ...).
from app.models import user, post, comment, message, notification, report, saved_post  # noqa: F401


def _migrate_legacy_ptit_test_email(db, target_email: str) -> None:
    legacy = db.query(User).filter(User.email == LEGACY_UNUSABLE_EMAIL).first()
    if not legacy:
        return
    taken = db.query(User).filter(User.email == target_email).first()
    if taken is not None and taken.id != legacy.id:
        print(
            f"Canh bao: da co user khac dung {target_email}; "
            f"xoa/sua tay user {LEGACY_UNUSABLE_EMAIL} (id={legacy.id}) neu can."
        )
        return
    legacy.email = target_email
    db.commit()
    print(
        f"Da doi email {LEGACY_UNUSABLE_EMAIL} -> {target_email} "
        "(domain .test khong hop le voi API dang nhap)."
    )


def main() -> None:
    email = os.environ.get("PTIT_ADMIN_EMAIL", DEFAULT_EMAIL).strip().lower()
    username = os.environ.get("PTIT_ADMIN_USERNAME", DEFAULT_USERNAME).strip()
    password = os.environ.get("PTIT_ADMIN_PASSWORD", DEFAULT_PASSWORD)

    db = SessionLocal()
    try:
        if email == DEFAULT_EMAIL:
            _migrate_legacy_ptit_test_email(db, email)

        user = db.query(User).filter(User.email == email).first()
        if user is None:
            user = db.query(User).filter(User.username == username).first()

        h = hash_password(password)
        if user:
            user.role = "ADMIN"
            user.password_hash = h
            if user.email != email:
                other = db.query(User).filter(User.email == email, User.id != user.id).first()
                if not other:
                    user.email = email
            if user.username != username:
                other_u = db.query(User).filter(User.username == username, User.id != user.id).first()
                if not other_u:
                    user.username = username
            db.commit()
            print(f"Da cap nhat user id={user.id} thanh ADMIN ({user.email}).")
        else:
            user = User(
                username=username,
                email=email,
                password_hash=h,
                role="ADMIN",
            )
            db.add(user)
            db.commit()
            db.refresh(user)
            print(f"Da tao ADMIN id={user.id} ({email}).")

        print("Dang nhap frontend/API:")
        print(f"  Email:    {email}")
        print(f"  Password: {password}")
        print("Truy cap /admin sau khi dang nhap.")
    finally:
        db.close()


if __name__ == "__main__":
    main()
