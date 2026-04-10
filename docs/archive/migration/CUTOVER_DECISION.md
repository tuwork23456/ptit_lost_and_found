# Cutover Decision (React -> Reflex)

Tai lieu nay dung de quyet dinh **Go / No-go** truoc khi thay frontend React bang Reflex.

## Current recommendation

- Decision: **NO-GO (tam thoi)**
- Ly do:
  - Chat realtime websocket chua parity 100% (hien tai on-demand/manual refresh la chinh).
  - Can chay full UAT checklist tren moi truong staging truoc cutover.

## Decision matrix

| Area | Status | Notes |
|---|---|---|
| Auth (login/register/persist/logout) | PASS | Da migrate va co guard route private |
| Browse (home/search/detail) | PASS | API core hoat dong |
| Post flows (create/delete/resolve/report/comment) | PASS | Da ho tro multipart upload |
| Profile (self/public) | PASS | `/profile` va `/user/[id]` da co |
| Messaging basic APIs | PASS | conversations/history/send/read co |
| Messaging realtime parity | PARTIAL | Chua websocket parity day du |
| Notifications | PASS | Dropdown + page + mark read/all |
| System ops check | PASS | `/system-status` da co health check |

## Go criteria

- [ ] Pass toan bo checklist trong `MIGRATION_STATUS.md`
- [ ] Chat realtime parity dat muc chap nhan duoc cho production
- [ ] Khong con bug blocker (P0/P1)
- [ ] Team xac nhan UAT pass
- [ ] Rollback plan duoc rehearse

## Rollout plan (when GO)

1. Deploy Reflex tren staging, chay smoke + UAT.
2. Canary 10-20% traffic.
3. Monitor error rate, auth success, messaging behavior.
4. Tang traffic dan toi 100%.
5. Giu rollback ve React trong 1 release cycle dau.

## Owner sign-off

- Product:
- Tech lead:
- QA:
- Release manager:
- Planned cutover date:
