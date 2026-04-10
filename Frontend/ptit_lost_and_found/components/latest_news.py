import reflex as rx

from ptit_lost_and_found.state import AppState


def _feed_comment_item(comment: dict) -> rx.Component:
    comment_id = comment.get("id")
    is_reply = comment.get("is_reply")
    reply_to = comment.get("reply_to_user")
    is_replying_this = AppState.feed_reply_parent_id == comment_id
    return rx.el.div(
        rx.el.div(
            rx.hstack(
                rx.el.div(
                    rx.icon("user-round", size=12),
                    class_name="w-6 h-6 rounded-full bg-slate-100 text-slate-500 flex items-center justify-center",
                ),
                rx.vstack(
                    rx.hstack(
                        rx.text(comment.get("username"), class_name="text-xs font-semibold text-slate-700"),
                        rx.cond(
                            is_reply & (reply_to != ""),
                            rx.hstack(
                                rx.text("tra loi", class_name="text-[11px] text-slate-400"),
                                rx.text(reply_to, class_name="text-[11px] text-slate-400"),
                                spacing="1",
                            ),
                        ),
                        spacing="2",
                    ),
                    rx.text(comment.get("content"), class_name="text-sm text-slate-700 whitespace-pre-line"),
                    rx.hstack(
                        rx.text(comment.get("created_at"), class_name="text-xs text-slate-500"),
                        rx.el.button(
                            "Tra loi",
                            on_click=AppState.set_feed_reply_target(comment_id, comment.get("username")),
                            class_name="text-[11px] font-semibold text-[#ff4500] hover:underline",
                        ),
                        spacing="3",
                    ),
                    align="start",
                    spacing="1",
                ),
                width="100%",
                align="start",
                spacing="2",
            ),
            rx.cond(
                is_replying_this,
                rx.form(
                    rx.vstack(
                        rx.input(
                            value=AppState.feed_reply_text,
                            on_change=AppState.set_feed_reply_text,
                            placeholder="Nhap tra loi...",
                            class_name="w-full bg-white border border-slate-200 rounded-full px-4 py-2 text-sm",
                        ),
                        rx.hstack(
                            rx.spacer(),
                            rx.el.button(
                                "Huy",
                                type="button",
                                on_click=AppState.cancel_feed_reply,
                                class_name="px-3 py-1.5 text-xs rounded-full border border-slate-200 hover:bg-slate-50",
                            ),
                            rx.el.button(
                                "Gui",
                                type="submit",
                                class_name="px-4 py-1.5 text-xs rounded-full bg-[#ff4500] text-white font-semibold hover:bg-[#e03d00]",
                            ),
                            width="100%",
                        ),
                        spacing="2",
                        width="100%",
                    ),
                    on_submit=AppState.submit_feed_reply_current,
                    class_name="mt-2",
                ),
            ),
            class_name="py-2 border-b border-slate-100 last:border-b-0",
            style={"marginLeft": f"{comment.get('indent_px', 0)}px"},
        ),
        width="100%",
    )


