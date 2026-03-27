from sqlalchemy.orm import Session
from app.models.user import User
from app.schemas.userschemas import UserCreate
# Import các hàm bảo mật từ folder core mới tạo
from app.core.security import hash_password, verify_password, create_access_token

# =======================
# LOGIC ĐĂNG KÝ
# =======================
def register_user_logic(db: Session, user_data: UserCreate):
    try:
        # 1. Check email tồn tại
        existing_user = db.query(User).filter(User.email == user_data.email).first()
        if existing_user:
            raise ValueError("Email already exists")

        # 2. Hash password (gọi sang core/security)
        hashed_password = hash_password(user_data.password)

        # 3. Tạo user object từ SQLAlchemy model
        new_user = User(
            username=user_data.username,
            email=user_data.email,
            password_hash=hashed_password
        )

        # 4. Lưu DB
        db.add(new_user)
        db.commit()
        db.refresh(new_user)

        return new_user

    except Exception as e:
        db.rollback()
        raise e


# =======================
# LOGIC ĐĂNG NHẬP
# =======================
def authenticate_user_logic(db: Session, email: str, password: str):
    """
    Xác thực thông tin đăng nhập. 
    Nếu đúng, trả về object User. Nếu sai, trả về None.
    """
    try:
        # 1. Tìm user theo email
        user = db.query(User).filter(User.email == email).first()
        if not user:
            return None # Không tìm thấy user

        # 2. Verify password (gọi sang core/security)
        if not verify_password(password, user.password_hash):
            return None # Sai mật khẩu

        # 3. Trả về object user đã xác thực thành công
        return user

    except Exception as e:
        raise e