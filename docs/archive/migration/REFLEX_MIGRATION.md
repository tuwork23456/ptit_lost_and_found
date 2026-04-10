# Reflex Migration Guide (Production-Ready)

Muc tieu: giu nguyen backend FastAPI va giu nguyen giao dien hien tai, chi thay frontend framework tu React sang Reflex.

## 1) Scope and non-scope

### In scope

- Giu backend trong `backend/` (khong doi API routes).
- Giu layout/CSS hien tai tu `frontend/src/index.css`.
- Migrate tat ca routes va business flow sang Reflex:
  - Home
  - Post
  - Manage Post (private)
  - Login
  - Register
  - Search
  - Post Detail
  - Profile
  - ChatBox global khi da login

### Out of scope (phase sau)

- Thay doi lon ve UI/UX.
- Refactor API backend.
- Toi uu hieu nang sau khi parity da dat.

## 2) Architecture mapping (React -> Reflex)

- Router:
  - React `react-router-dom` -> Reflex `@rx.page` + dynamic route params
- Global state:
  - `AppContext` -> `rx.State` (auth/user/loading/error)
- API layer:
  - `axios` services -> `httpx`/`requests` trong state actions hoac service module Python
- Protected routes:
  - `<Navigate />` -> guard trong state + `rx.redirect(...)`
- Layout:
  - `Navbar/Footer/ChatBox` -> reusable component functions trong Reflex
- Side effects:
  - `useEffect` -> Reflex event lifecycle / explicit action methods

## 3) File mapping

- `frontend/src/App.jsx` -> `frontend_reflex/<app_name>/<app_name>.py`
- `frontend/src/components/Navbar.jsx` -> `frontend_reflex/<app_name>/components/navbar.py`
- `frontend/src/components/Footer.jsx` -> `frontend_reflex/<app_name>/components/footer.py`
- `frontend/src/components/ChatBox.jsx` -> `frontend_reflex/<app_name>/components/chatbox.py`
- `frontend/src/pages/*.jsx` -> `frontend_reflex/<app_name>/pages/*.py`
- `frontend/src/services/*.js` -> `frontend_reflex/<app_name>/services/*.py`
- `frontend/src/index.css` -> `frontend_reflex/assets/styles.css`

## 4) Delivery plan (3 phases)

### Phase 1 - Foundation and visual parity

1. Tao project `frontend_reflex/`.
2. Add base config + env mapping.
3. Port `styles.css` va global layout.
4. Dung shell routes va static components (`Navbar`, `Footer`).
5. Confirm visual parity for shared layout.

Gate de qua phase 2:
- Layout trung >= 95% (spacing, font, colors, component positions).
- Route skeleton hoat dong.

### Phase 2 - Functional parity per page

1. Migrate pages public:
   - Home -> Search -> Post Detail
2. Migrate auth:
   - Login -> Register
3. Migrate pages private:
   - Post -> Manage Post -> Profile
4. Migrate ChatBox + notifications (milestone rieng).

Gate de qua phase 3:
- Tat ca API calls hoat dong.
- Auth flow va private route guard dung.
- Chat/notification khong loi nghiem trong.

### Phase 3 - Hardening and cutover

1. Smoke test full flow.
2. Bugfix round.
3. Chay song song React + Reflex (staging/prod canary).
4. Cutover route chinh sang Reflex.
5. Giu rollback switch ve React trong 1 release cycle.

## 5) Per-page migration checklist

Ap dung cho moi page:

1. Route + params parity.
2. UI structure parity (dom/component hierarchy).
3. CSS classes parity (khong doi class neu khong can thiet).
4. API integration parity (request payload, query, headers).
5. State parity (loading, empty, error, success).
6. Action parity (button/form/nav behavior).
7. Edge cases (unauthorized, not found, network fail).

## 6) Critical risk areas and controls

### A) Auth persistence

- Chot chien luoc token/session ngay tu dau:
  - uu tien cookie httpOnly neu backend ho tro;
  - neu dung token client-side, can policy ro rang cho refresh/expire/logout.
- Test reload page, multi-tab, token expiration.

### B) WebSocket / ChatBox

- Tach thanh milestone rieng:
  - connect/disconnect/reconnect
  - mapping user-room
  - duplicate message guard
- Fallback UX neu socket fail (retry and visible error).

### C) Upload media / Cloudinary

- Validate multipart upload trong Reflex.
- Test file size/type validation and preview behavior.

### D) Env and CORS

- Define ro:
  - `API_BASE_URL`
  - `WS_BASE_URL`
  - `APP_ENV`
- Kiem tra CORS headers cho host Reflex.

## 7) Test strategy

### Minimum smoke suite (bat buoc)

- Auth:
  - register -> login -> logout
- Post flow:
  - create -> edit -> delete post
- Interaction:
  - comment create/delete
  - search with keyword
- Profile:
  - view/update own profile
- Messaging:
  - open chat, send/receive basic message

### Regression checkpoints

- Sau moi page migrated, chay smoke subset.
- Truoc cutover, chay full smoke + manual UI diff.

## 8) Cutover and rollback plan

### Cutover

- Deploy Reflex app tren endpoint moi (staging truoc).
- Route traffic nho (canary) sang Reflex.
- Monitor logs + error rate + auth/chat success.
- Tang traffic dan den 100%.

### Rollback

- Giu frontend React deploy song song.
- Neu loi nghiem trong:
  - switch traffic ve React ngay (reverse proxy / deploy alias).
- Document trigger rollback:
  - auth fail rate cao
  - chat outage
  - major page inaccessible

## 9) Definition of done

- UI match >= 95% compared voi React.
- Tat ca route trong `App.jsx` da co page Reflex tuong ung.
- Private route guard dung.
- CRUD post/comment/message/notification hoat dong.
- Khong blocker ve CORS/auth/socket.
- Co runbook van hanh + rollback da duoc test.

## 10) Current migration status

### Done in `frontend_reflex`

- Core:
  - App shell + routing + shared layout
  - CSS migration (`assets/styles.css`)
  - Auth persistence (`rx.LocalStorage`) + logout
- Pages:
  - `/` Home (load posts)
  - `/search`
  - `/post/[id]` + comments
  - `/post` (create post, including multipart upload)
  - `/login`, `/register`
  - `/manage-post`
  - `/profile`, `/user/[id]`
  - `/messages`
  - `/notifications`
  - `/system-status`
- Messaging:
  - Popup chat + full page chat
  - Conversations/history/send/read/unread APIs

### Remaining gaps

- WebSocket real-time push parity (current chat refresh is manual/on-demand).
- Notification UX improved (dropdown + page), realtime push parity still pending.
- Final visual polish and edge-case parity per page.

## 11) Runbook (target)

- Backend:
  - `cd backend`
  - `source venv/bin/activate`
  - `uvicorn app.main:app --reload`
- Reflex frontend:
  - `cd frontend_reflex`
  - `reflex run`