def _feed_comments_modal() -> rx.Component:
    return rx.cond(
        AppState.show_feed_comments_modal,
        rx.el.div(
            rx.el.div(
                rx.el.div(
                    rx.hstack(
                        rx.text("Binh luan", class_name="text-base font-bold text-slate-800"),
                        rx.spacer(),
                        rx.el.button(
                            "✕",
                            on_click=AppState.close_feed_comments_modal,
                            class_name="w-8 h-8 rounded-full hover:bg-slate-100 text-slate-500",
                        ),
                        width="100%",
                        align="center",
                    ),
                    class_name="p-4 border-b border-slate-100",
                ),
                rx.el.div(
                    rx.vstack(
                        rx.text(AppState.feed_comment_post_title, class_name="font-bold text-slate-800"),
                        rx.hstack(
                            rx.text(AppState.feed_comment_post_owner, class_name="text-xs text-slate-600"),
                            rx.text("•", class_name="text-slate-300"),
                            rx.text(AppState.feed_comment_post_created_at, class_name="text-xs text-slate-400"),
                            spacing="2",
                        ),
                        rx.text(AppState.feed_comment_post_description, class_name="text-sm text-slate-600 whitespace-pre-line"),
                        rx.cond(
                            AppState.feed_comment_post_image != "",
                            rx.image(
                                src=AppState.feed_comment_post_image,
                                class_name="w-full rounded-xl object-cover max-h-56",
                            ),
                        ),
                        align="start",
                        spacing="2",
                        width="100%",
                    ),
                    class_name="p-4 border-b border-slate-100 bg-slate-50/60",
                ),
                rx.el.div(
                    rx.cond(
                        AppState.feed_threaded_comments.length() == 0,
                        rx.text("Chua co binh luan nao.", class_name="text-xs text-slate-400"),
                        rx.el.div(
                            rx.foreach(AppState.feed_threaded_comments, _feed_comment_item),
                            class_name="max-h-[360px] overflow-y-auto pr-1",
                        ),
                    ),
                    class_name="p-4",
                ),
                rx.form(
                    rx.hstack(
                        rx.input(
                            placeholder="Viet binh luan...",
                            value=AppState.feed_comment_text,
                            on_change=AppState.set_feed_comment_text,
                            class_name="flex-1 bg-slate-50 border border-slate-200 rounded-full px-4 py-2 text-sm",
                        ),
                        rx.el.button(
                            "Dang",
                            type="submit",
                            class_name="bg-[#ff4500] text-white px-4 py-2 rounded-full text-sm font-semibold hover:bg-[#e03d00]",
                        ),
                        width="100%",
                        align="center",
                    ),
                    on_submit=AppState.submit_feed_comment(AppState.feed_comment_post_id),
                    class_name="p-4 border-t border-slate-100",
                ),
                class_name="w-full max-w-2xl bg-white rounded-2xl shadow-2xl overflow-hidden",
            ),
            class_name="fixed inset-0 bg-black/40 z-[9998] flex items-center justify-center p-4",
        ),
    )


def _feed_tabs() -> rx.Component:
    def _tab(label: str, value: str) -> rx.Component:
        return rx.el.button(
            label,
            on_click=AppState.set_feed_filter(value),
            class_name=rx.cond(
                AppState.feed_filter == value,
                "text-sm font-bold text-white bg-[#ff4500] px-3 py-1.5 rounded-full shadow-sm ring-1 ring-[#ff4500]/30 transition",
                "text-sm font-semibold text-slate-700 hover:text-[#ff4500] hover:bg-orange-50 px-3 py-1.5 rounded-full transition",
            ),
        )

    return rx.hstack(
        rx.el.h2(
            "Ban tin",
            class_name="text-2xl md:text-[30px] font-black tracking-tight text-slate-800 mr-2",
        ),
        rx.hstack(
            _tab("Mat do", "LOST"),
            _tab("Nhat duoc", "FOUND"),
            spacing="1",
            class_name="bg-slate-100 p-1 rounded-full",
        ),
        spacing="2",
        align="center",
        wrap="wrap",
    )


def _feed_panel_header() -> rx.Component:
    return rx.el.div(
        rx.el.div(
            rx.el.span(
                "Cong dong PTIT",
                class_name="inline-flex items-center rounded-full bg-orange-50 border border-orange-200 text-[#ff4500] text-[11px] font-semibold px-2.5 py-1",
            ),
            rx.text(
                "Ban tin tim do that lac danh cho sinh vien Hoc vien Cong nghe Buu chinh Vien thong.",
                class_name="text-sm text-slate-500 mt-2",
            ),
            class_name="w-full",
        ),
        _feed_tabs(),
        class_name="sticky top-0 z-10 bg-white px-3 md:px-4 pt-3 pb-2 border-b border-slate-200",
    )


