import reflex as rx

from ptit_lost_and_found.state import AppState


def _profile_post_card(post: dict) -> rx.Component:
    post_id = post.get("id")
    post_type = rx.cond(post.get("type") == "LOST", "Mất đồ", "Nhặt được")
    has_image = (post.get("image") != None) & (post.get("image") != "")
    return rx.link(
        rx.el.div(
            rx.vstack(
                rx.el.div(
                    rx.cond(
                        has_image,
                        rx.image(
                            src=post.get("image"),
                            alt=rx.cond(post.get("title") != None, post.get("title"), "Post image"),
                            class_name="w-full h-full object-cover object-center",
                        ),
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
                    rx.text("Người đăng:", class_name="text-sm font-semibold text-slate-500 min-w-[74px]"),
                    rx.text(post.get("username"), class_name="text-sm font-bold text-[#ff4500] truncate"),
                    spacing="2",
                    align="center",
                    width="100%",
                    class_name="mb-1.5",
                ),
                rx.hstack(
                    rx.text("Tiêu đề:", class_name="text-sm font-semibold text-slate-500 min-w-[74px]"),
                    rx.text(
                        rx.cond(post.get("title") != None, post.get("title"), "Không có tiêu đề"),
                        class_name="text-sm font-bold text-slate-900 truncate",
                    ),
                    spacing="2",
                    align="center",
                    width="100%",
                    class_name="mb-1.5",
                ),
                rx.hstack(
                    rx.text("Mô tả:", class_name="text-sm font-semibold text-slate-500 min-w-[74px]"),
                    rx.text(
                        rx.cond(
                            (post.get("description") != None) & (post.get("description") != ""),
                            post.get("description"),
                            "Không có mô tả",
                        ),
                        class_name="text-sm text-slate-700 truncate",
                    ),
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
                        rx.hstack(rx.icon("info", size=14), rx.text("Chi tiết", class_name="text-xs"), spacing="1"),
                        href="/post/" + post_id.to_string(),
                        class_name="text-slate-600 hover:text-[#ff4500] hover:bg-orange-50 px-2.5 py-1.5 rounded-lg transition",
                    ),
                    rx.el.button(
                        rx.hstack(rx.icon("send", size=14), rx.text("Liên hệ", class_name="text-xs"), spacing="1"),
                        on_click=AppState.open_chat_with_user_from_post(
                            post.get("user_id"),
                            post.get("username"),
                            post.get("id"),
                            post.get("title"),
                        ),
                        class_name="text-slate-600 hover:text-[#ff4500] hover:bg-orange-50 px-2.5 py-1.5 rounded-lg transition",
                    ),
                    rx.el.button(
                        rx.hstack(rx.icon("message-circle", size=14), rx.text("Bình luận", class_name="text-xs"), spacing="1"),
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
                            rx.hstack(rx.icon("triangle-alert", size=14), rx.text("Báo cáo", class_name="text-xs"), spacing="1"),
                            on_click=AppState.toggle_feed_report_box(post.get("id")),
                            class_name="text-slate-600 hover:text-[#ff4500] hover:bg-orange-50 px-2.5 py-1.5 rounded-lg transition",
                        ),
                    ),
                    spacing="2",
                    align="center",
                    wrap="wrap",
                    class_name="mt-2",
                ),
                class_name="flex-1",
            ),
            class_name="w-full group flex flex-col md:flex-row gap-5 p-4 border border-slate-200 rounded-2xl hover:border-slate-300 hover:shadow-sm transition-all bg-white",
        ),
        href="/post/" + post_id.to_string(),
        class_name="block w-full",
    )


