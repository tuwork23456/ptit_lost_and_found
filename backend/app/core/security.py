from datetime import datetime, timedelta
from typing import Any, Union
from jose import jwt
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError
from sqlalchemy.orm import Session
from app.database.database import get_db
from app.models.user import User

# --- CẤU HÌNH ---
# TRONG THỰC TẾ, HÃY DÙNG BIẾN MÔI TRƯỜNG (.env) ĐỂ LƯU CÁC CÁI NÀY
# Lệnh tạo key bí mật: openssl rand -hex 32
SECRET_KEY = "Sieu_Mat_Khau_Cua_Btl_Python_Khong_Ai_Biet_Duoc_Dau_Nhe" 
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24 * 7  # Token có hiệu lực trong 7 ngày

# Dùng pbkdf2_sha256 thay vì bcrypt, vì bcrypt đang dính lỗi tương thích C-Extension (thường thấy với Python 3.12/3.13)
# pbkdf2_sha256 dùng thư viện chuẩn hashlib của Python nên đảm bảo 100% không bao giờ gặp lỗi bộ nhớ hay độ dài vô lý.
pwd_context = CryptContext(schemes=["pbkdf2_sha256", "bcrypt"], deprecated="auto")


# =======================
# HASH & VERIFY PASSWORD
# =======================
def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


# =======================
# JWT TOKEN LOGIC
# =======================
def create_access_token(subject: Union[str, Any], expires_delta: timedelta = None) -> str:
    """
    Tạo ra một JWT Token. subject thường là User ID.
    """
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    # Payload chứa thông tin chúng ta muốn mã hóa vào token
    to_encode = {"exp": expire, "sub": str(subject), "type": "access"}
    
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

# Khai báo "cửa" soát vé: FastAPI sẽ tự động tìm token ở Header của request
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    """
    Hàm Dependency này sẽ được gắn vào các API cần bảo mật.
    Nó trích xuất token, giải mã, và trả về thông tin User đang đăng nhập.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        # 1. Giải mã token bằng SECRET_KEY và thuật toán (ALGORITHM) đã cấu hình ở trên
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        
        # 2. Lấy ID người dùng (trường 'sub')
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception
            
    except JWTError:
        # Nếu token bị chỉnh sửa, sai định dạng, hoặc hết hạn -> văng lỗi ngay
        raise credentials_exception

    # 3. Dùng user_id truy vấn xuống Database để lấy đầy đủ thông tin User
    user = db.query(User).filter(User.id == int(user_id)).first()
    if user is None:
        raise credentials_exception

    # 4. Trả về object User hợp lệ
    return user