def _post_card(post: dict) -> rx.Component:
    post_id = post["id"].to_string()
    has_image = (post.get("image") != None) & (post.get("image") != "")
    post_type = rx.cond(post.get("type") == "FOUND", "Nhat duoc", "Mat do")
    return rx.el.div(
        rx.el.div(
            rx.vstack(
                rx.el.div(
                    rx.cond(
                        has_image,
                        rx.image(src=post["image"], class_name="w-full h-full object-cover object-center"),
                        rx.el.div(
                            rx.icon("image-off", size=16, class_name="text-slate-300"),
                            class_name="w-full h-full flex items-center justify-center bg-slate-100",
                        ),
                    ),
                    class_name="w-full md:w-52 h-40 md:h-32 rounded-xl overflow-hidden",
                ),
                rx.hstack(
                    rx.el.span(post_type, class_name="bg-orange-50 text-[#ff4500] text-[10px] font-bold px-2 py-1 rounded-full"),
                    rx.el.span(post.get("category"), class_name="bg-purple-50 text-purple-600 text-[10px] font-bold px-2 py-1 rounded-full"),
                    spacing="2",
                    wrap="wrap",
                    class_name="w-full",
                ),
                spacing="2",
                align="start",
                class_name="w-full md:w-52",
            ),
            rx.el.div(
                rx.hstack(
                    rx.text("Nguoi dang:", class_name="text-sm font-semibold text-slate-500 min-w-[74px]"),
                    rx.text(post.get("username"), class_name="text-sm font-bold text-[#ff4500] truncate"),
                    spacing="2",
                    align="center",
                    width="100%",
                    class_name="mb-1.5",
                ),
                rx.hstack(
                    rx.text("Tieu de:", class_name="text-sm font-semibold text-slate-500 min-w-[74px]"),
                    rx.text(
                        post["title"],
                        class_name="text-sm font-bold text-slate-900 truncate",
                    ),
                    spacing="2",
                    align="center",
                    width="100%",
                    class_name="mb-1.5",
                ),
                rx.hstack(
                    rx.text("Mo ta:", class_name="text-sm font-semibold text-slate-500 min-w-[74px]"),
                    rx.text(post["description"], class_name="text-sm text-slate-700 truncate"),
                    spacing="2",
                    align="center",
                    width="100%",
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
                        rx.text(post.get("created_date"), class_name="text-xs font-medium"),
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
                    class_name="text-slate-500 mt-2.5",
                    spacing="2",
                    wrap="wrap",
                    align="center",
                ),
                rx.hstack(
                    rx.link(
                        rx.hstack(rx.icon("info", size=14), rx.text("Chi tiet", class_name="text-xs"), spacing="1"),
                        href="/post/" + post_id,
                        class_name="text-slate-600 hover:text-[#ff4500] hover:bg-orange-50 px-2.5 py-1.5 rounded-lg transition",
                    ),
                    rx.el.button(
                        rx.hstack(rx.icon("send", size=14), rx.text("Lien he", class_name="text-xs"), spacing="1"),
                        on_click=AppState.open_chat_with_user_from_post(
                            post.get("user_id"),
                            post.get("username"),
                            post.get("id"),
                            post.get("title"),
                        ),
                        class_name="text-slate-600 hover:text-[#ff4500] hover:bg-orange-50 px-2.5 py-1.5 rounded-lg transition",
                    ),
                    rx.el.button(
                        rx.hstack(rx.icon("message-circle", size=14), rx.text("Binh luan", class_name="text-xs"), spacing="1"),
                        on_click=AppState.open_feed_comments_modal(
                            post.get("id"),
                            post.get("title"),
                            post.get("user_id"),
                            post.get("username"),
                            post.get("created_at"),
                            post.get("description"),
                            post.get("image"),
                        ),
                        class_name="text-slate-600 hover:text-[#ff4500] hover:bg-orange-50 px-2.5 py-1.5 rounded-lg transition",
                    ),
                    rx.cond(
                        ~AppState.is_admin,
                        rx.el.button(
                            rx.hstack(rx.icon("triangle-alert", size=14), rx.text("Bao cao", class_name="text-xs"), spacing="1"),
                            on_click=AppState.toggle_feed_report_box(post.get("id")),
                            class_name="text-slate-600 hover:text-[#ff4500] hover:bg-orange-50 px-2.5 py-1.5 rounded-lg transition",
                        ),
                    ),
                    rx.el.button(
                        rx.hstack(
                            rx.icon("bookmark", size=14),
                            rx.text(
                                rx.cond(post.get("is_saved"), "Da luu", "Luu"),
                                class_name="text-xs",
                            ),
                            spacing="1",
                        ),
                        on_click=AppState.toggle_saved_post(post.get("id")),
                        class_name=rx.cond(
                            post.get("is_saved"),
                            "text-emerald-700 bg-emerald-50 px-2.5 py-1.5 rounded-lg transition",
                            "text-slate-600 hover:text-[#ff4500] hover:bg-orange-50 px-2.5 py-1.5 rounded-lg transition",
                        ),
                    ),
                    rx.cond(
                        AppState.is_admin,
                        rx.el.button(
                            rx.hstack(rx.icon("trash-2", size=14), rx.text("Go bai", class_name="text-xs"), spacing="1"),
                            on_click=AppState.admin_remove_post(post.get("id")),
                            class_name="text-red-600 hover:text-red-700 hover:bg-red-50 px-2.5 py-1.5 rounded-lg transition",
                        ),
                    ),
                    spacing="2",
                    align="center",
                    class_name="mt-2",
                    wrap="wrap",
                ),
                rx.cond(
                    AppState.feed_report_post_id == post.get("id"),
                    rx.el.div(
                        rx.text_area(
                            placeholder="Nhap ly do bao cao...",
                            value=AppState.feed_report_reason,
                            on_change=AppState.set_feed_report_reason,
                            class_name="w-full bg-white border border-slate-200 rounded-xl p-3 text-sm min-h-[88px]",
                        ),
                        rx.hstack(
                            rx.button(
                                "Huy",
                                on_click=AppState.toggle_feed_report_box(post.get("id")),
                                class_name="bg-slate-100 hover:bg-slate-200 text-slate-700 font-semibold py-2 px-4 rounded-xl text-sm",
                            ),
                            rx.button(
                                "Gui bao cao",
                                on_click=AppState.submit_feed_report(post.get("id")),
                                class_name="bg-red-500 hover:bg-red-600 text-white font-semibold py-2 px-4 rounded-xl text-sm",
                            ),
                            spacing="2",
                        ),
                        rx.cond(
                            AppState.feed_action_message != "",
                            rx.text(
                                AppState.feed_action_message,
                                class_name="text-xs text-slate-600",
                            ),
                        ),
                        class_name="mt-3 bg-slate-50 border border-slate-200 rounded-2xl p-3.5",
                    ),
                ),
                class_name="flex-1",
            ),
            class_name="w-full group flex flex-col md:flex-row gap-5 p-4 border border-slate-200 rounded-2xl hover:border-slate-300 hover:shadow-sm transition-all bg-white",
        ),
        class_name="w-full",
    )


