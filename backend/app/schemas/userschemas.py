from pydantic import BaseModel, EmailStr, Field, field_validator
from datetime import datetime
import re

class UserBase(BaseModel):
    username: str
    email: EmailStr # Sử dụng EmailStr để tự động validate định dạng email

class UserCreate(UserBase):
    password: str = Field(..., min_length=8, description="Mat khau toi thieu 8 ky tu, gom chu hoa, chu thuong va so")

    @field_validator("password")
    @classmethod
    def validate_password_strength(cls, password: str) -> str:
        if not re.search(r"[A-Z]", password) or not re.search(r"[a-z]", password) or not re.search(r"\d", password):
            raise ValueError("Password must include uppercase, lowercase, and number")
        return password

class UserResponse(UserBase):
    id: int
    role: str = "USER"
    created_at: datetime

    # Quan trọng: Cấu hình để Pydantic đọc dữ liệu từ SQLAlchemy Model object
    model_config = {"from_attributes": True}

# Schema dùng cho Body lúc User gửi request đăng nhập
class UserLogin(BaseModel):
    email: EmailStr # Sửa lại dùng email đăng nhập cho phổ biến
    password: str

# Schema trả về cho Frontend sau khi login thành công
class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse # Trả về luôn thông tin user để Frontend hiển thị tên, avatar...