# UI Parity Checklist (React vs Reflex)

Muc tieu: doi chieu nhanh giao dien `frontend/` (React) va `frontend_reflex/` (Reflex) truoc khi cutover.

## 1) Layout and visual tokens

- [ ] Navbar height, spacing, button styles giong ban React
- [ ] Footer typography va spacing giong ban React
- [ ] Background tones (`#f0f2f5`, `#f8fafc`) dung dung
- [ ] Card radius/shadow dong bo giua 2 ban
- [ ] Badge colors (LOST/FOUND, notification badges) dung voi React

## 2) Page-by-page UI

- [ ] `/` Home: hero/news cards spacing + typography
- [ ] `/search`: search bar, filters, list cards, pagination
- [ ] `/post/[id]`: image/info/comments/action blocks
- [ ] `/post`: create form groups + input hierarchy
- [ ] `/manage-post`: row cards + action buttons
- [ ] `/profile`, `/user/[id]`: cover card + post grid
- [ ] `/messages`: conversation list + thread layout
- [ ] `/notifications`: list spacing + unread highlighting
- [ ] `/system-status`: utility panel legibility

## 3) Interaction parity

- [ ] Hover/focus states khong bi vo layout
- [ ] Loading states ro rang, khong nhay layout
- [ ] Error/success banners hien dung vi tri
- [ ] Empty states wording dung ngu canh

## 4) Mobile/responsive sanity

- [ ] Navbar khong vo tren man hinh hep
- [ ] Cards xuong dong dung
- [ ] Form controls de tap/click
- [ ] Chat popup khong che buttons quan trong

## 5) Sign-off

- UI parity target: **>=95%**
- Reviewer:
- Date:
- Notes:
