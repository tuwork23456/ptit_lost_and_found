import reflex as rx

from ptit_lost_and_found.components.chatbox import chatbox
from ptit_lost_and_found.components.footer import footer
from ptit_lost_and_found.components.navbar import navbar
from ptit_lost_and_found.components.reddit_layout import left_sidebar, right_panel
from ptit_lost_and_found.pages.auth import login_page, register_page
from ptit_lost_and_found.pages.home import home_page_with_load
from ptit_lost_and_found.pages.manage_post import manage_post_page
from ptit_lost_and_found.pages.notifications import notifications_page
from ptit_lost_and_found.pages.post_create import post_create_page
from ptit_lost_and_found.pages.post_detail import post_detail_page
from ptit_lost_and_found.pages.profile import profile_page
from ptit_lost_and_found.pages.admin import admin_page
from ptit_lost_and_found.pages.search import search_page as search_content_page
from ptit_lost_and_found.pages.saved_posts import saved_posts_page
from ptit_lost_and_found.state import AppState
from ptit_lost_and_found.pages.system_status import system_status_page


def base_layout(content: rx.Component) -> rx.Component:
    return rx.el.div(
        # Ensure Tailwind utility classes are available at runtime.
        rx.el.script(src="https://cdn.tailwindcss.com"),
        rx.el.span(
            AppState.user_id,
            id="rt-user-id",
            class_name="hidden",
        ),
        rx.button(
            "",
            id="rt-refresh-chat-btn",
            on_click=AppState.refresh_chat_data,
            class_name="hidden",
        ),
        rx.button(
            "",
            id="rt-refresh-notif-btn",
            on_click=AppState.load_notifications,
            class_name="hidden",
        ),
        rx.script(
            """
(() => {
  if (window.__camNhamRtInitialized) return;
  window.__camNhamRtInitialized = true;
  let ws = null;
  let lastUid = "";

  const getUid = () => {
    const el = document.getElementById("rt-user-id");
    return (el?.textContent || "").trim();
  };

  const clickIfExists = (id) => {
    const btn = document.getElementById(id);
    if (btn) btn.click();
  };

  const setupWs = (uid) => {
    if (!uid) return;
    try {
      ws = new WebSocket(`ws://localhost:8000/ws/${uid}`);
      ws.onmessage = () => {
        clickIfExists("rt-refresh-chat-btn");
        clickIfExists("rt-refresh-notif-btn");
      };
      ws.onclose = () => {
        setTimeout(() => {
          if (getUid() === uid) setupWs(uid);
        }, 1500);
      };
    } catch (_) {}
  };

  setInterval(() => {
    const uid = getUid();
    if (uid !== lastUid) {
      if (ws) {
        try { ws.close(); } catch (_) {}
        ws = null;
      }
      lastUid = uid;
      if (uid) setupWs(uid);
    }
  }, 1000);
})();
            """
        ),
        navbar(),
        rx.el.main(
            rx.el.div(
                left_sidebar(),
                rx.el.section(content, class_name="w-full min-w-0 overflow-visible lg:flex-1"),
                right_panel(),
                class_name="w-full px-3 md:px-5 lg:px-6 py-6 lg:flex lg:items-start lg:justify-between lg:gap-4 xl:gap-5",
            ),
            class_name="flex-grow w-full relative",
        ),
        chatbox(),
        footer(),
        class_name="min-h-screen flex flex-col bg-[#f8fafc]",
    )


def home() -> rx.Component:
    return base_layout(home_page_with_load())


def placeholder_page(title: str) -> rx.Component:
    return base_layout(
        rx.center(
            rx.vstack(
                rx.heading(title, size="8"),
                rx.text("Đang trong quá trình migrate từ React sang Reflex."),
                spacing="3",
                align="center",
            ),
            min_height="60vh",
        )
    )


def post_page() -> rx.Component:
    return base_layout(post_create_page())


def search_route() -> rx.Component:
    return base_layout(search_content_page())


def post_detail() -> rx.Component:
    return base_layout(post_detail_page())


def manage_post_route() -> rx.Component:
    return base_layout(manage_post_page())


def profile_route() -> rx.Component:
    return base_layout(profile_page())


def notifications_route() -> rx.Component:
    return base_layout(notifications_page())


def saved_posts_route() -> rx.Component:
    return base_layout(saved_posts_page())


def system_status_route() -> rx.Component:
    return base_layout(system_status_page())


def admin_route() -> rx.Component:
    return base_layout(admin_page())


app = rx.App()
app.add_page(home, route="/", title="PTIT Lost & Found")
app.add_page(post_page, route="/post", title="Đăng tin")
app.add_page(search_route, route="/search", title="Tìm kiếm")
app.add_page(post_detail, route="/post/[id]", title="Chi tiết tin")
app.add_page(manage_post_route, route="/manage-post", title="Quản lý bài đăng")
app.add_page(profile_route, route="/profile", title="Hồ sơ")
app.add_page(profile_route, route="/user/[id]", title="Trang cá nhân")
app.add_page(notifications_route, route="/notifications", title="Thông báo")
app.add_page(saved_posts_route, route="/saved-posts", title="Bài đã lưu")
app.add_page(system_status_route, route="/system-status", title="Trạng thái hệ thống")
app.add_page(admin_route, route="/admin", title="Quản trị")
app.add_page(login_page, route="/login", title="Đăng nhập")
app.add_page(register_page, route="/register", title="Đăng ký")

