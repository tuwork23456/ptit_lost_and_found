from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database.database import get_db
# Import Schemas
from app.schemas.userschemas import UserCreate, UserResponse, UserLogin, TokenResponse
# Import Services logic
from app.services.auth_service import register_user_logic, authenticate_user_logic
# Import hàm tạo token
from app.core.security import create_access_token

router = APIRouter(prefix="/auth", tags=["auth"])


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
    # 1. Xác thực user từ logic service
    user = authenticate_user_logic(db, login_data.email, login_data.password)

    # 2. Xử lý khi xác thực thất bại
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, 
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # 3. Xử lý khi xác thực thành công: Tạo JWT Token
    access_token = create_access_token(subject=user.id) # Mã hóa User ID vào token

    # 4. Trả về cấu trúc đúng theo TokenResponse Schema
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": user # Trả về luôn object user, FastAPI sẽ tự parse sang UserResponse bên trong
    }