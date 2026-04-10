# UAT Evidence Pack (Go/No-go Final)

Tai lieu nay quy dinh bang chung toi thieu de chot cutover React -> Reflex.

## 1) Folder structure de nop evidence

Tao thu muc:

```text
uat-evidence/
  auth/
  browse/
  post/
  profile/
  messaging/
  notifications/
  ops/
  logs/
```

## 2) Required artifacts

### A. Auth

- `auth/register-success.png`
- `auth/login-success.png`
- `auth/reload-still-logged-in.png`
- `auth/logout-success.png`

### B. Browse

- `browse/home-feed.png`
- `browse/search-filter-result.png`
- `browse/post-detail-open.png`

### C. Post actions

- `post/create-no-image-success.png`
- `post/create-with-image-success.png`
- `post/comment-success.png`
- `post/resolve-owner-success.png`
- `post/report-success.png`

### D. User area

- `profile/profile-self.png`
- `profile/profile-other.png`
- `post/manage-post-list.png`
- `post/manage-post-delete-success.png`

### E. Messaging

- `messaging/popup-open.png`
- `messaging/messages-page.png`
- `messaging/send-message-success.png`
- `messaging/unread-badge-update.png`
- `messaging/ws-push-refresh.mp4` (ngan, 10-30s)

### F. Notifications

- `notifications/dropdown-open.png`
- `notifications/notifications-page.png`
- `notifications/mark-one-success.png`
- `notifications/mark-all-success.png`

### G. Ops

- `ops/system-status-ok.png`
- `ops/api-docs-open.png`

### H. Logs

- `logs/backend.log` (doan trong luc test)
- `logs/frontend_reflex.log` (doan trong luc test)

## 3) Pass criteria

- 100% file bat buoc ton tai.
- Khong co blocker P0/P1 trong qua trinh test.
- `UAT_REPORT.md` duoc cap nhat day du va recommendation = GO.

## 4) Suggested command capture

Backend log:

```bash
cd backend
source venv/bin/activate
uvicorn app.main:app --reload 2>&1 | tee ../uat-evidence/logs/backend.log
```

Frontend log:

```bash
cd frontend_reflex
source .venv/bin/activate
reflex run 2>&1 | tee ../uat-evidence/logs/frontend_reflex.log
```

## 5) Final sign-off checklist

- [ ] Evidence pack du file
- [ ] `UAT_REPORT.md` cap nhat ket qua thuc te
- [ ] `CUTOVER_DECISION.md` doi sang GO
- [ ] Team sign-off (Product/QA/Tech lead)
