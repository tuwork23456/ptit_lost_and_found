from fastapi import APIRouter, Depends, HTTPException, status
from datetime import datetime, timedelta
from threading import Lock
from sqlalchemy.orm import Session
from app.database.database import get_db
# Import Schemas
from app.schemas.userschemas import UserCreate, UserResponse, UserLogin, TokenResponse
# Import Services logic
from app.services.auth_service import register_user_logic, authenticate_user_logic
# Import hàm tạo token
from app.core.security import create_access_token

router = APIRouter(prefix="/auth", tags=["auth"])

MAX_LOGIN_ATTEMPTS = 5
ATTEMPT_WINDOW_MINUTES = 15
LOCKOUT_MINUTES = 15

_login_attempts: dict[str, list[datetime]] = {}
_locked_until: dict[str, datetime] = {}
_attempt_lock = Lock()


def _is_locked(email: str) -> bool:
    now = datetime.utcnow()
    with _attempt_lock:
        locked_until = _locked_until.get(email)
        if not locked_until:
            return False
        if locked_until <= now:
            _locked_until.pop(email, None)
            return False
        return True


def _register_failed_attempt(email: str) -> None:
    now = datetime.utcnow()
    window_start = now - timedelta(minutes=ATTEMPT_WINDOW_MINUTES)
    with _attempt_lock:
        attempts = [t for t in _login_attempts.get(email, []) if t >= window_start]
        attempts.append(now)
        _login_attempts[email] = attempts
        if len(attempts) >= MAX_LOGIN_ATTEMPTS:
            _locked_until[email] = now + timedelta(minutes=LOCKOUT_MINUTES)
            _login_attempts.pop(email, None)


def _clear_login_tracking(email: str) -> None:
    with _attempt_lock:
        _login_attempts.pop(email, None)
        _locked_until.pop(email, None)


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register_user(user_data: UserCreate, db: Session = Depends(get_db)):
    """
    Đăng ký user mới.
    - Nhận vào dữ liệu dạng JSON Body khớp với UserCreate Schema.
    - Trả về dữ liệu khớp với UserResponse Schema (đã ẩn password_hash).
    """
    try:
        user = register_user_logic(db, user_data)
        return user # FastAPI tự động parse object user -> UserResponse schema
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal Server Error")


@router.post("/login", response_model=TokenResponse)
def login_user(login_data: UserLogin, db: Session = Depends(get_db)):
    """
    Đăng nhập.
    - Nhận vào dữ liệu dạng JSON Body khớp với UserLogin Schema.
    - Trả về Access Token và thông tin User.
    """
    normalized_email = str(login_data.email).strip().lower()
    if _is_locked(normalized_email):
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Too many failed login attempts. Try again later.",
        )

    # 1. Xác thực user từ logic service
    user = authenticate_user_logic(db, normalized_email, login_data.password)

    # 2. Xử lý khi xác thực thất bại
    if not user:
        _register_failed_attempt(normalized_email)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, 
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    if not bool(getattr(user, "is_active", True)):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Tai khoan da bi khoa.",
        )
    _clear_login_tracking(normalized_email)

    # 3. Xử lý khi xác thực thành công: Tạo JWT Token
    access_token = create_access_token(subject=user.id) # Mã hóa User ID vào token

    # 4. Trả về cấu trúc đúng theo TokenResponse Schema
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": user # Trả về luôn object user, FastAPI sẽ tự parse sang UserResponse bên trong
    }