import reflex as rx

from ptit_lost_and_found.state import AppState


def _conversation_item(conv: dict) -> rx.Component:
    is_active = AppState.current_chat_receiver_id == conv["id"]
    return rx.el.button(
        rx.hstack(
            rx.el.div(
                "U",
                class_name=rx.cond(
                    is_active,
                    "w-10 h-10 rounded-full bg-orange-500 text-white flex items-center justify-center font-bold text-xs flex-shrink-0",
                    "w-10 h-10 rounded-full bg-slate-200 text-slate-700 flex items-center justify-center font-bold text-xs flex-shrink-0",
                ),
            ),
            rx.vstack(
                rx.hstack(
                    rx.el.span(
                        conv["username"],
                        class_name=rx.cond(
                            is_active,
                            "text-sm text-slate-900 font-semibold",
                            "text-sm text-slate-700 font-medium",
                        ),
                    ),
                    rx.cond(
                        (conv["unread_count"] != None) & (conv["unread_count"] != 0),
                        rx.el.span(
                            conv["unread_count"],
                            class_name="bg-rose-500 text-white text-[10px] font-bold min-w-4 h-4 px-1 rounded-full flex items-center justify-center",
                        ),
                    ),
                    justify="between",
                    width="100%",
                    align="center",
                ),
                rx.el.p(conv["last_message"], class_name="text-xs truncate text-slate-500"),
                width="100%",
                spacing="1",
                align="start",
            ),
            spacing="3",
            width="100%",
            align="center",
        ),
        on_click=AppState.open_chat(conv["id"], conv["username"]),
        class_name=rx.cond(
            is_active,
            "w-full flex items-center gap-3 px-3 py-3 bg-orange-50/70 border-l-2 border-l-orange-500 border-b border-orange-100 text-left transition",
            "w-full flex items-center gap-3 px-3 py-3 hover:bg-slate-50 transition border-b border-slate-100 text-left",
        ),
    )


def _message_item(msg: dict) -> rx.Component:
    is_me = msg["sender_id"].to_string() == AppState.user_id
    return rx.el.div(
        msg["content"],
        class_name=rx.cond(
            is_me,
            "max-w-[80%] px-3.5 py-2 text-sm break-words bg-orange-500 text-white self-end rounded-2xl rounded-br-md shadow-sm",
            "max-w-[80%] px-3.5 py-2 text-sm break-words bg-white border border-slate-200 text-slate-700 self-start rounded-2xl rounded-bl-md shadow-sm",
        ),
    )


