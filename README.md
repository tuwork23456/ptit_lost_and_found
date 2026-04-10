# PTIT Lost & Found

Ung dung web tim do that lac cho sinh vien PTIT: backend **FastAPI** + **SQLite**, frontend **Reflex**.

---

## Yeu cau he thong

- **Python** 3.12+ (nen trung ban dang dung de dev)
- **Git**
- **Node.js** LTS + **npm** (Reflex can khi build frontend; neu thieu thi `reflex run` se bao loi)

Lam viec trong **WSL/Linux** hoac **macOS** cho thuan tien (vi du duong dan `~/ptit_lost_and_found`).

---

## Cai dat

### 1. Clone va moi truong ao

```bash
cd ~/ptit_lost_and_found
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -U pip
```

Uu tien `python -m pip` va `python -m uvicorn` / `python -m reflex` sau khi `activate`, tranh loi `pip`/`uvicorn` trong venv.

### 2. Cai dependency

```bash
pip install -r backend/requirements.txt
pip install -r Frontend/requirements.txt
```

### 3. Bien moi truong (bat buoc de chay backend)

Backend **khong chay** neu thieu `APP_SECRET_KEY` (JWT).

```bash
cp backend/.env.example backend/.env
```

Mo `backend/.env` va dat it nhat:

- `APP_SECRET_KEY` — chuoi bi mat dai, ngau nhien (vi du 32+ ky tu)

Cac bien trong `backend/.env.example` con lai co the giu mac dinh khi demo.

**Tuy chon anh bai viet (Cloudinary):** neu dat `CLOUDINARY_CLOUD_NAME`, `CLOUDINARY_API_KEY`, `CLOUDINARY_API_SECRET` thi upload se day len Cloudinary. Neu **khong** cau hinh hoac upload loi, backend **tu luu anh cuc bo** duoi `backend/app/uploads/` va phuc vu qua URL dang `/uploads/...` (xem `backend/app/routers/post_router.py`).

**Tuy chon:** `REMOVED_POST_RETENTION_DAYS` — so ngay giu bai da go truoc khi xoa han (mac dinh 14).

---

## Chay du an

Can **hai terminal**, cung mot venv.

### Terminal 1 — Backend

**Phai** chay tu thu muc `backend/` (code import `from app...`; neu sai thu muc se loi `No module named 'app'`).

```bash
cd ~/ptit_lost_and_found
source .venv/bin/activate
cd backend
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

- API docs: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)

### Terminal 2 — Frontend (Reflex)

```bash
cd ~/ptit_lost_and_found
source .venv/bin/activate
cd Frontend
python -m reflex run
```

- Giao dien thuong la [http://localhost:3000](http://localhost:3000) (xem dung port tren log cua Reflex).

Frontend goi API mac dinh toi `http://localhost:8000` (`Frontend/ptit_lost_and_found/state.py`). Neu doi port backend, can doi `api_base_url` trong state cho khop.

---

## Dang nhap va tai khoan

Form dang nhap dung **email** + **mat khau**, khong phai username.

**Tao / cap nhat admin (khuyen nghi khi setup may moi):**

```bash
cd ~/ptit_lost_and_found/backend
source ../.venv/bin/activate
python create_admin.py
```

Script in ra email/mat khau (mac dinh trong docstring: `admin@ptit.edu.vn`, `Adminptit1`). Ghi de bang bien moi truong `PTIT_ADMIN_EMAIL`, `PTIT_ADMIN_USERNAME`, `PTIT_ADMIN_PASSWORD`.

**User thuong:** dang ky tai `/register` tren frontend.

**DB trong:** khi khoi dong, backend co the tu tao user/post demo (`backend/app/main.py`). User demo: email `demo_user_1@ptit.edu.vn` … `demo_user_4@ptit.edu.vn`, mat khau `123456` — chi de thu nhanh, khong dung cho production.

---

## Gap loi thuong gap

| Hien tuong | Cach xu ly |
|------------|------------|
| `Missing APP_SECRET_KEY` | Tao `backend/.env` tu `.env.example` va dien `APP_SECRET_KEY`. |
| `No module named 'app'` khi chay backend | `cd backend` roi moi chay `python -m uvicorn app.main:app ...` |
| `pip` / `uvicorn` trong venv bao `cannot execute` | Tao lai venv: `deactivate`, xoa `.venv`, `python3 -m venv .venv`, cai lai requirements. |
| Frontend Reflex loi build / HMR la | Xoa cache roi chay lai: `rm -rf Frontend/.web Frontend/.reflex` sau do `python -m reflex run`. |
| Thieu Node khi `reflex run` | Cai Node.js LTS, chay lai; lam theo huong dan tren terminal (vi du `npm install` neu duoc nhac). |

---

## Cau truc thu muc (rut gon)

- `backend/` — FastAPI, SQLite (`lostfound.db` o thu muc backend khi chay), JWT, WebSocket
- `Frontend/` — ung dung Reflex (`ptit_lost_and_found`)

---

## Ghi chu demo / do an

- Khong commit file nhay cam: dung `backend/.env` (da co trong `backend/.gitignore`).
- File `.db` va thu muc upload cuc bo thuong khong nen dua len Git neu repo cong khai.

## Tai lieu them

- [BAO_CAO_KY_THUAT.md](BAO_CAO_KY_THUAT.md) — bao cao cong nghe, co so du lieu, cau truc frontend va lien ket API.
