import reflex as rx

from ptit_lost_and_found.state import AppState


def _notif_item(notif: dict) -> rx.Component:
    notif_id = notif.get("id")
    target_id = notif.get("target_id")
    is_read = notif.get("is_read")
    created = rx.cond(notif.get("created_at") != None, notif.get("created_at"), "")
    return rx.el.button(
        rx.vstack(
            rx.text(
                rx.cond(notif.get("message") != None, notif.get("message"), ""),
                class_name=rx.cond(
                    is_read,
                    "text-sm text-gray-600 text-left",
                    "text-sm text-gray-900 font-semibold text-left",
                ),
            ),
            rx.text(created, class_name="text-[11px] text-gray-400 text-left"),
            align="start",
            spacing="1",
            width="100%",
        ),
        on_click=AppState.mark_notification_read_and_open(notif_id, target_id),
        class_name=rx.cond(
            is_read,
            "w-full text-left px-4 py-3 border border-gray-100 rounded-xl bg-white hover:bg-gray-50 transition",
            "w-full text-left px-4 py-3 border border-red-100 rounded-xl bg-red-50/40 hover:bg-red-50 transition",
        ),
    )


def notifications_page() -> rx.Component:
    return rx.cond(
        AppState.is_logged_in,
        rx.el.div(
            rx.el.div(
                rx.hstack(
                    rx.vstack(
                        rx.heading("Thông báo", size="6", class_name="text-slate-800"),
                        rx.text(
                            f"{AppState.unread_notification_count} chưa đọc / {AppState.notifications.length()} tổng",
                            class_name="text-sm text-slate-500",
                        ),
                        align="start",
                        spacing="1",
                    ),
                    rx.spacer(),
                    rx.button(
                        "Làm mới",
                        on_click=AppState.load_notifications,
                        class_name="bg-white border border-slate-200 hover:bg-slate-50 text-slate-700 text-sm",
                    ),
                    rx.button(
                        "Đánh dấu đã đọc tất cả",
                        on_click=AppState.mark_all_notifications_read,
                        class_name="bg-red-50 hover:bg-red-100 text-red-600 text-sm border border-red-100",
                    ),
                    width="100%",
                    align="center",
                ),
                rx.cond(
                    AppState.notifications.length() == 0,
                    rx.center(
                        rx.text("Chưa có thông báo nào.", class_name="text-gray-400"),
                        class_name="py-16",
                    ),
                    rx.vstack(
                        rx.foreach(AppState.notifications, _notif_item),
                        spacing="3",
                        width="100%",
                        class_name="mt-5",
                    ),
                ),
                class_name="bg-white rounded-3xl shadow-sm border border-slate-100 p-6 md:p-8 max-w-7xl mx-auto",
            ),
            class_name="w-full bg-[#f8fafc] min-h-screen px-4 md:px-8 lg:px-10 py-8",
            on_mount=AppState.load_notifications,
        ),
        rx.center(
            rx.vstack(
                rx.text("Vui lòng đăng nhập để xem thông báo.", class_name="text-gray-500"),
                rx.link("Đăng nhập ngay", href="/login", class_name="text-red-500 hover:underline"),
                spacing="2",
            ),
            class_name="min-h-[60vh]",
        ),
    )

