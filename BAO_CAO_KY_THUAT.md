# Bao cao cong nghe — PTIT Lost & Found

Tai lieu tuong trinh ve **cong nghe**, **co so du lieu**, **cau truc frontend** va **cach API lien ket voi giao dien**. File dat cung cap voi [README.md](README.md) (huong dan cai dat va chay).

---

## Muc luc

1. [Tong quan du an](#1-tong-quan-du-an)
2. [Cong nghe su dung va nhiem vu](#2-cong-nghe-su-dung-va-nhiem-vu-trong-ung-dung)
3. [Co so du lieu](#3-co-so-du-lieu)
4. [Cau truc frontend va thanh phan chuc nang](#4-cau-truc-frontend-va-thanh-phan-chuc-nang)
5. [API backend va lien ket voi frontend](#5-api-backend-va-lien-ket-voi-frontend)
6. [Ket luan va pham vi demo](#6-ket-luan-va-pham-vi-demo)

---

## 1. Tong quan du an

**PTIT Lost & Found** la nen tang ho tro sinh vien dang va tra cuu tin **mat do / nhat duoc**, co **binh luan**, **thong bao**, **tin nhan**, **luu bai**, **bao cao** va **duyet / go bai** (admin).

Kien truc tach lop:

- **Backend**: REST API (FastAPI) + **WebSocket** de cap nhat gan thoi gian thuc; du lieu luu **SQLite** qua **SQLAlchemy**.
- **Frontend**: ung dung **Reflex** (UI viet bang Python), goi backend qua **HTTP (httpx)** va mo **WebSocket** tu trinh duyet toi cung host API.

---

## 2. Cong nghe su dung va nhiem vu trong ung dung

| Cong nghe | Nhiem vu trong he thong |
|-----------|-------------------------|
| **Python 3** | Ngon ngu chung cho backend va frontend (Reflex). |
| **FastAPI** | Khung web bat dong bo: dinh nghia route HTTP, dependency injection, tai lieu OpenAPI (`/docs`). Khoi tao: [backend/app/main.py](backend/app/main.py). |
| **Uvicorn** | ASGI server chay ung dung FastAPI. |
| **SQLAlchemy 2** | ORM: anh xa bang SQLite voi class model, session, truy van. Cau hinh: [backend/app/database/database.py](backend/app/database/database.py). |
| **SQLite** | CSDL file don (`lostfound.db` trong thu muc `backend/`), phu hop demo. |
| **Pydantic** | Kiem tra va chuan hoa du lieu request/response (schema). |
| **python-jose** | Ma hoa / giai ma **JWT** cho phien dang nhap. |
| **passlib** | Bam mat khau (uu tien `pbkdf2_sha256`, ho tro legacy `bcrypt`). Xem [backend/app/core/security.py](backend/app/core/security.py). |
| **python-dotenv** | Doc bien moi truong tu `backend/.env` (vi du `APP_SECRET_KEY`, thoi han token). |
| **Cloudinary + requests** | Tuy chon: dang anh len CDN. Neu thieu cau hinh hoac loi upload, backend **luu anh cuc bo** duoi `backend/app/uploads/`. Xem [backend/app/routers/post_router.py](backend/app/routers/post_router.py), [backend/app/services/cloudinary_service.py](backend/app/services/cloudinary_service.py). |
| **CORSMiddleware** | Cho phep frontend (cong 3000, 5173, …) goi API tu trinh duyet. Cau hinh trong [backend/app/main.py](backend/app/main.py). |
| **StaticFiles** | Phuc vu file anh da luu cuc bo qua tien to URL `/uploads`. |
| **WebSocket (Starlette/FastAPI)** | Kenh `/ws/{user_id}`: server day su kien toi client; quan ly ket noi: [backend/app/core/websocket.py](backend/app/core/websocket.py). |
| **Reflex** | Framework frontend Python: build SPA, dinh tuyen trang, state reactive. Cau hinh: [Frontend/rxconfig.py](Frontend/rxconfig.py). |
| **Tailwind (CDN + plugin)** | Utility CSS; layout nap script Tailwind trong [Frontend/ptit_lost_and_found/ptit_lost_and_found.py](Frontend/ptit_lost_and_found/ptit_lost_and_found.py). |
| **httpx** | Client HTTP bat dong bo trong state frontend. File trung tam: [Frontend/ptit_lost_and_found/state.py](Frontend/ptit_lost_and_found/state.py). |
| **JavaScript nhung (rx.script)** | Mo WebSocket `ws://localhost:8000/ws/{user_id}` va kich hoat nut an de **lam moi** chat / thong bao khi co tin tu server. Cung file `ptit_lost_and_found.py`. |

---

## 3. Co so du lieu

### 3.1. Cong nghe va vi tri

- **SQLite**, chuoi ket noi: `sqlite:///./lostfound.db` (file nam trong thu muc **`backend/`** khi chay server tu do).
- **Khoi tao / cap nhat schema**: `Base.metadata.create_all(bind=engine)` trong [backend/app/main.py](backend/app/main.py).

**Bo sung cot cho DB cu** (khong dung Alembic): mot so ham chay khi startup dung `PRAGMA table_info` + `ALTER TABLE` (vi du cot tra loi binh luan `parent_comment_id`, cot ngu canh tin nhan trong bang `messages`). Dieu nay giup may dang giu file `.db` cu van chay duoc voi model moi.

### 3.2. Cac thuc the chinh (model)

Thu muc: [backend/app/models/](backend/app/models/)

| Model | Bang (uoc luong) | Vai tro nghiep vu |
|-------|------------------|-----------------|
| **User** | `users` | Tai khoan: `username`, `email`, `password_hash`, **`role`** (`USER` / `ADMIN`), thoi gian tao. Quan he: bai viet, binh luan, thong bao, tin nhan. |
| **Post** | `posts` | Bai dang: tieu de, mo ta, loai LOST/FOUND, danh muc, khu vuc, lien he, anh, luot xem, **`is_resolved`**, **`moderation_status`** (PENDING / APPROVED / REJECTED / REMOVED), ghi chu duyet, nguoi duyet, thoi diem duyet. |
| **Comment** | `comments` | Binh luan theo bai; ho tro **tra loi long nhau** (`parent_comment_id`). |
| **Message** | `messages` | Tin nhan giua hai user; truong ngu canh bai (`post_id`, `post_title`, `message_type`) phuc vu banner trong chat. |
| **Notification** | `notifications` | Thong bao gan user. |
| **Report** | `reports` | Bao cao vi pham, trang thai xu ly. |
| **SavedPost** | (bang luu bai) | Quan he user — bai da luu. |

Quan he chi tiet khai bao bang `relationship` va `ForeignKey` trong tung model; frontend **khong** truy cap truc tiep SQLite.

### 3.3. Tac vu nen lien quan DB

- **Don bai da go**: bien `REMOVED_POST_RETENTION_DAYS` (mac dinh 14 ngay) de xoa cung bai `REMOVED` qua han khi khoi dong backend.

---

## 4. Cau truc frontend va thanh phan chuc nang

Thu muc goi package: [Frontend/ptit_lost_and_found/](Frontend/ptit_lost_and_found/)

### 4.1. Thanh phan khung

| Thanh phan | File | Chuc nang |
|------------|------|-----------|
| **Ung dung & layout** | [ptit_lost_and_found.py](Frontend/ptit_lost_and_found/ptit_lost_and_found.py) | Dinh nghia `base_layout`: navbar, sidebar, footer, chatbox; dang ky route tung trang; nhung Tailwind; **WebSocket client** va nut dong bo chat/thong bao. |
| **State tap trung** | [state.py](Frontend/ptit_lost_and_found/state.py) | `AppState`: token JWT, user id, `api_base_url`, form dang nhap/dang ky, tai feed, tim kiem, CRUD bai, binh luan, tin nhan, thong bao, admin, bao cao, luu bai — **moi loi goi HTTP toi FastAPI** tap trung o day (httpx). |

### 4.2. Trang (`pages/`)

| File | Chuc nang giao dien |
|------|---------------------|
| `auth.py` | Dang nhap, dang ky. |
| `home.py` | Trang chu / ban tin (feed). |
| `search.py` | Tim kiem va loc bai. |
| `post_create.py` | Tao bai moi (form + anh). |
| `post_detail.py` | Chi tiet bai, binh luan, hanh dong (luu, bao cao, lien he, …). |
| `manage_post.py` | Quan ly bai cua user hien tai. |
| `saved_posts.py` | Bai da luu. |
| `profile.py` | Trang ca nhan va danh sach bai theo user. |
| `notifications.py` | Danh sach thong bao. |
| `admin.py` | Duyet bai, bai da go, danh sach bao cao (admin). |
| `system_status.py` | Trang thai / kiem tra he thong (neu dung trong demo). |
| `placeholders.py` | Trang giu cho (neu con dung). |

### 4.3. Thanh phan dung lai (`components/`)

| File | Chuc nang |
|------|-----------|
| `navbar.py` | Thanh dieu huong, menu tai khoan. |
| `footer.py` | Chan trang. |
| `latest_news.py` | Khoi hien thi danh sach bai (card) tren feed. |
| `reddit_layout.py` | Bo cuc cot trai / cot phai (sidebar, panel phu). |
| `chatbox.py` | Popup / khung chat, lien ket state tin nhan. |

---

## 5. API backend va lien ket voi frontend

### 5.1. Nguyen tac lien ket

- Frontend biet **URL goc API** (mac dinh `http://localhost:8000` trong `AppState`) va cac **duong dan REST** + **WebSocket**.
- Sau dang nhap, backend tra **JWT**; frontend luu token va gui header **`Authorization: Bearer <token>`** cho route can xac thuc.
- Upload anh tao bai: thuong la **multipart/form-data** (`Form` + `File`) toi nhom `/posts`.
- Anh luu cuc bo hien thi qua URL dang `http://localhost:8000/uploads/...` (ghep voi `api_base_url`).

### 5.2. Nhom router (prefix)

Cac router gan vao app trong [backend/app/main.py](backend/app/main.py):

| Prefix | File | Nghiep vu tuong ung tren frontend |
|--------|------|-----------------------------------|
| `/auth` | [auth_router.py](backend/app/routers/auth_router.py) | Dang ky, dang nhap, lay thong tin user hien tai. |
| `/posts` | [post_router.py](backend/app/routers/post_router.py) | Danh sach bai, tao/sua/xoa (soft), tim kiem, duyet, bai cua toi, upload anh. |
| `/comments` | [comment_router.py](backend/app/routers/comment_router.py) | Binh luan, tra loi. |
| `/messages` | [message_router.py](backend/app/routers/message_router.py) | Gui tin, lich su chat, danh sach hoi thoai; co the ket hop thong bao realtime qua WebSocket. |
| `/notifications` | [notification_router.py](backend/app/routers/notification_router.py) | Doc / danh dau da doc thong bao. |
| `/users` | [user_router.py](backend/app/routers/user_router.py) | Ho so user va bai dang cong khai theo id. |
| `/reports` | [report_router.py](backend/app/routers/report_router.py) | Gui va xu ly bao cao (admin). |
| `/saved-posts` | [saved_post_router.py](backend/app/routers/saved_post_router.py) | Luu / bo luu / liet ke bai da luu. |

Ngoai ra trong [main.py](backend/app/main.py):

- **`GET /docs`**, **`GET /openapi.json`**: tai lieu API.
- **`WebSocket /ws/{user_id}`**: client frontend (trong `base_layout`) ket noi sau dang nhap de nhan su kien va lam moi UI.

### 5.3. CORS

Backend chi cho phep mot so origin (localhost Reflex/Vite) trong cau hinh CORS; khi trien khai that can chinh lai danh sach origin cho khop domain.

---

## 6. Ket luan va pham vi demo

Du an ket hop **FastAPI + SQLite + JWT + WebSocket** voi **Reflex + httpx**, du de demo luong: dang tin, duyet, tuong tac, tin nhan va thong bao. SQLite mot file phu hop do an; huong production thuong chuyen sang PostgreSQL/MySQL, them migration chuan (Alembic) va cung co bao mat (HTTPS, rate limit, …).

---

*Bao cao nay mo ta kien truc tai thoi diem soan. Chi tiet cai dat va lenh chay xem [README.md](README.md).*