def _feed_grid() -> rx.Component:
    return rx.el.div(
        rx.cond(
            AppState.posts_loading,
            rx.el.div(
                rx.el.div(class_name="h-5 w-44 bg-slate-200 rounded animate-pulse mb-3"),
                rx.el.div(class_name="h-4 w-64 bg-slate-100 rounded animate-pulse mb-3"),
                rx.el.div(class_name="h-40 w-full bg-slate-100 rounded-xl animate-pulse"),
                class_name="py-4",
            ),
            rx.cond(
                AppState.feed_filtered_posts.length() == 0,
                rx.el.div(
                    rx.icon("inbox", size=18),
                    rx.text("Chua co bai viet nao.", class_name="text-sm"),
                    class_name="text-center py-12 text-gray-400 flex flex-col items-center gap-2",
                ),
                rx.el.div(
                    rx.foreach(AppState.feed_filtered_posts, _post_card),
                    class_name="space-y-3 w-full",
                ),
            ),
        ),
        class_name="w-full",
    )


def latest_news() -> rx.Component:
    return rx.vstack(
        rx.el.div(
            _feed_panel_header(),
            rx.el.div(
                _feed_grid(),
                class_name="px-3 md:px-4 py-3 overflow-y-auto max-h-[calc(100vh-190px)]",
            ),
            class_name="w-full bg-white rounded-2xl border border-slate-300 shadow-sm overflow-hidden",
        ),
        _feed_comments_modal(),
        width="100%",
        align="stretch",
        class_name="w-full overflow-visible",
    )

