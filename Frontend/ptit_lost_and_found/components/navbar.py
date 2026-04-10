import reflex as rx

from ptit_lost_and_found.state import AppState


def navbar() -> rx.Component:
    notification_dropdown = rx.cond(
        AppState.show_notifications,
        rx.el.div(
            rx.hstack(
                rx.el.h3("Thong bao", class_name="font-bold text-slate-800"),
                rx.spacer(),
                rx.el.button(
                    "Danh dau da doc",
                    on_click=AppState.mark_all_notifications_read,
                    class_name="text-[11px] text-red-500 hover:underline",
                ),
                width="100%",
                align="center",
                class_name="px-4 py-3 border-b border-slate-100",
            ),
            rx.cond(
                AppState.notifications.length() == 0,
                rx.el.div("Chua co thong bao nao.", class_name="px-4 py-8 text-center text-sm text-slate-500"),
                rx.el.div(
                    rx.foreach(
                        AppState.notifications,
                        lambda notif: rx.el.button(
                            rx.text(
                                notif.get("message"),
                                class_name=rx.cond(
                                    notif.get("is_read"),
                                    "text-sm text-slate-600 text-left",
                                    "text-sm text-slate-900 font-semibold text-left",
                                ),
                            ),
                            rx.text(notif.get("created_at"), class_name="text-[10px] text-slate-400 mt-1 block text-left"),
                            on_click=AppState.mark_notification_read_and_open(notif.get("id"), notif.get("target_id")),
                            class_name="w-full px-4 py-3 border-b border-slate-50 hover:bg-slate-50 transition text-left",
                        ),
                    ),
                    class_name="max-h-[360px] overflow-y-auto",
                ),
            ),
            class_name="absolute right-0 mt-2 w-80 bg-white border border-slate-200 rounded-xl shadow-xl z-50 overflow-hidden",
        ),
    )

    account_dropdown = rx.cond(
        AppState.show_account_menu,
        rx.el.div(
            rx.link(
                "Trang ca nhan",
                href="/profile",
                on_click=AppState.close_account_menu,
                class_name="block w-full text-left px-4 py-2 text-sm text-slate-700 hover:bg-slate-50",
            ),
            rx.el.button(
                "Dang xuat",
                on_click=AppState.logout,
                class_name="w-full text-left px-4 py-2 text-sm text-red-600 hover:bg-red-50",
            ),
            class_name="absolute right-0 mt-2 w-44 bg-white border border-slate-200 rounded-xl shadow-lg z-50 overflow-hidden",
        ),
    )

    return rx.el.div(
        rx.el.div(
            rx.link(
                rx.hstack(
                    rx.text("ptit", class_name="text-[36px] leading-none font-black tracking-tight text-[#ff4500]"),
                    rx.text("lost&found", class_name="text-[24px] leading-none font-bold tracking-tight text-slate-700 mt-1"),
                    spacing="2",
                    align="end",
                ),
                href="/",
                class_name="px-1 py-1 rounded-lg hover:opacity-90 transition",
            ),
            rx.cond(
                AppState.is_logged_in,
                rx.hstack(
                    rx.el.div(
                        rx.el.button(
                            rx.icon("message-circle", size=18),
                            on_click=AppState.toggle_chat,
                            class_name="relative p-2 rounded-full text-slate-600 hover:bg-slate-100 hover:text-slate-900 transition",
                        ),
                        rx.cond(
                            AppState.unread_message_count > 0,
                            rx.el.span(
                                AppState.unread_message_count,
                                class_name="absolute -top-1 -right-1 bg-red-500 text-white text-[10px] font-bold min-w-4 h-4 px-1 rounded-full flex items-center justify-center",
                            ),
                        ),
                        class_name="relative",
                    ),
                    rx.el.div(
                        rx.el.button(
                            rx.icon("bell", size=18),
                            on_click=AppState.toggle_notifications,
                            class_name="relative p-2 rounded-full text-slate-600 hover:bg-slate-100 hover:text-slate-900 transition",
                        ),
                        rx.cond(
                            AppState.unread_notification_count > 0,
                            rx.el.span(
                                AppState.unread_notification_count,
                                class_name="absolute -top-1 -right-1 bg-red-500 text-white text-[10px] font-bold min-w-4 h-4 px-1 rounded-full flex items-center justify-center",
                            ),
                        ),
                        notification_dropdown,
                        class_name="relative",
                    ),
                    rx.el.div(
                        rx.el.button(
                            rx.hstack(
                                rx.el.div(
                                    rx.icon("user-round", size=16),
                                    class_name="w-8 h-8 rounded-full bg-amber-300 text-amber-900 flex items-center justify-center",
                                ),
                                rx.text(
                                    AppState.username,
                                    class_name="hidden md:inline text-sm font-semibold text-slate-700 max-w-[140px] truncate",
                                ),
                                rx.icon("chevron-down", size=14, class_name="text-slate-500"),
                                spacing="2",
                                align="center",
                            ),
                            on_click=AppState.toggle_account_menu,
                            class_name="rounded-full px-1.5 py-1 hover:bg-slate-100 transition",
                        ),
                        account_dropdown,
                        class_name="relative",
                    ),
                    spacing="3",
                    align="center",
                    class_name="pr-1",
                ),
                rx.link(
                    rx.hstack(
                        rx.icon("log-in", size=14),
                        rx.text("Đăng nhập"),
                        spacing="2",
                        align="center",
                    ),
                    href="/login",
                    class_name="inline-flex items-center justify-center rounded-full bg-gradient-to-r from-[#ff5a3d] to-[#ff4500] px-4 py-2 text-sm font-semibold text-white shadow-sm transition-all hover:from-[#f14b2f] hover:to-[#e03d00] hover:shadow-md",
                ),
            ),
            class_name="w-full px-3 md:px-5 lg:px-6 h-[64px] flex items-center justify-between",
        ),
        class_name="w-full bg-white sticky top-0 z-50 border-b border-slate-200",
        on_mount=[AppState.load_unread_count, AppState.load_notifications, AppState.load_saved_post_ids],
    )

