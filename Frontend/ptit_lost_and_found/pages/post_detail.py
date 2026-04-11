import reflex as rx

from ptit_lost_and_found.state import AppState


def _comment_item(comment: dict) -> rx.Component:
    comment_id = comment.get("id")
    is_replying_this = AppState.post_reply_parent_id == comment_id
    return rx.el.div(
        rx.el.div(
            rx.hstack(
                rx.el.div(
                    rx.icon("user-round", size=14),
                    class_name="w-8 h-8 rounded-full bg-slate-200 flex-shrink-0 flex items-center justify-center text-slate-600",
                ),
                rx.el.div(
                    rx.hstack(
                        rx.el.span(comment.get("username"), class_name="font-bold text-sm text-gray-800"),
                        rx.cond(
                            comment.get("is_reply") & (comment.get("reply_to_user") != ""),
                            rx.hstack(
                                rx.el.span("trả lời", class_name="text-[11px] text-gray-400"),
                                rx.el.span(comment.get("reply_to_user"), class_name="text-[11px] text-gray-400"),
                                spacing="1",
                            ),
                        ),
                        rx.el.span(comment.get("created_at"), class_name="text-[10px] text-gray-400"),
                        spacing="1",
                        wrap="wrap",
                    ),
                    rx.el.p(comment.get("content"), class_name="text-sm text-gray-700 whitespace-pre-line leading-6"),
                    rx.el.button(
                        "Trả lời",
                        on_click=AppState.set_post_reply_target(comment_id, comment.get("username")),
                        class_name="text-[11px] font-semibold text-[#ff4500] hover:underline mt-1",
                    ),
                    class_name="flex bg-slate-50 flex-col rounded-2xl rounded-tl-none px-4 py-2.5 border border-slate-200",
                ),
                align="start",
                spacing="3",
            ),
            rx.cond(
                is_replying_this,
                rx.form(
                    rx.vstack(
                        rx.input(
                            value=AppState.post_reply_text,
                            on_change=AppState.set_post_reply_text,
                            placeholder="Nhập trả lời...",
                            class_name="w-full bg-white border border-slate-200 rounded-full px-4 py-2 text-sm",
                        ),
                        rx.hstack(
                            rx.spacer(),
                            rx.el.button(
                                "Hủy",
                                type="button",
                                on_click=AppState.cancel_post_reply,
                                class_name="px-3 py-1.5 text-xs rounded-full border border-slate-200 hover:bg-slate-50",
                            ),
                            rx.el.button(
                                "Gửi",
                                type="submit",
                                class_name="px-4 py-1.5 text-xs rounded-full bg-[#ff4500] text-white font-semibold hover:bg-[#e03d00]",
                            ),
                            width="100%",
                        ),
                        spacing="2",
                        width="100%",
                    ),
                    on_submit=AppState.submit_post_reply_current,
                    class_name="mt-1.5 ml-11",
                ),
            ),
            class_name="w-full",
            style={"marginLeft": f"{comment.get('indent_px', 0)}px"},
        ),
        width="100%",
    )


