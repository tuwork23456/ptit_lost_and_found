from app.database.database import SessionLocal, engine, Base

# Import TẤT CẢ model để SQLAlchemy có thể khởi tạo các mối quan hệ (relationships)
from app.models.user import User
from app.models.post import Post
from app.models.comment import Comment
from app.models.message import Message
from app.models.notification import Notification

import random

from app.core.security import hash_password

# Tạo toàn bộ Schema MỚI NHẤT từ các class Model hiện tại
Base.metadata.create_all(bind=engine)

db = SessionLocal()

def seed_data():
    print("Bắt đầu khởi tạo dữ liệu ảo...")
    
    # 1. Thêm 5 Users
    users = []
    for i in range(1, 6):
        existing = db.query(User).filter(User.username == f"user{i}").first()
        if existing:
            users.append(existing)
            continue
            
        user = User(
            username=f"user{i}",
            email=f"user{i}@example.com",
            password_hash=hash_password("123456"),
            role="USER",
        )
        db.add(user)
        users.append(user)
        
    db.commit()
    for user in users:
        db.refresh(user)

    print(f"Đã nạp {len(users)} users.")

    # 2. Thêm 15 Posts
    categories = ["Thẻ sinh viên", "Ví/Bóp", "Điện thoại/Laptop", "Chìa khóa", "Balo/Túi xách"]
    locations = ["Nhà A1", "Căn tin khu B", "Sân bóng", "Thư viện", "Nhà xưởng thực hành"]
    types = ["LOST", "FOUND"]

    for i in range(1, 16):
        t = random.choice(types)
        c = random.choice(categories)
        l = random.choice(locations)
        title = f"Tìm {c} tại {l}" if t == "LOST" else f"Nhặt được {c} tại {l}"
        
        post = Post(
            title=title,
            description=f"Đây là tin đăng tự động số {i}. Chi tiết về {c} bị { 'mất' if t == 'LOST' else 'nhặt được' } tại {l}.",
            type=t,
            category=c,
            location=l,
            contact=f"09xx{i:03d}xxx",
            image=f"https://picsum.photos/seed/{random.randint(1,1000)}/600/400",
            views=random.randint(5, 300),
            user_id=random.choice(users).id
        )
        db.add(post)
        
    db.commit()
    print("Đã nạp thành công 15 bài Post mới.")

if __name__ == "__main__":
    seed_data()
