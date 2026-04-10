# Frontend (Reflex)

## Run

Dung chung virtualenv o thu muc goc repo (xem `../README.md`). Vi du:

```bash
cd ~/ptit_lost_and_found
source .venv/bin/activate
cd Frontend
python -m pip install -r requirements.txt   # lan dau hoac sau khi doi deps
python -m reflex run                          # dung -m de tranh loi .venv/bin/reflex tren WSL
```

## Notes

- Day la skeleton de giu layout/CSS truoc.
- Da migrate cac page chinh: home, search, post detail, login/register, profile, manage-post, messages.
- Da migrate trang dang tin `/post`, ho tro submit multipart (co file anh).
- Chat co 2 cach dung:
  - Popup chat tu Navbar
  - Trang day du: `/messages`
- Backend FastAPI giu nguyen trong `backend/`.
- Trang thai hien tai:
  - Auth persistence: done
  - CRUD chinh: done (khong gom edit post)
  - Chat realtime websocket push: chua parity 100% (dang manual refresh/on-demand)

## Quick test checklist

- Dang nhap/Dang ky:
  - `/register` -> tao tai khoan
  - `/login` -> login thanh cong, reload trang van giu session
- Bai dang:
  - `/` thay danh sach LOST/FOUND
  - `/search` loc/tim ra ket qua
  - `/post/{id}` xem chi tiet va gui binh luan (khi dang nhap)
  - `/post` dang tin moi (co/khong co anh)
- Ho so:
  - `/profile` xem profile cua minh
  - `/user/{id}` xem profile nguoi khac
- Quan ly bai dang:
  - `/manage-post` load bai cua minh, xoa bai
- Tin nhan:
  - mo popup tu Navbar hoac vao `/messages`
  - xem hoi thoai, gui tin nhan, bam `Lam moi`/`↻` de dong bo nhanh
- Thong bao:
  - dropdown notifications tren navbar hoat dong
  - `/notifications` xem day du, mark read tung cai/mark all

## Handover docs

- Checklist nghiem thu/chot trang thai chinh: `../MIGRATION_STATUS.md`
- Tai lieu migration cu (archive): `../docs/archive/migration/`

## Ops utility

- Route `/system-status`:
  - `Run Health Check` de kiem tra ket noi backend nhanh
  - link mo `http://127.0.0.1:8000/docs`

