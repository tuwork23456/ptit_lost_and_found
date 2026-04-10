import re
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
    selected_type: str = "Tat ca loai tin"
    selected_category: str = "Tat ca danh muc"
    selected_location: str = "Tat ca khu vuc"
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
    current_chat_pinned_post: dict = {}
    chat_input: str = ""
    unread_message_count: int = 0
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
    admin_loading: bool = False
    admin_tab: str = "posts"  # "posts" | "reports" | "removed"
    admin_action_message: str = ""

    api_base_url: str = "http://localhost:8000"

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
    def _normalize_comment(comment: dict) -> dict:
        user = comment.get("user") if isinstance(comment, dict) else None
        username = "An danh"
        if isinstance(user, dict):
            username = str(user.get("username") or "An danh")
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
                username = str(node.get("username") or "An danh")
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
        username = str(owner.get("username") or normalized.get("username") or "Nguoi dung PTIT")
        normalized["username"] = username
        raw_image = str(
            normalized.get("image")
            or normalized.get("image_url")
            or normalized.get("imagePath")
            or ""
        ).strip()
        original_raw_image = raw_image
        raw_image = raw_image.replace("\\", "/")
        if "/uploads/" in raw_image and not raw_image.startswith("/uploads/"):
            raw_image = "/uploads/" + raw_image.split("/uploads/")[-1]
        if raw_image.startswith("uploads/"):
            raw_image = "/" + raw_image
        if raw_image.startswith("/"):
            raw_image = f"{self.api_base_url.rstrip('/')}{raw_image}"
        # Avoid broken image icon when backend returns invalid/non-url strings.
        if raw_image and (
            raw_image.startswith("http://")
            or raw_image.startswith("https://")
            or raw_image.startswith("data:image/")
        ):
            normalized["image"] = raw_image
        else:
            normalized["image"] = ""
            if original_raw_image and len(self.image_debug_samples) < 10 and original_raw_image not in self.image_debug_samples:
                self.image_debug_samples.append(original_raw_image)
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
            normalized["post_image"] = str(post_obj.get("image") or normalized.get("post_image") or "").strip()
            normalized["post_location"] = str(post_obj.get("location") or normalized.get("post_location") or "").strip()
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
        uname = "Nguoi dung"
        if isinstance(rep, dict):
            u = rep.get("username")
            if u is not None and str(u).strip():
                uname = str(u).strip()
        normalized["reporter_username"] = uname
        return normalized

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
            self.error_message = "Khong tai duoc danh sach bai viet."
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
            if self.selected_type == "Mat do":
                selected_type = "LOST"
            elif self.selected_type == "Nhat duoc":
                selected_type = "FOUND"

            search_category = "" if self.selected_category == "Tat ca danh muc" else self.selected_category
            search_location = "" if self.selected_location == "Tat ca khu vuc" else self.selected_location
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

            self.search_results = [self._normalize_post(p) for p in all_items]
            self.search_total = int(total)
        except Exception:
            if req_id != self.search_request_seq:
                return
            self.error_message = "Khong tai duoc ket qua tim kiem."
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
            if self.create_post_category == "Khac"
            else self.create_post_category.strip()
        )
        location = (
            self.create_post_custom_location.strip()
            if self.create_post_location == "Khac"
            else ("" if self.create_post_location == "Khong co" else self.create_post_location.strip())
        )
        if not category:
            category = "do vat"
        prefix = "Tim" if self.create_post_type == "LOST" else "Nhat duoc"
        return f"{prefix} {category}" + (f" tai {location}" if location else "")

    @rx.var
    def available_categories(self) -> list[str]:
        values = sorted({str(p.get("category", "")).strip() for p in self.posts if p.get("category")})
        return ["Tat ca danh muc", *values]

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
        return ["Tat ca khu vuc", *values]

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
        if self.feed_filter == "FOUND":
            posts = [p for p in self.posts if p.get("type") == "FOUND"]
        else:
            posts = [p for p in self.posts if p.get("type") == "LOST"]
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
                self.error_message = "Vui long nhap day du email va mat khau."
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
                                "Dang nhap that bai qua nhieu lan. Vui long doi khoang 15 phut roi thu lai."
                            )
                        elif code == 422:
                            self.error_message = (
                                "Email hoac dinh dang khong hop le. Vui long kiem tra lai."
                            )
                        elif code == 401:
                            self.error_message = "Sai email hoac mat khau. Vui long kiem tra lai."
                        else:
                            self.error_message = str(
                                detail or "Dang nhap that bai. Vui long kiem tra lai thong tin."
                            )
                        self.loading = False
                        return
                    except httpx.RequestError as e:
                        last_error = e

            if data is None:
                self.error_message = (
                    "Khong ket noi duoc backend dang nhap (da thu port 8000/8001). "
                    "Hay kiem tra backend da chay chua."
                )
                if last_error:
                    self.error_message = (
                        "Khong ket noi duoc backend dang nhap. Vui long bat backend truoc."
                    )
                self.loading = False
                return
            self.token = data.get("access_token", "")
            user = data.get("user") or {}
            self.username = user.get("username", "")
            self.user_id = str(user.get("id", "") or "")
            self.user_email = user.get("email", email)
            self.user_role = str(user.get("role", "USER") or "USER").upper()
            self.success_message = "Dang nhap thanh cong."
            if not self.token:
                self.error_message = "Dang nhap that bai: server khong tra ve token."
                return
            return rx.redirect("/")
        except Exception:
            self.error_message = "Dang nhap that bai. Vui long thu lai."
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
            self.error_message = "Mat khau xac nhan khong khop."
            self.loading = False
            return
        if len(reg_password) < 8:
            self.error_message = "Mat khau phai co it nhat 8 ky tu, gom chu hoa, chu thuong va so."
            self.loading = False
            return
        # Đồng bộ validation với backend: phải có chữ hoa, chữ thường và số
        if (
            not re.search(r"[A-Z]", reg_password)
            or not re.search(r"[a-z]", reg_password)
            or not re.search(r"\d", reg_password)
        ):
            self.error_message = "Mat khau phai co it nhat 1 chu hoa, 1 chu thuong va 1 so."
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
                        self.error_message = str(detail or "Dang ky that bai.")
                        self.loading = False
                        return
                    except httpx.RequestError:
                        continue

            if not ok:
                self.error_message = "Khong ket noi duoc backend dang ky. Vui long bat backend truoc."
                self.loading = False
                return
            self.success_message = "Dang ky thanh cong. Moi ban dang nhap."
            return rx.redirect("/login")
        except Exception:
            self.error_message = "Dang ky that bai. Email co the da ton tai."
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
        self.saved_posts = []
        self.saved_post_ids_data = []
        post_id = self.router.page.params.get("id")
        if not post_id:
            self.error_message = "Khong tim thay bai viet."
            self.post_loading = False
            return
        try:
            post_data = await self._request_json("GET", f"/posts/{post_id}", timeout=20.0)
            comments = await self._request_json("GET", f"/comments/post/{post_id}", timeout=20.0)
            self.current_post = self._normalize_post(post_data if isinstance(post_data, dict) else {})
            normalized_comments = [self._normalize_comment(c) for c in comments]
            self.post_comments = sorted(normalized_comments, key=lambda x: x.get("created_at", ""))
        except Exception:
            self.error_message = "Khong tai duoc chi tiet bai viet."
            self.current_post = {}
            self.post_comments = []
        finally:
            self.post_loading = False

    async def submit_comment(self):
        if not self.is_logged_in or not self.token:
            self.error_message = "Vui long dang nhap de binh luan."
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
            self.error_message = "Gui binh luan that bai."
        except Exception:
            self.error_message = "Gui binh luan that bai."

    def set_post_reply_target(self, parent_id: int, target_name: str) -> None:
        self.post_reply_parent_id = int(parent_id) if parent_id else 0
        self.post_reply_target_name = target_name or "nguoi dung"

    def cancel_post_reply(self) -> None:
        self.post_reply_parent_id = 0
        self.post_reply_target_name = ""
        self.post_reply_text = ""

    async def submit_post_reply_current(self):
        if not self.is_logged_in or not self.token:
            self.error_message = "Vui long dang nhap de tra loi."
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
            self.error_message = "Gui tra loi that bai."
        except Exception:
            self.error_message = "Gui tra loi that bai."

    async def load_my_posts(self) -> None:
        if not self.is_logged_in or not self.token:
            self.error_message = "Vui long dang nhap."
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
            self.error_message = "Khong tai duoc bai dang cua ban."
            self.my_posts = []
        except Exception:
            self.error_message = "Khong tai duoc bai dang cua ban."
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
                    posts.append(post)
                    ids.append(int(post.get("id")))
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
            self.error_message = "Xoa bai that bai."

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
            self.error_message = "Khong tim thay nguoi dung."
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
            self.error_message = "Khong tai duoc thong tin nguoi dung."
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
        await self.mark_read(receiver_id)

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
            self.unread_message_count = int((resp.json() or {}).get("unread_count", 0))
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
            self.chat_input = ""
            await self.load_conversations()
        except Exception:
            self.error_message = "Gui tin nhan that bai."

    async def refresh_chat_data(self):
        if self.chat_view == "chat" and self.current_chat_receiver_id:
            await self.load_chat_history()
            await self.mark_read(self.current_chat_receiver_id)
        else:
            await self.load_conversations()
        await self.load_unread_count()
        await self.load_notifications()

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

    async def mark_notification_read_and_open(self, notification_id: int, target_id: int):
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
            self.error_message = "Vui long dang nhap de dang tin."
            return rx.redirect("/login")

        final_category = (
            self.create_post_custom_category.strip()
            if self.create_post_category == "Khac"
            else self.create_post_category.strip()
        )
        final_location = (
            self.create_post_custom_location.strip()
            if self.create_post_location == "Khac"
            else ("" if self.create_post_location == "Khong co" else self.create_post_location.strip())
        )
        if not final_category:
            self.error_message = "Vui long chon loai do."
            return
        if not self.create_post_title.strip():
            self.error_message = "Vui long nhap tieu de."
            return
        if not self.create_post_description.strip():
            self.error_message = "Vui long nhap noi dung."
            return
        if not self.create_post_contact.strip():
            self.error_message = "Vui long nhap thong tin lien he."
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
                    self.error_message = "File anh qua lon (toi da 5MB)."
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
                        self.error_message = "File anh qua lon (toi da 5MB)."
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
                self.error_message = "Dang tin thanh cong nhung anh chua duoc luu. Vui long cap nhat anh cho bai viet."
                return rx.redirect(f"/post/{int(created_post.get('id', 0))}" if created_post.get("id") else "/manage-post")
            self.success_message = "Dang tin thanh cong."
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
            self.error_message = str(detail or "Dang tin that bai. Vui long thu lai.")
        except Exception:
            self.error_message = "Dang tin that bai. Vui long thu lai."
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
            self.error_message = "File anh qua lon (toi da 5MB)."
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
        self.current_chat_receiver_name = receiver_name or "User"
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
        self.current_chat_receiver_name = receiver_name or "User"
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
                            "post_title": (post_title or "").strip() or f"Bai viet #{int(post_id)}",
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
        self.feed_comment_post_owner = post_owner or "Nguoi dung PTIT"
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
            self.error_message = "Vui long dang nhap de binh luan."
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
            self.error_message = "Gui binh luan that bai."
        except Exception:
            self.error_message = "Gui binh luan that bai."

    def set_feed_reply_target(self, parent_id: int, target_name: str) -> None:
        self.feed_reply_parent_id = int(parent_id) if parent_id else 0
        self.feed_reply_target_name = target_name or "nguoi dung"

    def cancel_feed_reply(self) -> None:
        self.feed_reply_parent_id = 0
        self.feed_reply_target_name = ""
        self.feed_reply_text = ""

    async def submit_feed_reply_current(self):
        if not self.is_logged_in or not self.token:
            self.error_message = "Vui long dang nhap de tra loi."
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
            self.error_message = "Gui tra loi that bai."
        except Exception:
            self.error_message = "Gui tra loi that bai."

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
            self.feed_action_message = "Vui long dang nhap de thuc hien."
            return rx.redirect("/login")
        reason = self.feed_report_reason.strip()
        if not reason:
            self.feed_action_message = "Vui long nhap ly do."
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
            self.feed_action_message = "Da gui thanh cong."
            self.feed_report_reason = ""
        except Exception:
            self.feed_action_message = "Gui that bai. Vui long thu lai."

    async def submit_feed_report(self, post_id: int):
        await self._submit_feed_report(post_id, "")

    async def submit_feed_remove_request(self, post_id: int):
        await self._submit_feed_report(post_id, "[Yeu cau go bai] ")

    async def admin_remove_post(self, post_id: int):
        if not self.is_logged_in or not self.token:
            self.feed_action_message = "Vui long dang nhap."
            return rx.redirect("/login")
        if not self.is_admin:
            self.feed_action_message = "Ban khong co quyen admin."
            return
        try:
            pid = int(post_id) if post_id else 0
        except Exception:
            pid = 0
        if pid <= 0:
            self.feed_action_message = "Khong tim thay bai viet de go."
            return
        try:
            await self._request_json(
                "PUT",
                f"/posts/{pid}/moderate",
                json={"action": "remove"},
                headers={"Authorization": f"Bearer {self.token}"},
            )
            self.feed_action_message = "Admin da chuyen bai vao muc da go."
            await self.load_posts()
            self.admin_tab = "removed"
            await self.load_admin_removed_posts()
            self.current_post = {}
            return rx.redirect("/admin")
        except Exception:
            self.feed_action_message = "Khong go duoc bai viet."

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
            self.post_action_message = "Da danh dau bai viet la da giai quyet."
        except Exception:
            self.post_action_message = "Khong the cap nhat trang thai bai viet."

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
            self.post_action_message = "Vui long nhap ly do bao cao."
            return
        try:
            async with httpx.AsyncClient(timeout=15.0) as client:
                resp = await client.post(
                    f"{self.api_base_url}/reports",
                    json={"post_id": int(post_id), "reason": reason},
                    headers={"Authorization": f"Bearer {self.token}"},
                )
                resp.raise_for_status()
            self.post_action_message = "Da gui bao cao thanh cong."
            self.report_reason = ""
            self.show_post_report_box = False
        except Exception:
            self.post_action_message = "Gui bao cao that bai."

    async def request_remove_current_post(self):
        if not self.is_logged_in or not self.token:
            return rx.redirect("/login")
        post_id = self.router.page.params.get("id")
        reason = self.report_reason.strip()
        if not post_id or not reason:
            self.post_action_message = "Vui long nhap ly do yeu cau go bai."
            return
        try:
            async with httpx.AsyncClient(timeout=15.0) as client:
                resp = await client.post(
                    f"{self.api_base_url}/reports",
                    json={"post_id": int(post_id), "reason": f"[Yeu cau go bai] {reason}"},
                    headers={"Authorization": f"Bearer {self.token}"},
                )
                resp.raise_for_status()
            self.post_action_message = "Da gui yeu cau go bai thanh cong."
            self.report_reason = ""
            self.show_post_report_box = False
        except Exception:
            self.post_action_message = "Gui yeu cau go bai that bai."


    # ADMIN METHODS
    def set_admin_tab(self, tab: str):
        self.admin_tab = tab
        if tab == "posts":
            return AppState.load_admin_pending_posts
        if tab == "reports":
            return AppState.load_admin_reports
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
            data = await self._request_json("GET", "/reports", headers={"Authorization": f"Bearer {self.token}"})
            self.admin_reports = [self._normalize_admin_report(r) for r in data if isinstance(r, dict)]
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

    async def admin_moderate_post(self, post_id: int, action: str):
        if not self.is_admin: return
        try:
            await self._request_json(
                "PUT", 
                f"/posts/{post_id}/moderate", 
                json={"action": action}, 
                headers={"Authorization": f"Bearer {self.token}"}
            )
            self.admin_action_message = f"Da {action.upper()} bai viet #{post_id}"
            await self.load_admin_pending_posts()
            await self.load_posts()
        except Exception:
            self.admin_action_message = f"Loi khi {action} bai viet"

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
            self.admin_action_message = "Khong tim thay ID bai viet de go."
            return
        try:
            await self._request_json("DELETE", f"/posts/{pid}", headers={"Authorization": f"Bearer {self.token}"})
            self.admin_action_message = f"Da GO bai viet #{pid} thanh cong."
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
                self.admin_action_message = f"Bai viet #{pid} da khong ton tai (da go truoc do)."
                await self.load_posts()
                self.admin_tab = "removed"
                await self.load_admin_removed_posts()
                return rx.redirect("/admin")
            detail = ""
            try:
                detail = str((e.response.json() or {}).get("detail", ""))
            except Exception:
                detail = e.response.text
            self.admin_action_message = detail or "Khong the go bai viet"
        except Exception:
            self.admin_action_message = "Khong the go bai viet"

    async def run_health_check(self):
        self.health_status = "checking"
        self.health_message = "Dang kiem tra ket noi backend..."
        try:
            async with httpx.AsyncClient(timeout=8.0) as client:
                resp = await client.get(f"{self.api_base_url}/posts")
                resp.raise_for_status()
            self.health_status = "ok"
            self.health_message = "Backend ket noi OK."
        except Exception:
            self.health_status = "error"
            self.health_message = "Khong ket noi duoc backend. Kiem tra server/cors/env."

