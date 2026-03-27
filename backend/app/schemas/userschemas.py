from pydantic import BaseModel, EmailStr, Field
from datetime import datetime
from typing import Optional

class UserBase(BaseModel):
    username: str
    email: EmailStr # Sử dụng EmailStr để tự động validate định dạng email

class UserCreate(UserBase):
    password: str = Field(..., min_length=6, description="Mật khẩu phải từ 6 ký tự trở lên")  # Chỉ nhận password lúc đăng ký

class UserResponse(UserBase):
    id: int
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