def profile_page() -> rx.Component:
    profile = AppState.profile_data
    pid = profile.get("id")
    is_own = AppState.user_id == pid.to_string()
    join_year = rx.cond(profile.get("created_at") != None, profile.get("created_at"), "?")
    return rx.el.div(
        rx.el.div(
            rx.cond(
                AppState.profile_loading,
                rx.center(
                    rx.el.div(class_name="animate-spin rounded-full h-10 w-10 border-b-2 border-red-500"),
                    class_name="min-h-[60vh]",
                ),
                rx.cond(
                    (pid == None) | (pid == 0),
                    rx.center(
                        rx.vstack(
                            rx.text("Không tìm thấy người dùng.", class_name="text-slate-500 text-lg font-medium"),
                            rx.link("← Về trang chủ", href="/", class_name="text-[#ff4500] hover:underline text-sm"),
                            spacing="3",
                        ),
                        class_name="min-h-[60vh]",
                    ),
                    rx.vstack(
                        rx.el.div(
                            rx.hstack(
                                rx.el.div(
                                    rx.icon("user-round", size=24),
                                    class_name="w-16 h-16 rounded-2xl bg-orange-50 text-[#ff4500] flex items-center justify-center border border-orange-100",
                                ),
                                rx.vstack(
                                    rx.heading(
                                        rx.cond(profile.get("username") != None, profile.get("username"), "User"),
                                        size="6",
                                        class_name="text-slate-900",
                                    ),
                                    rx.hstack(
                                        rx.el.span(
                                            rx.cond(profile.get("role") != None, profile.get("role"), "USER"),
                                            class_name="text-[11px] font-semibold px-2 py-0.5 rounded bg-slate-100 text-slate-700 border border-slate-200",
                                        ),
                                        rx.text("Tham gia:", class_name="text-sm text-slate-500"),
                                        rx.text(join_year, class_name="text-sm text-slate-600"),
                                        spacing="2",
                                        align="center",
                                    ),
                                    spacing="1",
                                    align="start",
                                ),
                                rx.spacer(),
                                rx.cond(
                                    ~is_own,
                                    rx.button(
                                        "Liên hệ",
                                        on_click=AppState.open_chat_with_user(
                                            pid,
                                            rx.cond(profile.get("username") != None, profile.get("username"), "User"),
                                        ),
                                        class_name="bg-[#ff4500] hover:bg-[#e03d00] text-white font-semibold px-4 py-2 rounded-xl text-sm",
                                    ),
                                ),
                                width="100%",
                                align="center",
                            ),
                            rx.el.div(
                                rx.text("Bài đăng", class_name="text-xs uppercase tracking-wide text-slate-500 font-semibold"),
                                rx.text(AppState.profile_posts_count, class_name="text-2xl font-bold text-slate-800"),
                                class_name="mt-5 pt-4 border-t border-slate-200",
                            ),
                            class_name="bg-white rounded-3xl border border-slate-200 shadow-sm p-5 md:p-6 w-full",
                        ),
                        rx.el.div(
                            rx.hstack(
                                rx.heading(
                                    rx.cond(is_own, "Bài đăng của bạn", "Bài đăng của "),
                                    size="5",
                                    class_name="text-slate-800",
                                ),
                                rx.cond(
                                    ~is_own,
                                    rx.text(rx.cond(profile.get("username") != None, profile.get("username"), "User"), class_name="text-slate-800"),
                                ),
                                rx.text("(", class_name="text-[#ff4500]"),
                                rx.text(AppState.profile_posts_count, class_name="text-[#ff4500]"),
                                rx.text(")", class_name="text-[#ff4500]"),
                                spacing="2",
                                class_name="mb-5",
                            ),
                            rx.cond(
                                AppState.profile_posts_count == 0,
                                rx.el.div(
                                    "Chưa có bài đăng nào.",
                                    class_name="text-center py-14 text-slate-400 text-sm",
                                ),
                                rx.grid(
                                    rx.foreach(AppState.profile_posts, _profile_post_card),
                                    columns="1",
                                    spacing="3",
                                    width="100%",
                                ),
                            ),
                            class_name="bg-white rounded-3xl border border-slate-200 shadow-sm p-5 md:p-6 w-full",
                        ),
                        spacing="6",
                        width="100%",
                    ),
                ),
            ),
            class_name="w-full max-w-7xl mx-auto px-4 md:px-8 lg:px-10 py-10",
        ),
        class_name="w-full bg-[#f8fafc] min-h-screen",
        on_mount=AppState.load_profile,
    )

