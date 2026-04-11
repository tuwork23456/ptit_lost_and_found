import reflex as rx

from ptit_lost_and_found.state import AppState


def _saved_post_item(post: dict) -> rx.Component:
    post_id = post.get("id").to_string()
    has_image = (post.get("image") != None) & (post.get("image") != "")
    post_type = rx.cond(post.get("type") == "LOST", "Mất đồ", "Nhặt được")
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
                    rx.text("Người đăng:", class_name="text-sm font-semibold text-slate-500 min-w-[74px]"),
                    rx.text(post.get("username"), class_name="text-sm font-bold text-[#ff4500] truncate"),
                    spacing="2",
                    align="center",
                    width="100%",
                    class_name="mb-1.5",
                ),
                rx.hstack(
                    rx.text("Tiêu đề:", class_name="text-sm font-semibold text-slate-500 min-w-[74px]"),
                    rx.text(post.get("title"), class_name="text-sm font-bold text-slate-900 truncate"),
                    spacing="2",
                    align="center",
                    width="100%",
                    class_name="mb-1.5",
                ),
                rx.hstack(
                    rx.text("Mô tả:", class_name="text-sm font-semibold text-slate-500 min-w-[74px]"),
                    rx.text(post.get("description"), class_name="text-sm text-slate-700 truncate"),
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
                        "Xem bài",
                        href="/post/" + post_id,
                        class_name="inline-flex items-center justify-center h-10 min-w-[96px] text-center text-xs font-semibold text-blue-600 bg-blue-50 px-3 py-2 rounded-lg hover:bg-blue-100 transition-all",
                    ),
                    rx.button(
                        "Liên hệ",
                        on_click=AppState.open_chat_with_user_from_post(
                            post.get("user_id"),
                            post.get("username"),
                            post.get("id"),
                            post.get("title"),
                        ),
                        class_name="inline-flex items-center justify-center h-10 min-w-[96px] text-xs font-semibold text-emerald-700 bg-emerald-50 px-3 py-2 rounded-lg hover:bg-emerald-100 transition-all",
                    ),
                    rx.button(
                        "Bỏ lưu",
                        on_click=AppState.toggle_saved_post(post.get("id")),
                        class_name="inline-flex items-center justify-center h-10 min-w-[96px] text-xs font-semibold text-red-600 bg-red-50 px-3 py-2 rounded-lg hover:bg-red-100 transition-all",
                    ),
                    spacing="2",
                    class_name="mt-3",
                    wrap="wrap",
                ),
                class_name="flex-1",
            ),
            class_name="w-full group flex flex-col md:flex-row gap-5 p-4 border border-slate-200 rounded-2xl hover:border-slate-300 hover:shadow-sm transition-all bg-white",
        ),
        class_name="w-full",
    )


def saved_posts_page() -> rx.Component:
    return rx.el.div(
        rx.el.div(
            rx.el.div(
                rx.el.div(
                    rx.hstack(
                        rx.heading("Bài đã lưu", size="6", class_name="text-slate-800"),
                        rx.spacer(),
                        rx.button("Làm mới", on_click=AppState.load_saved_posts, class_name="bg-white border border-slate-200 hover:bg-slate-50 text-sm"),
                        width="100%",
                    ),
                    class_name="sticky top-0 z-10 bg-white px-6 pt-6 pb-4 border-b border-slate-200",
                ),
                rx.el.div(
                    rx.cond(
                        AppState.saved_posts.length() == 0,
                        rx.center(rx.text("Bạn chưa lưu bài viết nào.", class_name="text-slate-400"), class_name="py-12"),
                        rx.vstack(rx.foreach(AppState.saved_posts, _saved_post_item), spacing="4", width="100%", class_name="mt-4"),
                    ),
                    class_name="flex-1 px-6 pb-6 overflow-y-auto",
                ),
                class_name="bg-white rounded-3xl shadow-sm border border-slate-100 overflow-hidden flex flex-col h-[calc(100vh-140px)] min-h-[440px]",
            ),
            class_name="w-full max-w-7xl mx-auto px-4 md:px-8 lg:px-10 py-8",
        ),
        class_name="w-full bg-[#f8fafc] min-h-screen",
        on_mount=[AppState.load_posts, AppState.load_saved_posts],
    )

