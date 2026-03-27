# 🧩 Item Search Forum

Hệ thống web cho phép người dùng đăng bài, tìm kiếm và tương tác (comment, message, notification).

Project gồm:

* 🔙 Backend: FastAPI
* 💻 Frontend: React + Vite

---

# 🚀 Tech Stack

## Backend

* Python 3.12
* FastAPI
* SQLAlchemy
* Uvicorn
* JWT (python-jose)
* Cloudinary (upload ảnh)

## Frontend

* React
* Vite
* Axios
* React Router
* TailwindCSS

---

# 📁 Project Structure

```
Item-Search-Forum/
│
├── backend/
│   ├── app/
│   │   ├── core/          # security, websocket
│   │   ├── crud/          # thao tác DB
│   │   ├── database/      # config database
│   │   ├── models/        # ORM models
│   │   ├── routers/       # API routes
│   │   ├── schemas/       # Pydantic schemas
│   │   ├── services/      # business logic
│   │   └── main.py        # entry point
│   └── requirements.txt
│
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   ├── pages/
│   │   ├── services/
│   │   └── context/
│   └── package.json
```

---

# ⚙️ Setup & Run

## 🔙 Backend (FastAPI)

### 1. Vào thư mục

```bash
cd backend
```

### 2. Tạo & kích hoạt môi trường

```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Cài thư viện

```bash
pip install -r requirements.txt
```

### 4. Chạy server

```bash
uvicorn app.main:app --reload
```

### 🌐 Kết quả

* API: http://127.0.0.1:8000
* Docs: http://127.0.0.1:8000/docs

---

## 💻 Frontend (React + Vite)

### ⚠️ Yêu cầu: Node >= 20

### 1. Cài Node bằng nvm (nếu chưa có)

```bash
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.7/install.sh | bash
nvm install 20
nvm use 20
```

---

### 2. Vào thư mục frontend

```bash
cd frontend
```

### 3. Cài lại dependencies

```bash
rm -rf node_modules package-lock.json
npm install
```

### 4. Chạy project

```bash
npm run dev
```

### 🌐 Kết quả

* http://localhost:5173

---

# 🔄 Flow chạy hệ thống

1. ▶️ Chạy backend trước
2. ▶️ Chạy frontend
3. 🌐 Mở trình duyệt
4. 🔗 Frontend gọi API backend

---

# 🔑 Environment Variables

Tạo file `.env` trong `backend/`:

```
DATABASE_URL=your_database_url
SECRET_KEY=your_secret_key
CLOUDINARY_URL=your_cloudinary_config
```

---

# 📡 API Overview

* Auth: `/auth`
* User: `/users`
* Post: `/posts`
* Comment: `/comments`
* Message: `/messages`
* Notification: `/notifications`
* Report: `/reports`

---

# ✅ Dấu hiệu chạy thành công

* Backend chạy không lỗi
* Frontend hiển thị UI
* API gọi thành công (F12 → Network)

---

# ⚠️ Lưu ý

* Không push:

  * `venv/`
  * `node_modules/`
  * `.env`
* Đã có `.gitignore` sẵn

---

# 👨‍💻 Author

tuwork23456 va 3 nguoi khac :>>

---

# 🚀 Future Improvements

* Deploy server (Docker / VPS)
* Tối ưu API
* Thêm real-time (WebSocket)
* Hoàn thiện authentication & authorization

---
