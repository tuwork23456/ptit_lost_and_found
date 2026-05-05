import re
import asyncio
import reflex as rx
import httpx
import base64


class AppState(rx.State):
    """App state for phase 2 migration."""

    token: str = rx.LocalStorage("")
    username: str = rx.LocalStorage("")
    user_id: str = rx.LocalStorage("")
    user_email: str = rx.LocalStorage("")
    user_role: str = rx.LocalStorage("USER")
    login_email: str = ""
    login_password: str = ""
    register_username: str = ""
    register_email: str = ""
    register_password: str = ""
    register_confirm_password: str = ""
    error_message: str = ""
    success_message: str = ""
    loading: bool = False
    posts: list[dict] = []
    posts_loading: bool = False
    search_query: str = ""
    selected_type: str = "Tất cả loại tin"
    selected_category: str = "Tất cả danh mục"
    selected_location: str = "Tất cả khu vực"
    current_page: int = 1
    items_per_page: int = 6
    search_total: int = 0
    search_results: list[dict] = []
    search_request_seq: int = 0
    feed_filter: str = "LOST"
    feed_page: int = 1
    feed_items_per_page: int = 4
    feed_comment_post_id: int = 0
    show_feed_comments_modal: bool = False
    feed_comments: list[dict] = []
    feed_comment_text: str = ""
    feed_reply_parent_id: int = 0
    feed_reply_target_name: str = ""
    feed_reply_text: str = ""
    feed_comment_post_title: str = ""
    feed_comment_post_owner: str = ""
    feed_comment_post_owner_id: int = 0
    feed_comment_post_description: str = ""
    feed_comment_post_image: str = ""
    feed_comment_post_created_at: str = ""
    feed_report_post_id: int = 0
    feed_report_reason: str = ""
    feed_action_message: str = ""
    current_post: dict = {}
    post_comments: list[dict] = []
    post_loading: bool = False
    comment_text: str = ""
    post_reply_parent_id: int = 0
    post_reply_target_name: str = ""
    post_reply_text: str = ""
    my_posts: list[dict] = []
    profile_data: dict = {}
    profile_loading: bool = False
    is_chat_open: bool = False
    chat_view: str = "list"
    conversations: list[dict] = []
    conversations_loading: bool = False
    current_chat_receiver_id: int = 0
    current_chat_receiver_name: str = ""
    chat_messages: list[dict] = []
    chat_scroll_tick: int = 0
    current_chat_pinned_post: dict = {}
    chat_input: str = ""
    unread_message_count: int = 0
    message_ping_active: bool = False
    notifications: list[dict] = []
    show_notifications: bool = False
    show_messages_menu: bool = False
    show_account_menu: bool = False
    create_post_type: str = "LOST"
    create_post_title: str = ""
    create_post_description: str = ""
    create_post_category: str = ""
    create_post_location: str = ""
    create_post_custom_location: str = ""
    create_post_contact: str = ""
    create_post_custom_category: str = ""
    create_post_image_preview: str = ""
    report_reason: str = ""
    post_action_message: str = ""
    show_post_report_box: bool = False
    post_report_mode: str = "report"
    health_status: str = "unknown"
    health_message: str = ""
    saved_post_ids_data: list[int] = []
    saved_posts: list[dict] = []
    image_debug_samples: list[str] = []

    # Admin state
    admin_pending_posts: list[dict] = []
    admin_reports: list[dict] = []
    admin_removed_posts: list[dict] = []
    admin_locked_users: list[dict] = []
    admin_loading: bool = False
    admin_tab: str = "posts"  # "posts" | "reports" | "removed" | "locked_users"
    admin_action_message: str = ""

    api_base_url: str = "http://localhost:8000"
    unread_badge_clear_delay_sec: float = 0.35
    chat_realtime_autoread_delay_sec: float = 1.2

    def _api_candidates(self) -> list[str]:
        base = str(self.api_base_url or "http://localhost:8000").rstrip("/")
        candidates: list[str] = [base]
        if base.endswith(":8000"):
            candidates.append(base[:-5] + ":8001")
            candidates.append(base[:-5] + ":8002")
        elif base.endswith(":8001"):
            candidates.append(base[:-5] + ":8000")
            candidates.append(base[:-5] + ":8002")
        elif base.endswith(":8002"):
            candidates.append(base[:-5] + ":8000")
            candidates.append(base[:-5] + ":8001")
        else:
            candidates.extend(["http://localhost:8000", "http://localhost:8001", "http://localhost:8002"])
        deduped: list[str] = []
        for item in candidates:
            if item and item not in deduped:
                deduped.append(item)
        return deduped

    async def _request_json(
        self,
        method: str,
        path: str,
        *,
        params: dict | None = None,
        data: dict | None = None,
        json: dict | None = None,
        files: dict | None = None,
        headers: dict | None = None,
        timeout: float = 15.0,
    ) -> dict | list:
        req_headers = dict(headers or {})
        last_exc: Exception | None = None
        for base in self._api_candidates():
            try:
                async with httpx.AsyncClient(timeout=timeout) as client:
                    resp = await client.request(
                        method,
                        f"{base}{path}",
                        params=params,
                        data=data,
                        json=json,
                        files=files,
                        headers=req_headers,
                    )
                    resp.raise_for_status()
                    self.api_base_url = base
                    if resp.status_code == 204 or not resp.content:
                        return {}
                    try:
                        body = resp.json()
                    except ValueError:
                        return {}
                    return body if isinstance(body, (dict, list)) else {}
            except httpx.HTTPStatusError as e:
                last_exc = e
                # Retry alternate base for likely wrong backend port.
                if e.response.status_code == 404:
                    continue
                break
            except httpx.RequestError as e:
                last_exc = e
                continue
        raise last_exc or RuntimeError("Request failed")

    @rx.var
    def is_logged_in(self) -> bool:
        return bool(self.token and self.user_id)

    @rx.var
    def is_admin(self) -> bool:
        role = (self.user_role or "").strip().upper()
        return role in {"ADMIN", "MOD"}

    def clear_messages(self) -> None:
        self.error_message = ""
        self.success_message = ""

    @staticmethod
    def _is_empty_location_choice(val: str) -> bool:
        v = (val or "").strip().lower()
        return v in {"", "khong co", "không có"}

    @staticmethod
    def _normalize_comment(comment: dict) -> dict:
        user = comment.get("user") if isinstance(comment, dict) else None
        username = "Ẩn danh"
        if isinstance(user, dict):
            username = str(user.get("username") or "Ẩn danh")
        elif comment.get("username"):
            username = str(comment.get("username"))
        normalized = dict(comment)
        normalized["username"] = username
        parent = normalized.get("parent_comment_id")
        try:
            normalized["parent_comment_id"] = int(parent) if parent is not None else None
        except Exception:
            normalized["parent_comment_id"] = None
        return normalized

    @staticmethod
    def _thread_comments(comments: list[dict]) -> list[dict]:
        if not comments:
            return []
        normalized = [dict(c) for c in comments if isinstance(c, dict)]
        by_parent: dict[int | None, list[dict]] = {}
        for c in normalized:
            parent = c.get("parent_comment_id")
            if parent in (0, "", "0"):
                parent = None
            by_parent.setdefault(parent, []).append(c)

        for group in by_parent.values():
            group.sort(key=lambda x: str(x.get("created_at", "")))

        threaded: list[dict] = []

        def walk(nodes: list[dict], depth: int, reply_to_user: str = "") -> None:
            for node in nodes:
                node_id = node.get("id")
                username = str(node.get("username") or "Ẩn danh")
                item = dict(node)
                item["depth"] = depth
                item["is_reply"] = depth > 0
                item["indent_px"] = min(depth, 6) * 20
                item["reply_to_user"] = reply_to_user
                threaded.append(item)
                walk(by_parent.get(node_id, []), depth + 1, username)

        walk(by_parent.get(None, []), 0)
        return threaded

    def _normalize_post(self, post: dict) -> dict:
        normalized = dict(post) if isinstance(post, dict) else {}
        owner = normalized.get("owner") if isinstance(normalized.get("owner"), dict) else {}
        username = str(owner.get("username") or normalized.get("username") or "Người dùng PTIT")
        normalized["username"] = username
        raw_image = str(normalized.get("image") or normalized.get("image_url") or normalized.get("imagePath") or "").strip()
        normalized["image"] = self._normalize_image_url(raw_image)
        if not normalized["image"] and raw_image and len(self.image_debug_samples) < 10 and raw_image not in self.image_debug_samples:
            self.image_debug_samples.append(raw_image)
        created_raw = str(normalized.get("created_at") or "").strip()
        created_date = created_raw
        created_time = ""
        if "T" in created_raw:
            parts = created_raw.split("T", 1)
            created_date = parts[0]
            created_time = parts[1].split(".", 1)[0] if len(parts) > 1 else ""
        elif " " in created_raw:
            parts = created_raw.split(" ", 1)
            created_date = parts[0]
            created_time = parts[1].split(".", 1)[0] if len(parts) > 1 else ""
        normalized["created_date"] = created_date
        normalized["created_time"] = created_time
        return normalized

    def _normalize_image_url(self, raw_image: str) -> str:
        value = str(raw_image or "").strip().replace("\\", "/")
        if not value:
            return ""
        if "/uploads/" in value and not value.startswith("/uploads/"):
            value = "/uploads/" + value.split("/uploads/")[-1]
        if value.startswith("uploads/"):
            value = "/" + value
        if value.startswith("/"):
            value = f"{self.api_base_url.rstrip('/')}{value}"
        if value.startswith(("http://", "https://", "data:image/")):
            return value
        return ""

    def _normalize_admin_report(self, report: dict) -> dict:
        normalized = dict(report) if isinstance(report, dict) else {}
        post_obj = normalized.get("post")
        if isinstance(post_obj, dict):
            # Always prefer nested post.id from backend relation to avoid
            # mismatched top-level ids in some responses.
            nested_pid = post_obj.get("id")
            if nested_pid not in (None, "", 0):
                try:
                    normalized["post_id"] = int(nested_pid)
                except Exception:
                    pass
            normalized["post_title"] = str(post_obj.get("title") or normalized.get("post_title") or "").strip()
            normalized["post_description"] = str(post_obj.get("description") or normalized.get("post_description") or "").strip()
            normalized["post_category"] = str(post_obj.get("category") or normalized.get("post_category") or "Uncategorized").strip()
            normalized["post_type"] = str(post_obj.get("type") or normalized.get("post_type") or "").strip()
            try:
                normalized["post_user_id"] = int(post_obj.get("user_id") or normalized.get("post_user_id") or 0)
            except Exception:
                normalized["post_user_id"] = 0
            report_raw_image = str(post_obj.get("image") or normalized.get("post_image") or "").strip()
            normalized["post_image"] = self._normalize_image_url(report_raw_image)
            normalized["post_location"] = str(post_obj.get("location") or normalized.get("post_location") or "").strip()
            owner_obj = post_obj.get("owner") if isinstance(post_obj.get("owner"), dict) else {}
            owner_active_raw = owner_obj.get("is_active", normalized.get("post_owner_active"))
            if owner_active_raw is None:
                normalized["post_owner_active"] = None
            else:
                normalized["post_owner_active"] = bool(owner_active_raw)
            created_raw = str(post_obj.get("created_at") or normalized.get("post_created_at") or "").strip()
            created_date = created_raw
            created_time = ""
            if "T" in created_raw:
                parts = created_raw.split("T", 1)
                created_date = parts[0]
                created_time = parts[1].split(".", 1)[0] if len(parts) > 1 else ""
            elif " " in created_raw:
                parts = created_raw.split(" ", 1)
                created_date = parts[0]
                created_time = parts[1].split(".", 1)[0] if len(parts) > 1 else ""
            normalized["post_created_date"] = created_date
            normalized["post_created_time"] = created_time
        rep = normalized.get("reporter")
        uname = "Người dùng"
        if isinstance(rep, dict):
            u = rep.get("username")
            if u is not None and str(u).strip():
                uname = str(u).strip()
        normalized["reporter_username"] = uname
        return normalized

    @staticmethod
    def _is_post_resolved(post: dict) -> bool:
        if not isinstance(post, dict):
            return False
        value = post.get("is_resolved")
        if isinstance(value, bool):
            return value
        if isinstance(value, int):
            return value == 1
        if isinstance(value, str):
            normalized = value.strip().lower()
            return normalized in {"1", "true", "yes"}
        return False

    def _saved_ids(self) -> list[int]:
        return [int(x) for x in self.saved_post_ids_data]

    def _set_saved_ids(self, ids: list[int]) -> None:
        self.saved_post_ids_data = sorted({int(x) for x in ids if int(x) > 0})

    async def load_posts(self) -> None:
        self.posts_loading = True
        self.error_message = ""
        try:
            data = await self._request_json("GET", "/posts", timeout=15.0)
            raw_posts = data if isinstance(data, list) else []
            self.posts = [self._normalize_post(p) for p in raw_posts]
        except Exception:
            self.error_message = "Không tải được danh sách bài viết."
            self.posts = []
        finally:
            self.posts_loading = False

    async def load_search_posts(self) -> None:
        self.search_request_seq += 1
        req_id = self.search_request_seq
        self.posts_loading = True
        self.error_message = ""
        try:
            selected_type = ""
            if self.selected_type == "Mất đồ":
                selected_type = "LOST"
            elif self.selected_type == "Nhặt được":
                selected_type = "FOUND"

            search_category = "" if self.selected_category == "Tất cả danh mục" else self.selected_category
            search_location = "" if self.selected_location == "Tất cả khu vực" else self.selected_location
            per_page = 50

            async def _fetch_all_for_type(type_value: str) -> tuple[list[dict], int]:
                page = 1
                merged: list[dict] = []
                total = 0
                while True:
                    query_params = {
                        "q": self.search_query.strip(),
                        "type": type_value,
                        "category": search_category,
                        "location": search_location,
                        "page": page,
                        "limit": per_page,
                    }
                    data = await self._request_json("GET", "/posts/search", params=query_params, timeout=15.0) or {}

                    if req_id != self.search_request_seq:
                        return [], 0

                    raw_items = data.get("items", []) if isinstance(data, dict) else []
                    total = int(data.get("total", 0)) if isinstance(data, dict) else 0
                    merged.extend(raw_items if isinstance(raw_items, list) else [])
                    if len(raw_items) < per_page or len(merged) >= total:
                        break
                    page += 1
                return merged, total

            if selected_type:
                all_items, total = await _fetch_all_for_type(selected_type)
            else:
                lost_items, lost_total = await _fetch_all_for_type("LOST")
                found_items, found_total = await _fetch_all_for_type("FOUND")
                all_items = lost_items + found_items
                total = lost_total + found_total

                # Deduplicate by id and keep newest first.
                seen: set[int] = set()
                deduped: list[dict] = []
                for row in all_items:
                    pid = int((row or {}).get("id") or 0)
                    if pid > 0 and pid not in seen:
                        seen.add(pid)
                        deduped.append(row)
                all_items = sorted(
                    deduped,
                    key=lambda x: (str((x or {}).get("created_at") or ""), int((x or {}).get("id") or 0)),
                    reverse=True,
                )
                total = len(all_items)

            normalized_results = [self._normalize_post(p) for p in all_items]
            visible_results = [p for p in normalized_results if not self._is_post_resolved(p)]
            self.search_results = visible_results
            self.search_total = len(visible_results)
        except Exception:
            if req_id != self.search_request_seq:
                return
            self.error_message = "Không tải được kết quả tìm kiếm."
            self.search_results = []
            self.search_total = 0
        finally:
            if req_id == self.search_request_seq:
                self.posts_loading = False

    def reset_search_page(self) -> None:
        self.current_page = 1
        self.search_total = 0
        self.search_results = []

    async def reset_search_and_fetch(self) -> None:
        self.current_page = 1
        await self.load_search_posts()

    def set_search_query(self, value: str) -> None:
        self.search_query = value

    async def run_quick_search(self) -> None:
        self.current_page = 1
        await self.load_search_posts()

    async def set_selected_type_and_reset(self, value: str) -> None:
        self.selected_type = value
        self.current_page = 1
        await self.load_search_posts()

    async def set_selected_category_and_reset(self, value: str) -> None:
        self.selected_category = value
        self.current_page = 1
        await self.load_search_posts()

    async def set_selected_location_and_reset(self, value: str) -> None:
        self.selected_location = value
        self.current_page = 1
        await self.load_search_posts()

    @rx.var
    def lost_posts(self) -> list[dict]:
        return [p for p in self.posts if p.get("type") == "LOST"][:8]

    @rx.var
    def found_posts(self) -> list[dict]:
        return [p for p in self.posts if p.get("type") == "FOUND"][:8]

    @rx.var
    def create_post_preview_title(self) -> str:
        category = (
            self.create_post_custom_category.strip()
            if self.create_post_category == "Khác"
            else self.create_post_category.strip()
        )
        location = (
            self.create_post_custom_location.strip()
            if self.create_post_location == "Khác"
            else ("" if self._is_empty_location_choice(self.create_post_location) else self.create_post_location.strip())
        )
        if not category:
            category = "đồ vật"
        prefix = "Tìm" if self.create_post_type == "LOST" else "Nhặt được"
        return f"{prefix} {category}" + (f" tại {location}" if location else "")

    @rx.var
    def available_categories(self) -> list[str]:
        values = sorted({str(p.get("category", "")).strip() for p in self.posts if p.get("category")})
        return ["Tất cả danh mục", *values]

    @rx.var
    def available_locations(self) -> list[str]:
        values = sorted(
            {
                str(p.get("location", "")).strip()
                for p in self.posts
                if p.get("location")
                and str(p.get("location", "")).strip().lower() not in {"khong co", "không có"}
            }
        )
        return ["Tất cả khu vực", *values]

    @rx.var
    def filtered_posts(self) -> list[dict]:
        return self.search_results

    @rx.var
    def total_pages(self) -> int:
        total = int(self.search_total)
        return max(1, (total + self.items_per_page - 1) // self.items_per_page)

    @rx.var
    def paginated_posts(self) -> list[dict]:
        return self.search_results

    async def next_page(self) -> None:
        if self.current_page < self.total_pages:
            self.current_page += 1
            await self.load_search_posts()

    async def prev_page(self) -> None:
        if self.current_page > 1:
            self.current_page -= 1
            await self.load_search_posts()

    async def goto_page(self, page: int) -> None:
        if 1 <= page <= self.total_pages:
            self.current_page = page
            await self.load_search_posts()

    def set_feed_filter(self, value: str) -> None:
        self.feed_filter = value
        self.feed_page = 1

    @rx.var
    def feed_filtered_posts(self) -> list[dict]:
        saved = set(self._saved_ids())
        visible_posts = [p for p in self.posts if not self._is_post_resolved(p)]
        if self.feed_filter == "FOUND":
            posts = [p for p in visible_posts if p.get("type") == "FOUND"]
        else:
            posts = [p for p in visible_posts if p.get("type") == "LOST"]
        result = []
        for p in posts:
            item = dict(p)
            pid = int(item.get("id", 0) or 0)
            item["is_saved"] = pid in saved
            result.append(item)
        return result

    @rx.var
    def feed_threaded_comments(self) -> list[dict]:
        return self._thread_comments(self.feed_comments)

    @rx.var
    def feed_total_pages(self) -> int:
        total = len(self.feed_filtered_posts)
        return max(1, (total + self.feed_items_per_page - 1) // self.feed_items_per_page)

    @rx.var
    def feed_paginated_posts(self) -> list[dict]:
        start = (self.feed_page - 1) * self.feed_items_per_page
        end = start + self.feed_items_per_page
        return self.feed_filtered_posts[start:end]

    @rx.var
    def feed_page_numbers(self) -> list[int]:
        return list(range(1, self.feed_total_pages + 1))

    @rx.var
    def post_threaded_comments(self) -> list[dict]:
        return self._thread_comments(self.post_comments)

    @rx.var
    def saved_post_ids(self) -> list[int]:
        return self._saved_ids()

    @rx.var
    def is_current_post_saved(self) -> bool:
        pid = int(self.current_post.get("id", 0) or 0)
        return pid > 0 and pid in set(self._saved_ids())

    def goto_feed_page(self, page: int) -> None:
        if 1 <= page <= self.feed_total_pages:
            self.feed_page = page

    @staticmethod
    def _form_value(form_data: dict | None, key: str, fallback: str = "") -> str:
        """Read a field from Reflex rx.form submit payload (FormData + refs)."""
        if not form_data:
            return fallback
        v = form_data.get(key)
        if isinstance(v, list):
            v = v[0] if v else None
        if v is None:
            return fallback
        s = str(v).strip()
        return s if s else fallback

    async def submit_login(self, form_data: dict | None = None):
        self.loading = True
        self.clear_messages()
        try:
            email = self._form_value(form_data, "email", self.login_email).strip().lower()
            password = self._form_value(form_data, "password", self.login_password)
            if not email or not password:
                self.error_message = "Vui lòng nhập đầy đủ email và mật khẩu."
                return
            payload = {"email": email, "password": password}
            login_urls = [f"{b.rstrip('/')}/auth/login" for b in self._api_candidates()]

            data = None
            last_error = None
            async with httpx.AsyncClient(timeout=15.0) as client:
                for url in login_urls:
                    try:
                        resp = await client.post(url, json=payload)
                        resp.raise_for_status()
                        data = resp.json()
                        host = url.split("/auth/login")[0]
                        if host:
                            self.api_base_url = host
                        break
                    except httpx.HTTPStatusError as e:
                        detail = ""
                        try:
                            body = e.response.json() or {}
                            raw_detail = body.get("detail", "")
                            if isinstance(raw_detail, list):
                                detail = "; ".join(
                                    [str(item.get("msg", item)) for item in raw_detail]
                                )
                            else:
                                detail = str(raw_detail)
                        except Exception:
                            detail = e.response.text
                        code = e.response.status_code
                        if code == 429:
                            self.error_message = (
                                "Đăng nhập thất bại quá nhiều lần. Vui lòng đợi khoảng 15 phút rồi thử lại."
                            )
                        elif code == 422:
                            self.error_message = (
                                "Email hoặc định dạng không hợp lệ. Vui lòng kiểm tra lại."
                            )
                        elif code == 401:
                            self.error_message = "Sai email hoặc mật khẩu. Vui lòng kiểm tra lại."
                        else:
                            self.error_message = str(
                                detail or "Đăng nhập thất bại. Vui lòng kiểm tra lại thông tin."
                            )
                        self.loading = False
                        return
                    except httpx.RequestError as e:
                        last_error = e

            if data is None:
                self.error_message = (
                    "Không kết nối được backend đăng nhập (đã thử cổng 8000/8001). "
                    "Hãy kiểm tra backend đã chạy chưa."
                )
                if last_error:
                    self.error_message = (
                        "Không kết nối được backend đăng nhập. Vui lòng bật backend trước."
                    )
                self.loading = False
                return
            self.token = data.get("access_token", "")
            user = data.get("user") or {}
            self.username = user.get("username", "")
            self.user_id = str(user.get("id", "") or "")
            self.user_email = user.get("email", email)
            self.user_role = str(user.get("role", "USER") or "USER").upper()
            if not self.token:
                self.error_message = "Đăng nhập thất bại: server không trả về token."
                return
            return rx.redirect("/")
        except Exception:
            self.error_message = "Đăng nhập thất bại. Vui lòng thử lại."
        finally:
            self.loading = False

    async def submit_register(self, form_data: dict | None = None):
        self.loading = True
        self.clear_messages()
        username = self._form_value(form_data, "username", self.register_username)
        reg_email = self._form_value(form_data, "email", self.register_email)
        reg_password = self._form_value(form_data, "password", self.register_password)
        reg_confirm = self._form_value(form_data, "confirm_password", self.register_confirm_password)
        self.register_username = username
        self.register_email = reg_email
        self.register_password = reg_password
        self.register_confirm_password = reg_confirm
        if reg_password != reg_confirm:
            self.error_message = "Mật khẩu xác nhận không khớp."
            self.loading = False
            return
        if len(reg_password) < 8:
            self.error_message = "Mật khẩu phải có ít nhất 8 ký tự, gồm chữ hoa, chữ thường và số."
            self.loading = False
            return
        # Đồng bộ validation với backend: phải có chữ hoa, chữ thường và số
        if (
            not re.search(r"[A-Z]", reg_password)
            or not re.search(r"[a-z]", reg_password)
            or not re.search(r"\d", reg_password)
        ):
            self.error_message = "Mật khẩu phải có ít nhất 1 chữ hoa, 1 chữ thường và 1 số."
            self.loading = False
            return
        try:
            payload = {"username": username, "email": reg_email, "password": reg_password}
            register_urls = [f"{b.rstrip('/')}/auth/register" for b in self._api_candidates()]

            ok = False
            async with httpx.AsyncClient(timeout=15.0) as client:
                for url in register_urls:
                    try:
                        resp = await client.post(url, json=payload)
                        resp.raise_for_status()
                        ok = True
                        host = url.split("/auth/register")[0]
                        if host:
                            self.api_base_url = host
                        break
                    except httpx.HTTPStatusError as e:
                        detail = ""
                        try:
                            detail = (e.response.json() or {}).get("detail", "")
                        except Exception:
                            detail = e.response.text
                        self.error_message = str(detail or "Đăng ký thất bại.")
                        self.loading = False
                        return
                    except httpx.RequestError:
                        continue

            if not ok:
                self.error_message = "Không kết nối được backend đăng ký. Vui lòng bật backend trước."
                self.loading = False
                return
            self.success_message = "Đăng ký thành công. Mời bạn đăng nhập."
            return rx.redirect("/login")
        except Exception:
            self.error_message = "Đăng ký thất bại. Email có thể đã tồn tại."
        finally:
            self.loading = False

    async def load_post_detail(self) -> None:
        self.post_loading = True
        self.error_message = ""
        self.current_post = {}
        self.post_comments = []
        self.post_action_message = ""
        self.show_post_report_box = False
        self.post_report_mode = "report"
        self.report_reason = ""
        self.post_reply_parent_id = 0
        self.post_reply_target_name = ""
        self.post_reply_text = ""
        self.post_report_mode = "report"
        post_id = self.router.page.params.get("id")
        if not post_id:
            self.error_message = "Không tìm thấy bài viết."
            self.post_loading = False
            return
        try:
            await self.load_saved_post_ids()
            post_data = await self._request_json("GET", f"/posts/{post_id}", timeout=20.0)
            comments = await self._request_json("GET", f"/comments/post/{post_id}", timeout=20.0)
            self.current_post = self._normalize_post(post_data if isinstance(post_data, dict) else {})
            normalized_comments = [self._normalize_comment(c) for c in comments]
            self.post_comments = sorted(normalized_comments, key=lambda x: x.get("created_at", ""))
        except Exception:
            self.error_message = "Không tải được chi tiết bài viết."
            self.current_post = {}
            self.post_comments = []
        finally:
            self.post_loading = False

    async def submit_comment(self):
        if not self.is_logged_in or not self.token:
            self.error_message = "Vui lòng đăng nhập để bình luận."
            return rx.redirect("/login")
        content = self.comment_text.strip()
        post_id = self.router.page.params.get("id")
        if not content or not post_id:
            return
        try:
            async with httpx.AsyncClient(timeout=15.0) as client:
                resp = await client.post(
                    f"{self.api_base_url}/comments/",
                    json={"content": content, "post_id": int(post_id), "parent_comment_id": None},
                    headers={"Authorization": f"Bearer {self.token}"},
                )
                resp.raise_for_status()
            self.comment_text = ""
            await self.load_post_detail()
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 401:
                return self.logout()
            self.error_message = "Gửi bình luận thất bại."
        except Exception:
            self.error_message = "Gửi bình luận thất bại."

    def set_post_reply_target(self, parent_id: int, target_name: str) -> None:
        self.post_reply_parent_id = int(parent_id) if parent_id else 0
        self.post_reply_target_name = target_name or "người dùng"

    def cancel_post_reply(self) -> None:
        self.post_reply_parent_id = 0
        self.post_reply_target_name = ""
        self.post_reply_text = ""

    async def submit_post_reply_current(self):
        if not self.is_logged_in or not self.token:
            self.error_message = "Vui lòng đăng nhập để trả lời."
            return rx.redirect("/login")
        post_id = self.router.page.params.get("id")
        content = self.post_reply_text.strip()
        if not post_id or not content or not self.post_reply_parent_id:
            return
        try:
            async with httpx.AsyncClient(timeout=15.0) as client:
                resp = await client.post(
                    f"{self.api_base_url}/comments/",
                    json={
                        "content": content,
                        "post_id": int(post_id),
                        "parent_comment_id": int(self.post_reply_parent_id),
                    },
                    headers={"Authorization": f"Bearer {self.token}"},
                )
                resp.raise_for_status()
            self.post_reply_text = ""
            self.post_reply_parent_id = 0
            self.post_reply_target_name = ""
            await self.load_post_detail()
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 401:
                return self.logout()
            self.error_message = "Gửi trả lời thất bại."
        except Exception:
            self.error_message = "Gửi trả lời thất bại."

    async def load_my_posts(self) -> None:
        if not self.is_logged_in or not self.token:
            self.error_message = "Vui lòng đăng nhập."
            return rx.redirect("/login")
        self.posts_loading = True
        try:
            data = await self._request_json(
                "GET",
                "/posts/my",
                headers={"Authorization": f"Bearer {self.token}"},
                timeout=15.0,
            )
            normalized_posts = [self._normalize_post(p) for p in data if isinstance(p, dict)]
            self.my_posts = sorted(normalized_posts, key=lambda x: x.get("created_at", ""), reverse=True)
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 401:
                return self.logout()
            self.error_message = "Không tải được bài đăng của bạn."
            self.my_posts = []
        except Exception:
            self.error_message = "Không tải được bài đăng của bạn."
            self.my_posts = []
        finally:
            self.posts_loading = False

    async def load_saved_post_ids(self) -> None:
        if not self.is_logged_in or not self.token:
            self.saved_post_ids_data = []
            return
        try:
            async with httpx.AsyncClient(timeout=15.0) as client:
                resp = await client.get(
                    f"{self.api_base_url}/saved-posts/ids",
                    headers={"Authorization": f"Bearer {self.token}"},
                )
                resp.raise_for_status()
            data = resp.json() or []
            self.saved_post_ids_data = [int(x) for x in data]
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 401:
                return self.logout()
            self.saved_post_ids_data = []
        except Exception:
            self.saved_post_ids_data = []

    async def toggle_saved_post(self, post_id: int):
        try:
            pid = int(post_id) if post_id else 0
        except Exception:
            pid = 0
        if pid <= 0:
            return
        if not self.is_logged_in or not self.token:
            return rx.redirect("/login")
        is_saved = pid in set(self._saved_ids())
        try:
            async with httpx.AsyncClient(timeout=15.0) as client:
                if is_saved:
                    resp = await client.delete(
                        f"{self.api_base_url}/saved-posts/{pid}",
                        headers={"Authorization": f"Bearer {self.token}"},
                    )
                else:
                    resp = await client.post(
                        f"{self.api_base_url}/saved-posts/{pid}",
                        headers={"Authorization": f"Bearer {self.token}"},
                    )
                resp.raise_for_status()
            await self.load_saved_post_ids()
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 401:
                return self.logout()
        await self.load_saved_posts()

    async def load_saved_posts(self):
        if not self.is_logged_in or not self.token:
            self.saved_posts = []
            return
        try:
            async with httpx.AsyncClient(timeout=15.0) as client:
                resp = await client.get(
                    f"{self.api_base_url}/saved-posts",
                    headers={"Authorization": f"Bearer {self.token}"},
                )
                resp.raise_for_status()
            rows = resp.json() or []
            posts: list[dict] = []
            ids: list[int] = []
            for row in rows:
                post = self._normalize_post((row or {}).get("post") or {})
                if post.get("id"):
                    ids.append(int(post.get("id")))
                    if not self._is_post_resolved(post):
                        posts.append(post)
            self.saved_posts = posts
            self.saved_post_ids_data = sorted(set(ids))
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 401:
                return self.logout()
            self.saved_posts = []
        except Exception:
            self.saved_posts = []

    async def delete_my_post(self, post_id: int):
        if not self.is_logged_in or not self.token:
            return rx.redirect("/login")
        try:
            async with httpx.AsyncClient(timeout=15.0) as client:
                resp = await client.delete(
                    f"{self.api_base_url}/posts/{post_id}",
                    headers={"Authorization": f"Bearer {self.token}"},
                )
                resp.raise_for_status()
            self.my_posts = [p for p in self.my_posts if int(p.get("id", 0)) != int(post_id)]
        except Exception:
            self.error_message = "Xóa bài thất bại."

    async def load_profile(self) -> None:
        self.profile_loading = True
        self.error_message = ""
        target_id = self.router.page.params.get("id")
        if not target_id:
            if not self.is_logged_in:
                self.profile_loading = False
                return rx.redirect("/login")
            target_id = self.user_id if self.user_id else ""
        if not target_id:
            self.profile_loading = False
            self.error_message = "Không tìm thấy người dùng."
            return
        try:
            data = await self._request_json("GET", f"/users/{target_id}", timeout=15.0)
            if isinstance(data, dict):
                normalized_profile = dict(data)
                raw_posts = normalized_profile.get("posts")
                if isinstance(raw_posts, list):
                    profile_username = str(normalized_profile.get("username") or "").strip()
                    profile_user_id = normalized_profile.get("id")
                    normalized_profile["posts"] = [
                        self._normalize_post(
                            {
                                **p,
                                "username": str(p.get("username") or profile_username or ""),
                                "user_id": p.get("user_id") if p.get("user_id") not in (None, "", 0) else profile_user_id,
                            }
                        )
                        for p in raw_posts
                        if isinstance(p, dict)
                    ]
                else:
                    normalized_profile["posts"] = []
                self.profile_data = normalized_profile
            else:
                self.profile_data = {}
        except Exception:
            self.profile_data = {}
            self.error_message = "Không tải được thông tin người dùng."
        finally:
            self.profile_loading = False

    def logout(self):
        self.token = ""
        self.username = ""
        self.user_id = ""
        self.user_email = ""
        self.user_role = "USER"
        self.comment_text = ""
        self.feed_comment_text = ""
        self.feed_reply_parent_id = 0
        self.feed_reply_target_name = ""
        self.feed_reply_text = ""
        self.show_feed_comments_modal = False
        self.current_post = {}
        self.post_comments = []
        self.post_reply_parent_id = 0
        self.post_reply_target_name = ""
        self.post_reply_text = ""
        self.my_posts = []
        self.profile_data = {}
        self.is_chat_open = False
        self.chat_view = "list"
        self.conversations = []
        self.current_chat_receiver_id = 0
        self.current_chat_receiver_name = ""
        self.chat_messages = []
        self.current_chat_pinned_post = {}
        self.chat_input = ""
        self.unread_message_count = 0
        self.clear_messages()
        return rx.redirect("/")

    def toggle_chat(self):
        # Khi mở popup chat thì đóng các dropdown nhỏ trên navbar.
        self.show_messages_menu = False
        self.show_notifications = False
        self.show_account_menu = False
        self.is_chat_open = not self.is_chat_open
        if self.is_chat_open and self.chat_view == "list":
            return AppState.load_conversations
        return None

    def close_chat(self):
        self.is_chat_open = False
        self.chat_view = "list"
        self.current_chat_receiver_id = 0
        self.current_chat_receiver_name = ""
        self.show_notifications = False

    async def load_unread_count(self):
        if not self.is_logged_in:
            self.unread_message_count = 0
            return
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                resp = await client.get(
                    f"{self.api_base_url}/messages/unread-count",
                    headers={"Authorization": f"Bearer {self.token}"},
                )
                resp.raise_for_status()
            self.unread_message_count = int((resp.json() or {}).get("unread_count", 0))
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 401:
                return self.logout()
            self.unread_message_count = 0
        except Exception:
            self.unread_message_count = 0

    async def load_conversations(self):
        if not self.is_logged_in:
            return
        self.conversations_loading = True
        try:
            async with httpx.AsyncClient(timeout=15.0) as client:
                resp = await client.get(
                    f"{self.api_base_url}/messages/conversations",
                    headers={"Authorization": f"Bearer {self.token}"},
                )
                resp.raise_for_status()
            self.conversations = resp.json() or []
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 401:
                return self.logout()
            self.conversations = []
        except Exception:
            self.conversations = []
        finally:
            self.conversations_loading = False

    async def open_chat(self, receiver_id: int, receiver_name: str):
        self.current_chat_receiver_id = receiver_id
        self.current_chat_receiver_name = receiver_name
        self.chat_view = "chat"
        self.is_chat_open = True
        await self.load_chat_history()
        self.chat_scroll_tick += 1
        await self.mark_read(receiver_id)
        await self.load_conversations()

    def back_to_conversations(self):
        self.chat_view = "list"
        self.current_chat_receiver_id = 0
        self.current_chat_receiver_name = ""
        self.chat_messages = []
        self.current_chat_pinned_post = {}
        return AppState.load_conversations

    async def load_chat_history(self):
        if not self.is_logged_in or not self.current_chat_receiver_id:
            return
        try:
            async with httpx.AsyncClient(timeout=15.0) as client:
                resp = await client.get(
                    f"{self.api_base_url}/messages/history/{self.current_chat_receiver_id}",
                    headers={"Authorization": f"Bearer {self.token}"},
                )
                resp.raise_for_status()
            payload = resp.json() or {}
            if isinstance(payload, dict):
                self.chat_messages = payload.get("messages") or []
                self.current_chat_pinned_post = payload.get("pinned_post") or {}
            else:
                # Backward-compat if backend still returns list
                self.chat_messages = payload if isinstance(payload, list) else []
                self.current_chat_pinned_post = {}
            self.chat_scroll_tick += 1
        except Exception:
            self.chat_messages = []
            self.current_chat_pinned_post = {}

    async def mark_read(self, sender_id: int):
        if not self.is_logged_in:
            return
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                resp = await client.put(
                    f"{self.api_base_url}/messages/read/{sender_id}",
                    headers={"Authorization": f"Bearer {self.token}"},
                )
                resp.raise_for_status()
            remaining = int((resp.json() or {}).get("unread_count", 0))
            # Keep badge for a short moment so the UX feels smoother.
            await asyncio.sleep(self.unread_badge_clear_delay_sec)
            self.unread_message_count = remaining
        except Exception:
            pass

    async def send_chat_message(self):
        if not self.is_logged_in or not self.current_chat_receiver_id:
            return
        content = self.chat_input.strip()
        if not content:
            return
        try:
            async with httpx.AsyncClient(timeout=15.0) as client:
                resp = await client.post(
                    f"{self.api_base_url}/messages/send",
                    json={"receiver_id": self.current_chat_receiver_id, "content": content},
                    headers={"Authorization": f"Bearer {self.token}"},
                )
                resp.raise_for_status()
            sent = resp.json() or {}
            self.chat_messages = [*self.chat_messages, sent]
            self.chat_scroll_tick += 1
            self.chat_input = ""
            await self.load_conversations()
        except Exception:
            self.error_message = "Gửi tin nhắn thất bại."

    async def refresh_chat_data(self):
        if self.is_chat_open and self.chat_view == "chat" and self.current_chat_receiver_id:
            # Realtime while user is inside chat:
            # only auto-read when the active conversation itself receives new unread messages.
            await self.load_conversations()
            active_unread = 0
            for conv in self.conversations:
                try:
                    if int(conv.get("id", 0) or 0) == int(self.current_chat_receiver_id):
                        active_unread = int(conv.get("unread_count", 0) or 0)
                        break
                except Exception:
                    continue

            await self.load_unread_count()
            await self.load_notifications()

            if active_unread > 0:
                await asyncio.sleep(self.chat_realtime_autoread_delay_sec)
                await self.load_chat_history()
                await self.mark_read(self.current_chat_receiver_id)
                await self.load_conversations()
            else:
                await self.load_chat_history()
        else:
            await self.load_conversations()
        await self.load_unread_count()
        await self.load_notifications()

    async def trigger_message_ping(self):
        """Show a brief visual ping for incoming messages."""
        self.message_ping_active = True
        await asyncio.sleep(1.5)
        self.message_ping_active = False

    async def init_messages_page(self):
        await self.load_conversations()
        await self.load_unread_count()
        if self.current_chat_receiver_id:
            await self.load_chat_history()

    def toggle_notifications(self):
        self.show_messages_menu = False
        self.show_account_menu = False
        self.show_notifications = not self.show_notifications
        return AppState.load_notifications

    def close_notifications(self):
        self.show_notifications = False

    def toggle_messages_menu(self):
        self.show_notifications = False
        self.show_account_menu = False
        self.show_messages_menu = not self.show_messages_menu
        return AppState.load_conversations

    def close_messages_menu(self):
        self.show_messages_menu = False

    def toggle_account_menu(self):
        self.show_notifications = False
        self.show_messages_menu = False
        self.show_account_menu = not self.show_account_menu

    def close_account_menu(self):
        self.show_account_menu = False

    async def load_notifications(self):
        if not self.is_logged_in:
            self.notifications = []
            return
        try:
            async with httpx.AsyncClient(timeout=15.0) as client:
                resp = await client.get(
                    f"{self.api_base_url}/notifications",
                    headers={"Authorization": f"Bearer {self.token}"},
                )
                resp.raise_for_status()
            self.notifications = resp.json() or []
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 401:
                return self.logout()
            self.notifications = []
        except Exception:
            self.notifications = []

    @rx.var
    def unread_notification_count(self) -> int:
        return len([n for n in self.notifications if not n.get("is_read", False)])

    @rx.var
    def is_current_post_owner(self) -> bool:
        uid = str(self.current_post.get("user_id", ""))
        return bool(uid and self.user_id and uid == self.user_id)

    @rx.var
    def profile_posts(self) -> list[dict]:
        posts = self.profile_data.get("posts", [])
        return posts if isinstance(posts, list) else []

    @rx.var
    def profile_posts_count(self) -> int:
        return len(self.profile_posts)

    async def mark_notification_read_and_open(self, notification_id: int, target_id: int, notif_type: str = ""):
        if not self.is_logged_in:
            return
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                resp = await client.put(
                    f"{self.api_base_url}/notifications/{notification_id}/read",
                    headers={"Authorization": f"Bearer {self.token}"},
                )
                resp.raise_for_status()
            self.notifications = [
                {**n, "is_read": True} if int(n.get("id", 0)) == int(notification_id) else n
                for n in self.notifications
            ]
            self.show_notifications = False
            if (notif_type or "").upper() == "MESSAGE":
                self.is_chat_open = True
                self.chat_view = "list"
                await self.load_conversations()
                await self.load_unread_count()
                return
            if target_id:
                return rx.redirect(f"/post/{target_id}")
        except Exception:
            pass

    async def mark_all_notifications_read(self):
        if not self.is_logged_in:
            return
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                resp = await client.put(
                    f"{self.api_base_url}/notifications/read-all",
                    headers={"Authorization": f"Bearer {self.token}"},
                )
                resp.raise_for_status()
            self.notifications = [{**n, "is_read": True} for n in self.notifications]
        except Exception:
            pass

    async def submit_create_post(self):
        return await self.submit_create_post_with_file([])

    def reset_create_post_form(self) -> None:
        self.loading = False
        self.create_post_type = "LOST"
        self.create_post_title = ""
        self.create_post_description = ""
        self.create_post_category = ""
        self.create_post_location = ""
        self.create_post_custom_location = ""
        self.create_post_contact = ""
        self.create_post_custom_category = ""
        self.create_post_image_preview = ""
        self.clear_messages()

    async def submit_create_post_with_file(self, files: list[rx.UploadFile]):
        if not self.is_logged_in or not self.token:
            self.error_message = "Vui lòng đăng nhập để đăng tin."
            return rx.redirect("/login")

        final_category = (
            self.create_post_custom_category.strip()
            if self.create_post_category == "Khác"
            else self.create_post_category.strip()
        )
        final_location = (
            self.create_post_custom_location.strip()
            if self.create_post_location == "Khác"
            else (
                ""
                if self._is_empty_location_choice(self.create_post_location)
                else self.create_post_location.strip()
            )
        )
        if not final_category:
            self.error_message = "Vui lòng chọn loại đồ."
            return
        if not self.create_post_title.strip():
            self.error_message = "Vui lòng nhập tiêu đề."
            return
        if not self.create_post_description.strip():
            self.error_message = "Vui lòng nhập nội dung."
            return
        if not self.create_post_contact.strip():
            self.error_message = "Vui lòng nhập thông tin liên hệ."
            return

        self.loading = True
        self.clear_messages()
        try:
            payload = {
                "title": self.create_post_title.strip(),
                "description": self.create_post_description.strip(),
                "type": self.create_post_type,
                "category": final_category,
                "location": final_location,
                "contact": self.create_post_contact.strip(),
            }
            file_payload = None
            has_file = False
            if files and len(files) > 0:
                file = files[0]
                file_bytes = await file.read()
                if len(file_bytes) > 5 * 1024 * 1024:
                    self.loading = False
                    self.error_message = "File ảnh quá lớn (tối đa 5MB)."
                    return
                file_payload = {"file": (file.filename, file_bytes, file.content_type or "application/octet-stream")}
                has_file = True
            elif str(self.create_post_image_preview or "").startswith("data:image/"):
                # Fallback path: some Reflex builds may not return upload_files() reliably.
                preview = str(self.create_post_image_preview)
                try:
                    header, b64_data = preview.split(",", 1)
                    mime = header.split(";")[0].replace("data:", "") or "image/png"
                    ext = "png"
                    if "/" in mime:
                        ext = mime.split("/", 1)[1] or "png"
                    file_bytes = base64.b64decode(b64_data)
                    if len(file_bytes) > 5 * 1024 * 1024:
                        self.loading = False
                        self.error_message = "File ảnh quá lớn (tối đa 5MB)."
                        return
                    file_payload = {"file": (f"post_upload.{ext}", file_bytes, mime)}
                    has_file = True
                except Exception:
                    # Keep silent and continue without file to preserve current UX.
                    pass
            created = await self._request_json(
                "POST",
                "/posts",
                data=payload,
                files=file_payload,
                headers={"Authorization": f"Bearer {self.token}"},
                timeout=20.0,
            )
            created_post = self._normalize_post(created if isinstance(created, dict) else {})
            if has_file and not str(created_post.get("image") or "").strip():
                self.error_message = "Đăng tin thành công nhưng ảnh chưa được lưu. Vui lòng cập nhật ảnh cho bài viết."
                return rx.redirect(f"/post/{int(created_post.get('id', 0))}" if created_post.get("id") else "/manage-post")
            self.success_message = "Đăng tin thành công."
            self.create_post_title = ""
            self.create_post_description = ""
            self.create_post_category = ""
            self.create_post_location = ""
            self.create_post_custom_location = ""
            self.create_post_contact = ""
            self.create_post_custom_category = ""
            self.create_post_image_preview = ""
            return rx.redirect("/manage-post")
        except httpx.HTTPStatusError as e:
            detail = ""
            try:
                detail = (e.response.json() or {}).get("detail", "")
            except Exception:
                detail = e.response.text
            self.error_message = str(detail or "Đăng tin thất bại. Vui lòng thử lại.")
        except Exception:
            self.error_message = "Đăng tin thất bại. Vui lòng thử lại."
        finally:
            self.loading = False

    async def set_create_post_image_preview(self, files: list[rx.UploadFile]):
        if not files:
            self.create_post_image_preview = ""
            return
        file = files[0]
        file_bytes = await file.read()
        # Reset pointer so the same file can be read again on submit.
        try:
            await file.seek(0)
        except Exception:
            pass
        if len(file_bytes) > 5 * 1024 * 1024:
            self.error_message = "File ảnh quá lớn (tối đa 5MB)."
            self.create_post_image_preview = ""
            return
        mime = file.content_type or "image/png"
        encoded = base64.b64encode(file_bytes).decode("utf-8")
        self.create_post_image_preview = f"data:{mime};base64,{encoded}"

    async def open_chat_with_user(self, receiver_id: int, receiver_name: str):
        if not self.is_logged_in:
            return rx.redirect("/login")
        if not receiver_id:
            return
        self.is_chat_open = True
        self.current_chat_receiver_id = int(receiver_id)
        self.current_chat_receiver_name = receiver_name or "Người dùng"
        self.chat_view = "chat"
        await self.load_chat_history()
        await self.mark_read(int(receiver_id))
        await self.load_conversations()

    async def open_chat_with_user_from_post(
        self,
        receiver_id: int,
        receiver_name: str,
        post_id: int,
        post_title: str,
    ):
        if not self.is_logged_in:
            return rx.redirect("/login")
        if not receiver_id:
            return
        self.is_chat_open = True
        self.current_chat_receiver_id = int(receiver_id)
        self.current_chat_receiver_name = receiver_name or "Người dùng"
        self.chat_view = "chat"
        # Ghim ngữ cảnh bài viết theo cặp hội thoại (ghi đè banner cũ).
        if int(post_id or 0) > 0:
            try:
                async with httpx.AsyncClient(timeout=15.0) as client:
                    resp = await client.post(
                        f"{self.api_base_url}/messages/send",
                        json={
                            "receiver_id": int(receiver_id),
                            "content": "",
                            "message_type": "context",
                            "post_id": int(post_id),
                            "post_title": (post_title or "").strip() or f"Bài viết #{int(post_id)}",
                        },
                        headers={"Authorization": f"Bearer {self.token}"},
                    )
                    resp.raise_for_status()
            except Exception:
                pass
        await self.load_chat_history()
        await self.mark_read(int(receiver_id))
        await self.load_conversations()

    def open_post_comments(self, post_id: int):
        if not post_id:
            return
        return rx.redirect(f"/post/{post_id}")

    async def open_feed_comments_modal(
        self,
        post_id: int,
        post_title: str = "",
        post_owner_id: int = 0,
        post_owner: str = "",
        post_created_at: str = "",
        post_description: str = "",
        post_image: str = "",
    ):
        if not post_id:
            return
        self.feed_comment_post_id = int(post_id)
        self.feed_comment_text = ""
        self.feed_reply_parent_id = 0
        self.feed_reply_target_name = ""
        self.feed_reply_text = ""
        self.feed_comment_post_title = post_title or ""
        self.feed_comment_post_owner_id = int(post_owner_id) if post_owner_id else 0
        self.feed_comment_post_owner = post_owner or "Người dùng PTIT"
        self.feed_comment_post_created_at = post_created_at or ""
        self.feed_comment_post_description = post_description or ""
        self.feed_comment_post_image = post_image or ""
        self.show_feed_comments_modal = True
        await self.load_feed_comments(int(post_id))

    def close_feed_comments_modal(self):
        self.show_feed_comments_modal = False
        self.feed_comment_post_id = 0
        self.feed_comments = []
        self.feed_comment_text = ""
        self.feed_reply_parent_id = 0
        self.feed_reply_target_name = ""
        self.feed_reply_text = ""

    async def load_feed_comments(self, post_id: int):
        if not post_id:
            self.feed_comments = []
            return
        try:
            async with httpx.AsyncClient(timeout=15.0) as client:
                resp = await client.get(f"{self.api_base_url}/comments/post/{int(post_id)}")
                resp.raise_for_status()
            comments = resp.json() or []
            normalized_comments = [self._normalize_comment(c) for c in comments]
            self.feed_comments = sorted(normalized_comments, key=lambda x: x.get("created_at", ""))
        except Exception:
            self.feed_comments = []

    async def submit_feed_comment(self, post_id: int):
        if not self.is_logged_in or not self.token:
            self.error_message = "Vui lòng đăng nhập để bình luận."
            return rx.redirect("/login")
        content = self.feed_comment_text.strip()
        if not content or not post_id:
            return
        try:
            async with httpx.AsyncClient(timeout=15.0) as client:
                resp = await client.post(
                    f"{self.api_base_url}/comments/",
                    json={"content": content, "post_id": int(post_id), "parent_comment_id": None},
                    headers={"Authorization": f"Bearer {self.token}"},
                )
                resp.raise_for_status()
            self.feed_comment_text = ""
            await self.load_feed_comments(int(post_id))
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 401:
                return self.logout()
            self.error_message = "Gửi bình luận thất bại."
        except Exception:
            self.error_message = "Gửi bình luận thất bại."

    def set_feed_reply_target(self, parent_id: int, target_name: str) -> None:
        self.feed_reply_parent_id = int(parent_id) if parent_id else 0
        self.feed_reply_target_name = target_name or "người dùng"

    def cancel_feed_reply(self) -> None:
        self.feed_reply_parent_id = 0
        self.feed_reply_target_name = ""
        self.feed_reply_text = ""

    async def submit_feed_reply_current(self):
        if not self.is_logged_in or not self.token:
            self.error_message = "Vui lòng đăng nhập để trả lời."
            return rx.redirect("/login")
        content = self.feed_reply_text.strip()
        post_id = self.feed_comment_post_id
        if not content or not post_id or not self.feed_reply_parent_id:
            return
        try:
            async with httpx.AsyncClient(timeout=15.0) as client:
                resp = await client.post(
                    f"{self.api_base_url}/comments/",
                    json={
                        "content": content,
                        "post_id": int(post_id),
                        "parent_comment_id": int(self.feed_reply_parent_id),
                    },
                    headers={"Authorization": f"Bearer {self.token}"},
                )
                resp.raise_for_status()
            self.feed_reply_text = ""
            self.feed_reply_parent_id = 0
            self.feed_reply_target_name = ""
            await self.load_feed_comments(int(post_id))
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 401:
                return self.logout()
            self.error_message = "Gửi trả lời thất bại."
        except Exception:
            self.error_message = "Gửi trả lời thất bại."

    def toggle_feed_report_box(self, post_id: int):
        if not post_id:
            return
        if self.feed_report_post_id == int(post_id):
            self.feed_report_post_id = 0
            self.feed_report_reason = ""
            self.feed_action_message = ""
            return
        self.feed_report_post_id = int(post_id)
        self.feed_report_reason = ""
        self.feed_action_message = ""

    async def _submit_feed_report(self, post_id: int, reason_prefix: str = ""):
        if not self.is_logged_in or not self.token:
            self.feed_action_message = "Vui lòng đăng nhập để thực hiện."
            return rx.redirect("/login")
        reason = self.feed_report_reason.strip()
        if not reason:
            self.feed_action_message = "Vui lòng nhập lý do."
            return
        if not post_id:
            return
        final_reason = f"{reason_prefix}{reason}"
        try:
            async with httpx.AsyncClient(timeout=15.0) as client:
                resp = await client.post(
                    f"{self.api_base_url}/reports",
                    json={"post_id": int(post_id), "reason": final_reason},
                    headers={"Authorization": f"Bearer {self.token}"},
                )
                resp.raise_for_status()
            self.feed_action_message = "Đã gửi thành công."
            self.feed_report_reason = ""
        except Exception:
            self.feed_action_message = "Gửi thất bại. Vui lòng thử lại."

    async def submit_feed_report(self, post_id: int):
        await self._submit_feed_report(post_id, "")

    async def submit_feed_remove_request(self, post_id: int):
        await self._submit_feed_report(post_id, "[Yêu cầu gỡ bài] ")

    async def admin_remove_post(self, post_id: int):
        if not self.is_logged_in or not self.token:
            self.feed_action_message = "Vui lòng đăng nhập."
            return rx.redirect("/login")
        if not self.is_admin:
            self.feed_action_message = "Bạn không có quyền admin."
            return
        try:
            pid = int(post_id) if post_id else 0
        except Exception:
            pid = 0
        if pid <= 0:
            self.feed_action_message = "Không tìm thấy bài viết để gỡ."
            return
        try:
            await self._request_json(
                "PUT",
                f"/posts/{pid}/moderate",
                json={"action": "remove"},
                headers={"Authorization": f"Bearer {self.token}"},
            )
            self.feed_action_message = "Admin đã chuyển bài vào mục đã gỡ."
            await self.load_posts()
            self.admin_tab = "removed"
            await self.load_admin_removed_posts()
            self.current_post = {}
            return rx.redirect("/admin")
        except Exception:
            self.feed_action_message = "Không gỡ được bài viết."

    async def resolve_current_post(self):
        if not self.is_logged_in or not self.token:
            return rx.redirect("/login")
        post_id = self.router.page.params.get("id")
        if not post_id:
            return
        try:
            async with httpx.AsyncClient(timeout=15.0) as client:
                resp = await client.put(
                    f"{self.api_base_url}/posts/{post_id}/resolve",
                    headers={"Authorization": f"Bearer {self.token}"},
                )
                resp.raise_for_status()
            self.current_post = self._normalize_post(resp.json() or self.current_post)
            self.post_action_message = "Đã đánh dấu bài viết là đã giải quyết."
        except Exception:
            self.post_action_message = "Không thể cập nhật trạng thái bài viết."

    def close_post_report_box(self):
        self.show_post_report_box = False
        self.report_reason = ""

    def open_post_report_box(self):
        self.show_post_report_box = True
        self.post_report_mode = "report"

    def open_post_remove_request_box(self):
        self.show_post_report_box = True
        self.post_report_mode = "remove_request"

    async def report_current_post(self):
        if not self.is_logged_in or not self.token:
            return rx.redirect("/login")
        post_id = self.router.page.params.get("id")
        reason = self.report_reason.strip()
        if not post_id or not reason:
            self.post_action_message = "Vui lòng nhập lý do báo cáo."
            return
        try:
            async with httpx.AsyncClient(timeout=15.0) as client:
                resp = await client.post(
                    f"{self.api_base_url}/reports",
                    json={"post_id": int(post_id), "reason": reason},
                    headers={"Authorization": f"Bearer {self.token}"},
                )
                resp.raise_for_status()
            self.post_action_message = "Đã gửi báo cáo thành công."
            self.report_reason = ""
            self.show_post_report_box = False
        except Exception:
            self.post_action_message = "Gửi báo cáo thất bại."

    async def request_remove_current_post(self):
        if not self.is_logged_in or not self.token:
            return rx.redirect("/login")
        post_id = self.router.page.params.get("id")
        reason = self.report_reason.strip()
        if not post_id or not reason:
            self.post_action_message = "Vui lòng nhập lý do yêu cầu gỡ bài."
            return
        try:
            async with httpx.AsyncClient(timeout=15.0) as client:
                resp = await client.post(
                    f"{self.api_base_url}/reports",
                    json={"post_id": int(post_id), "reason": f"[Yêu cầu gỡ bài] {reason}"},
                    headers={"Authorization": f"Bearer {self.token}"},
                )
                resp.raise_for_status()
            self.post_action_message = "Đã gửi yêu cầu gỡ bài thành công."
            self.report_reason = ""
            self.show_post_report_box = False
        except Exception:
            self.post_action_message = "Gửi yêu cầu gỡ bài thất bại."


    # ADMIN METHODS
    def set_admin_tab(self, tab: str):
        self.admin_tab = tab
        if tab == "posts":
            return AppState.load_admin_pending_posts
        if tab == "reports":
            return AppState.load_admin_reports
        if tab == "locked_users":
            return AppState.load_admin_locked_users
        return AppState.load_admin_removed_posts

    async def load_admin_pending_posts(self):
        if not self.is_admin: return
        self.admin_loading = True
        self.admin_action_message = ""
        try:
            data = await self._request_json("GET", "/posts/moderation/PENDING", headers={"Authorization": f"Bearer {self.token}"})
            self.admin_pending_posts = [self._normalize_post(p) for p in data if isinstance(p, dict)]
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 401: return self.logout()
            self.admin_pending_posts = []
        except Exception:
            self.admin_pending_posts = []
        finally:
            self.admin_loading = False

    async def load_admin_reports(self):
        if not self.is_admin: return
        self.admin_loading = True
        self.admin_action_message = ""
        try:
            existing_owner_status: dict[int, bool] = {}
            for item in self.admin_reports:
                try:
                    uid = int((item or {}).get("post_user_id") or 0)
                    active_val = (item or {}).get("post_owner_active")
                    if uid > 0 and active_val is not None:
                        existing_owner_status[uid] = bool(active_val)
                except Exception:
                    continue
            data = await self._request_json("GET", "/reports", headers={"Authorization": f"Bearer {self.token}"})
            normalized_reports = [self._normalize_admin_report(r) for r in data if isinstance(r, dict)]
            for item in normalized_reports:
                try:
                    uid = int(item.get("post_user_id", 0) or 0)
                    if uid > 0 and item.get("post_owner_active") is None and uid in existing_owner_status:
                        item["post_owner_active"] = existing_owner_status[uid]
                except Exception:
                    continue
            self.admin_reports = normalized_reports
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 401: return self.logout()
            self.admin_reports = []
        except Exception:
            self.admin_reports = []
        finally:
            self.admin_loading = False

    async def load_admin_removed_posts(self):
        if not self.is_admin:
            return
        self.admin_loading = True
        self.admin_action_message = ""
        try:
            data = await self._request_json("GET", "/posts/moderation/REMOVED", headers={"Authorization": f"Bearer {self.token}"})
            self.admin_removed_posts = [self._normalize_post(p) for p in data if isinstance(p, dict)]
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 401:
                return self.logout()
            self.admin_removed_posts = []
        except Exception:
            self.admin_removed_posts = []
        finally:
            self.admin_loading = False

    async def load_admin_locked_users(self):
        if not self.is_admin:
            return
        self.admin_loading = True
        self.admin_action_message = ""
        try:
            data = await self._request_json(
                "GET",
                "/users/locked",
                headers={"Authorization": f"Bearer {self.token}"},
            )
            self.admin_locked_users = [u for u in data if isinstance(u, dict)]
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 401:
                return self.logout()
            self.admin_locked_users = []
        except Exception:
            self.admin_locked_users = []
        finally:
            self.admin_loading = False

    async def admin_moderate_post(self, post_id: int, action: str):
        if not self.is_admin: return
        try:
            await self._request_json(
                "PUT", 
                f"/posts/{post_id}/moderate", 
                json={"action": action}, 
                headers={"Authorization": f"Bearer {self.token}"}
            )
            self.admin_action_message = f"Đã {action.upper()} bài viết #{post_id}"
            await self.load_admin_pending_posts()
            await self.load_posts()
        except Exception:
            self.admin_action_message = f"Lỗi khi {action} bài viết"

    async def admin_delete_post_report(self, post_id: int, report_id: int = 0):
        if not self.is_admin:
            return
        try:
            pid = int(post_id) if post_id else 0
        except Exception:
            pid = 0
        try:
            rid = int(report_id) if report_id else 0
        except Exception:
            rid = 0
        if pid <= 0:
            self.admin_action_message = "Không tìm thấy ID bài viết để gỡ."
            return
        try:
            await self._request_json(
                "PUT",
                f"/posts/{pid}/moderate",
                json={"action": "remove"},
                headers={"Authorization": f"Bearer {self.token}"},
            )
            self.admin_action_message = f"Đã chuyển bài viết #{pid} vào mục đã xóa."
            await self.load_posts()
            self.admin_tab = "removed"
            await self.load_admin_removed_posts()
            return rx.redirect("/admin")
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 404:
                if rid > 0:
                    self.admin_reports = [r for r in self.admin_reports if int(r.get("id", 0) or 0) != rid]
                else:
                    self.admin_reports = [r for r in self.admin_reports if int(r.get("post_id", 0) or 0) != pid]
                self.admin_action_message = f"Bài viết #{pid} đã không tồn tại (đã gỡ trước đó)."
                await self.load_posts()
                self.admin_tab = "removed"
                await self.load_admin_removed_posts()
                return rx.redirect("/admin")
            detail = ""
            try:
                detail = str((e.response.json() or {}).get("detail", ""))
            except Exception:
                detail = e.response.text
            self.admin_action_message = detail or "Không thể gỡ bài viết"
        except Exception:
            self.admin_action_message = "Không thể gỡ bài viết"

    async def admin_mark_report_safe(self, report_id: int):
        if not self.is_admin:
            return
        try:
            rid = int(report_id) if report_id else 0
        except Exception:
            rid = 0
        if rid <= 0:
            self.admin_action_message = "Không tìm thấy báo cáo để cập nhật."
            return
        try:
            await self._request_json(
                "PUT",
                f"/reports/{rid}/review",
                headers={"Authorization": f"Bearer {self.token}"},
            )
            self.admin_reports = [r for r in self.admin_reports if int(r.get("id", 0) or 0) != rid]
            self.admin_action_message = "Đã đánh dấu an toàn và ẩn báo cáo."
        except Exception:
            self.admin_action_message = "Không thể cập nhật báo cáo."

    async def admin_set_user_active(self, user_id: int, is_active: bool):
        if not self.is_admin:
            return
        try:
            uid = int(user_id) if user_id else 0
        except Exception:
            uid = 0
        if uid <= 0:
            self.admin_action_message = "Không tìm thấy người dùng để cập nhật."
            return
        try:
            await self._request_json(
                "PUT",
                f"/users/{uid}/status",
                json={"is_active": bool(is_active)},
                headers={"Authorization": f"Bearer {self.token}"},
            )
            updated_reports: list[dict] = []
            for report in self.admin_reports:
                item = dict(report) if isinstance(report, dict) else {}
                try:
                    if int(item.get("post_user_id", 0) or 0) == uid:
                        item["post_owner_active"] = bool(is_active)
                except Exception:
                    pass
                updated_reports.append(item)
            self.admin_reports = updated_reports
            self.admin_action_message = (
                "Đã mở khóa tài khoản người dùng."
                if bool(is_active)
                else "Đã khóa tài khoản người dùng do vi phạm lặp lại."
            )
            await self.load_admin_locked_users()
        except Exception:
            self.admin_action_message = "Không thể cập nhật trạng thái tài khoản."

    async def run_health_check(self):
        self.health_status = "checking"
        self.health_message = "Đang kiểm tra kết nối backend..."
        try:
            async with httpx.AsyncClient(timeout=8.0) as client:
                resp = await client.get(f"{self.api_base_url}/posts")
                resp.raise_for_status()
            self.health_status = "ok"
            self.health_message = "Backend kết nối OK."
        except Exception:
            self.health_status = "error"
            self.health_message = "Không kết nối được backend. Kiểm tra server/CORS/env."