def post_detail_page() -> rx.Component:
    post = AppState.current_post
    post_id = post.get("id").to_string()
    post_type = rx.cond(post.get("type") == "FOUND", "Nhặt được", "Mất đồ")
    status_text = rx.cond(post.get("is_resolved") == True, "Đã giải quyết", "Đang xử lý")

    detail_view = rx.vstack(
        rx.el.div(
            rx.hstack(
                rx.text("Người đăng:", class_name="text-sm font-semibold text-slate-500 min-w-[90px]"),
                rx.link(
                    rx.text(post.get("username"), class_name="text-sm font-bold text-[#ff4500]"),
                    href="/user/" + post.get("user_id").to_string(),
                ),
                spacing="2",
                align="center",
                width="100%",
            ),
            rx.hstack(
                rx.text("Tiêu đề:", class_name="text-sm font-semibold text-slate-500 min-w-[90px]"),
                rx.heading(
                    rx.cond(post.get("title") != None, post.get("title"), "Không có tiêu đề"),
                    size="5",
                    class_name="text-slate-900 tracking-tight leading-tight",
                ),
                spacing="2",
                align="center",
                wrap="wrap",
                width="100%",
            ),
            rx.hstack(
                rx.text("Mô tả:", class_name="text-sm font-semibold text-slate-500 min-w-[90px]"),
                rx.el.p(
                    post.get("description"),
                    class_name="text-sm leading-6 text-slate-700 whitespace-pre-line",
                ),
                spacing="2",
                align="start",
                width="100%",
            ),
            spacing="3",
            align="start",
            width="100%",
            class_name="rounded-2xl border border-slate-200 bg-slate-50/70 p-4 md:p-5",
        ),
        rx.hstack(
            rx.cond(
                (post.get("location") != None) & (post.get("location") != ""),
                rx.hstack(
                    rx.icon("map-pin", size=12),
                    rx.text(post.get("location"), class_name="text-xs font-medium"),
                    spacing="2",
                    align="center",
                    class_name="px-2 py-1 rounded-md bg-slate-50 border border-slate-200/80",
                ),
            ),
            rx.hstack(
                rx.icon("calendar", size=12),
                rx.text(
                    rx.cond(
                        (post.get("created_date") != None) & (post.get("created_date") != ""),
                        post.get("created_date"),
                        post.get("created_at"),
                    ),
                    class_name="text-xs font-medium",
                ),
                spacing="2",
                align="center",
                class_name="px-2 py-1 rounded-md bg-slate-50 border border-slate-200/80",
            ),
            rx.cond(
                (post.get("created_time") != None) & (post.get("created_time") != ""),
                rx.hstack(
                    rx.icon("clock-3", size=12),
                    rx.text(post.get("created_time"), class_name="text-xs font-medium"),
                    spacing="2",
                    align="center",
                    class_name="px-2 py-1 rounded-md bg-slate-50 border border-slate-200/80",
                ),
            ),
            class_name="text-slate-500",
            spacing="2",
            wrap="wrap",
            align="center",
            width="100%",
        ),
        rx.cond(
            (post.get("image") != None) & (post.get("image") != ""),
            rx.el.div(
                rx.image(src=post.get("image"), class_name="w-full h-64 md:h-80 object-cover rounded-2xl border border-slate-200"),
                class_name="rounded-2xl bg-slate-50 p-2 border border-slate-200",
            ),
        ),
        rx.hstack(
            rx.el.span(post_type, class_name="text-[11px] font-semibold px-3 py-1 rounded-full bg-orange-50 text-orange-700 border border-orange-100"),
            rx.el.span(post.get("category"), class_name="text-[11px] font-semibold px-3 py-1 rounded-full bg-violet-50 text-violet-700 border border-violet-100"),
            rx.el.span(status_text, class_name="text-[11px] font-medium px-3 py-1 rounded-full bg-slate-100 text-slate-600 border border-slate-200"),
            spacing="2",
            wrap="wrap",
            width="100%",
        ),
        rx.el.div(
            rx.hstack(
                rx.button(
                    "Liên hệ",
                    on_click=AppState.open_chat_with_user_from_post(
                        post.get("user_id"),
                        post.get("username"),
                        post.get("id"),
                        post.get("title"),
                    ),
                    class_name="inline-flex items-center justify-center h-10 bg-[#ff4500] hover:bg-[#e03d00] text-white font-semibold px-4 rounded-xl text-sm shadow-sm",
                ),
                rx.link(
                    "Chi tiết",
                    href="/post/" + post_id,
                    class_name="inline-flex items-center justify-center h-10 bg-white hover:bg-slate-50 text-slate-700 font-medium px-4 rounded-xl text-sm border border-slate-200",
                ),
                rx.button(
                    rx.cond(AppState.is_current_post_saved, "Đã lưu bài viết", "Lưu bài viết"),
                    on_click=AppState.toggle_saved_post(post.get("id")),
                    class_name=rx.cond(
                        AppState.is_current_post_saved,
                        "inline-flex items-center justify-center h-10 bg-emerald-50 hover:bg-emerald-100 text-emerald-700 font-medium px-4 rounded-xl text-sm border border-emerald-200",
                        "inline-flex items-center justify-center h-10 bg-white hover:bg-slate-50 text-slate-700 font-medium px-4 rounded-xl text-sm border border-slate-200",
                    ),
                ),
                rx.cond(
                    AppState.is_admin,
                    rx.button(
                        "Gỡ bài",
                        on_click=AppState.admin_remove_post(post.get("id")),
                        class_name="inline-flex items-center justify-center h-10 bg-white hover:bg-red-50 text-red-700 font-medium px-4 rounded-xl text-sm border border-red-200",
                    ),
                    rx.button(
                        "Báo cáo",
                        on_click=AppState.open_post_report_box,
                        class_name="inline-flex items-center justify-center h-10 bg-white hover:bg-amber-50 text-amber-700 font-medium px-4 rounded-xl text-sm border border-amber-200",
                    ),
                ),
                rx.cond(
                    AppState.is_current_post_owner & (post.get("is_resolved") != True),
                    rx.button(
                        "Đánh dấu đã giải quyết",
                        on_click=AppState.resolve_current_post,
                        class_name="inline-flex items-center justify-center h-10 bg-slate-800 hover:bg-slate-900 text-white font-medium px-4 rounded-xl text-sm",
                    ),
                ),
                spacing="2",
                wrap="wrap",
                width="100%",
            ),
            class_name="rounded-2xl border border-slate-200 bg-slate-50/70 p-4",
        ),
        rx.cond(
            AppState.show_post_report_box,
            rx.vstack(
                rx.text_area(
                    placeholder=rx.cond(
                        AppState.post_report_mode == "report",
                        "Nhập lý do báo cáo...",
                        "Nhập lý do yêu cầu gỡ bài...",
                    ),
                    value=AppState.report_reason,
                    on_change=AppState.set_report_reason,
                    class_name="w-full bg-white border border-slate-200 rounded-xl p-3 text-sm min-h-[90px]",
                ),
                rx.hstack(
                    rx.button(
                        "Hủy",
                        on_click=AppState.close_post_report_box,
                        class_name="bg-slate-100 hover:bg-slate-200 text-slate-700 font-semibold py-2 px-4 rounded-xl text-sm",
                    ),
                    rx.cond(
                        AppState.post_report_mode == "report",
                        rx.button(
                            "Gửi báo cáo",
                            on_click=AppState.report_current_post,
                            class_name="bg-red-500 hover:bg-red-600 text-white font-semibold py-2 px-4 rounded-xl text-sm",
                        ),
                        rx.button(
                            "Gửi yêu cầu gỡ bài",
                            on_click=AppState.request_remove_current_post,
                            class_name="bg-red-500 hover:bg-red-600 text-white font-semibold py-2 px-4 rounded-xl text-sm",
                        ),
                    ),
                    spacing="2",
                    wrap="wrap",
                ),
                width="100%",
                align="start",
                class_name="bg-amber-50/40 border border-amber-200/70 rounded-2xl p-4",
            ),
        ),
        rx.cond(
            AppState.post_action_message != "",
            rx.text(
                AppState.post_action_message,
                class_name="text-sm text-slate-600",
            ),
        ),
        spacing="5",
        width="100%",
        class_name="bg-white rounded-3xl shadow-sm border border-slate-200 p-5 md:p-7",
    )

    comments_view = rx.el.div(
        rx.hstack(
            rx.heading("Bình luận", size="5"),
            rx.text(f"({AppState.post_threaded_comments.length()})", class_name="text-red-500"),
            width="100%",
            align="center",
            class_name="pb-1",
        ),
        rx.el.div(class_name="h-px bg-slate-200 my-2"),
        rx.cond(
            AppState.is_logged_in,
            rx.form(
                rx.vstack(
                    rx.text_area(
                        placeholder="Viết bình luận của bạn...",
                        value=AppState.comment_text,
                        on_change=AppState.set_comment_text,
                        class_name="w-full bg-slate-50 border border-slate-200 rounded-xl px-3 py-2.5 text-sm outline-none min-h-[82px]",
                    ),
                    rx.hstack(
                        rx.spacer(),
                        rx.button(
                            "Đăng",
                            type="submit",
                            class_name="bg-[#ff4500] hover:bg-[#e03d00] text-white px-4 py-1.5 rounded-xl font-semibold text-sm",
                        ),
                        width="100%",
                    ),
                    spacing="2",
                    width="100%",
                ),
                on_submit=AppState.submit_comment,
                class_name="mb-4 rounded-2xl bg-slate-50 border border-slate-200 p-3",
            ),
            rx.el.div(
                rx.text("Vui lòng đăng nhập để có thể bình luận.", class_name="text-gray-500 text-sm"),
                rx.link("Đăng nhập ngay", href="/login", class_name="text-red-500 hover:underline text-sm"),
                class_name="py-4 mb-4 bg-slate-50 rounded-xl border border-slate-200 text-center space-y-2",
            ),
        ),
        rx.cond(
            AppState.post_threaded_comments.length() == 0,
            rx.el.div(
                "Chưa có bình luận nào. Hãy là người đầu tiên!",
                class_name="text-center text-slate-400 py-5 text-sm",
            ),
            rx.vstack(
                rx.foreach(AppState.post_threaded_comments, _comment_item),
                spacing="3",
                width="100%",
                class_name="rounded-2xl bg-white",
            ),
        ),
        class_name="bg-white rounded-3xl shadow-sm border border-slate-200 p-5 md:p-6 w-full",
    )

    not_found_view = rx.center(
        rx.vstack(
            rx.heading("Không tìm thấy bài viết!", size="6"),
            rx.link("Về trang chủ", href="/", class_name="text-red-500 hover:underline"),
            spacing="3",
        ),
        class_name="min-h-[60vh]",
    )

    return rx.el.div(
        rx.cond(
            AppState.post_loading,
            rx.center(
                rx.el.div(class_name="animate-spin rounded-full h-12 w-12 border-b-2 border-red-500"),
                class_name="min-h-[60vh]",
            ),
            rx.cond(
                post_id == "",
                not_found_view,
                rx.vstack(detail_view, comments_view, spacing="6", width="100%"),
            ),
        ),
        class_name="w-full bg-[#f8fafc] min-h-screen max-w-7xl mx-auto px-4 md:px-8 lg:px-10 py-8",
        on_mount=AppState.load_post_detail,
    )