def chatbox() -> rx.Component:
    return rx.cond(
        AppState.is_logged_in & AppState.is_chat_open,
        rx.el.div(
            rx.el.div(
                rx.hstack(
                    rx.el.span("Tin nhan", class_name="font-semibold text-sm text-slate-800"),
                    rx.spacer(),
                    rx.el.button(
                        rx.icon("refresh-cw", size=14),
                        on_click=AppState.refresh_chat_data,
                        class_name="w-8 h-8 rounded-full border border-slate-200 text-slate-500 hover:bg-slate-100 hover:text-slate-700 transition flex items-center justify-center",
                    ),
                    rx.el.button(
                        rx.icon("x", size=14),
                        on_click=AppState.close_chat,
                        class_name="w-8 h-8 rounded-full border border-slate-200 text-slate-500 hover:bg-slate-100 hover:text-slate-700 transition flex items-center justify-center",
                    ),
                    width="100%",
                    align="center",
                ),
                class_name="bg-white px-4 py-3 border-b border-slate-200",
            ),
            rx.el.div(
                rx.el.div(
                    rx.text(
                        "Hoi thoai",
                        class_name="text-[11px] uppercase tracking-wide font-semibold text-slate-400 px-3 pt-3 pb-2",
                    ),
                    rx.cond(
                        AppState.conversations_loading,
                        rx.center(
                            rx.el.div(
                                class_name="animate-spin rounded-full h-5 w-5 border-b-2 border-orange-500"
                            ),
                            class_name="py-10",
                        ),
                        rx.cond(
                            AppState.conversations.length() == 0,
                            rx.center(
                                rx.text(
                                    "Chua co tin nhan nao.",
                                    class_name="text-sm text-slate-400",
                                ),
                                class_name="h-full",
                            ),
                            rx.vstack(
                                rx.foreach(AppState.conversations, _conversation_item),
                                spacing="0",
                                width="100%",
                            ),
                        ),
                    ),
                    class_name="w-[230px] h-full overflow-y-auto bg-white",
                ),
                rx.el.div(
                    rx.hstack(
                        rx.text("Dang chat voi:", class_name="text-xs text-slate-500"),
                        rx.text(
                            rx.cond(
                                AppState.current_chat_receiver_id > 0,
                                AppState.current_chat_receiver_name,
                                "Chua chon hoi thoai",
                            ),
                            class_name="text-sm font-semibold text-slate-800",
                        ),
                        spacing="2",
                        class_name="px-4 py-3 border-b border-slate-200 bg-white",
                    ),
                    rx.cond(
                        AppState.current_chat_pinned_post.get("post_id") != None,
                        rx.link(
                            rx.hstack(
                                rx.icon("pin", size=14, class_name="text-orange-600"),
                                rx.text(
                                    AppState.current_chat_pinned_post.get("post_title"),
                                    class_name="text-xs font-medium text-orange-700 truncate",
                                ),
                                spacing="2",
                                align="center",
                                class_name="w-full",
                            ),
                            href="/post/" + AppState.current_chat_pinned_post.get("post_id").to_string(),
                            class_name="mx-4 my-2 px-3 py-2 bg-orange-50/70 border border-orange-200 rounded-lg hover:bg-orange-100 transition block",
                        ),
                    ),
                    rx.el.div(
                        rx.cond(
                            AppState.current_chat_receiver_id > 0,
                            rx.cond(
                                AppState.chat_messages.length() == 0,
                                rx.center(
                                    rx.text(
                                        "Chua co tin nhan.",
                                        class_name="text-xs text-slate-400",
                                    ),
                                    class_name="h-full",
                                ),
                                rx.vstack(
                                    rx.foreach(AppState.chat_messages, _message_item),
                                    spacing="3",
                                    width="100%",
                                ),
                            ),
                            rx.center(
                                rx.text(
                                    "Chon mot hoi thoai de bat dau.",
                                    class_name="text-xs text-slate-400",
                                ),
                                class_name="h-full",
                            ),
                        ),
                        class_name="flex-1 bg-slate-50 overflow-y-auto p-4 flex flex-col gap-3",
                    ),
                    rx.form(
                        rx.hstack(
                            rx.input(
                                placeholder="Nhap tin nhan...",
                                value=AppState.chat_input,
                                on_change=AppState.set_chat_input,
                                class_name="flex-1 h-10 bg-white border border-slate-200 rounded-full px-4 py-0 text-sm leading-6 outline-none focus:border-orange-300",
                            ),
                            rx.button(
                                "Gui",
                                type="submit",
                                disabled=(AppState.chat_input == "")
                                | (AppState.current_chat_receiver_id == 0),
                                class_name="text-white bg-orange-500 hover:bg-orange-600 disabled:bg-slate-200 px-4 py-2.5 rounded-full",
                            ),
                            width="100%",
                            align="center",
                        ),
                        on_submit=AppState.send_chat_message,
                        class_name="px-3 pt-2 pb-3 mb-1 bg-white border-t border-slate-200",
                    ),
                    class_name="flex-1 flex flex-col min-w-0",
                ),
                class_name="flex-1 flex min-h-0 divide-x divide-slate-200",
            ),
            class_name="fixed bottom-3 right-2 md:bottom-4 md:right-3 w-[calc(100vw-1rem)] md:w-[560px] max-w-[560px] h-[440px] max-h-[calc(100vh-5rem)] bg-white rounded-2xl shadow-xl flex flex-col border border-slate-200 z-[9999] overflow-hidden",
            on_mount=[AppState.load_conversations, AppState.load_unread_count],
        ),
    )

