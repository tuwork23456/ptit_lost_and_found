import reflex as rx

from ptit_lost_and_found.state import AppState


def _moderation_badge(post: dict) -> rx.Component:
    status = rx.cond(post.get("moderation_status") != None, post.get("moderation_status"), "APPROVED")
    label = rx.cond(
        status == "PENDING",
        "Cho duyet",
        rx.cond(status == "REJECTED", "Tu choi", rx.cond(status == "REMOVED", "Da go", "Da duyet")),
    )
    return rx.el.span(
        label,
        class_name=rx.cond(
            status == "PENDING",
            "text-[10px] font-semibold px-2 py-1 rounded-full text-amber-700 bg-amber-50 border border-amber-200",
            rx.cond(
                status == "REJECTED",
                "text-[10px] font-semibold px-2 py-1 rounded-full text-red-700 bg-red-50 border border-red-200",
                rx.cond(
                    status == "REMOVED",
                    "text-[10px] font-semibold px-2 py-1 rounded-full text-slate-700 bg-slate-100 border border-slate-200",
                    "text-[10px] font-semibold px-2 py-1 rounded-full text-emerald-700 bg-emerald-50 border border-emerald-200",
                ),
            ),
        ),
    )


def _resolved_badge(post: dict) -> rx.Component:
    return rx.el.span(
        rx.cond(post.get("is_resolved") == True, "Đã giải quyết", "Đang xử lý"),
        class_name=rx.cond(
            post.get("is_resolved") == True,
            "text-[10px] font-semibold px-2 py-1 rounded-full text-emerald-700 bg-emerald-50 border border-emerald-200",
            "text-[10px] font-semibold px-2 py-1 rounded-full text-slate-600 bg-slate-100 border border-slate-200",
        ),
    )


def _post_item(post: dict) -> rx.Component:
    post_id = post.get("id")
    post_type = rx.cond(post.get("type") == "LOST", "Mất đồ", "Nhặt được")
    has_image = (post.get("image") != None) & (post.get("image") != "")
    return rx.el.div(
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
                rx.el.span(
                    post_type,
                    class_name="bg-orange-50 text-[#ff4500] text-[10px] font-bold px-2 py-1 rounded-full",
                ),
                rx.el.span(
                    post.get("category"),
                    class_name="bg-purple-50 text-purple-600 text-[10px] font-bold px-2 py-1 rounded-full",
                ),
                _moderation_badge(post),
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
                    rx.cond(post.get("description") != None, post.get("description"), ""),
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
                    rx.text(rx.cond(post.get("created_date") != None, post.get("created_date"), ""), class_name="text-xs font-medium"),
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
                spacing="2",
                class_name="mt-2.5 text-slate-500",
                wrap="wrap",
                align="center",
            ),
            rx.hstack(
                rx.link(
                    "Xem",
                    href="/post/" + post_id.to_string(),
                    class_name="text-center text-xs font-semibold text-blue-600 bg-blue-50 px-3 py-2 rounded-lg hover:bg-blue-100 transition-all",
                ),
                rx.button(
                    "Xóa",
                    on_click=AppState.delete_my_post(post_id),
                    class_name="text-xs font-semibold text-red-600 bg-red-50 px-3 py-2 rounded-lg hover:bg-red-100 transition-all",
                ),
                spacing="2",
                class_name="mt-3",
            ),
            class_name="flex-1",
        ),
        class_name="w-full group flex flex-col md:flex-row gap-5 p-4 border border-slate-200 rounded-2xl hover:border-slate-300 hover:shadow-sm transition-all bg-white",
    )


def manage_post_page() -> rx.Component:
    return rx.cond(
        AppState.is_logged_in,
        rx.el.div(
            rx.el.div(
                rx.el.div(
                    rx.el.div(
                        rx.hstack(
                            rx.vstack(
                                rx.heading("Quản lý bài đăng", size="6", class_name="text-slate-800"),
                                rx.text(f"Tổng {AppState.my_posts.length()} bài đã đăng", class_name="text-sm text-slate-500"),
                                spacing="1",
                                align="start",
                            ),
                            rx.link(
                                "+ Đăng tin mới",
                                href="/post",
                                class_name="bg-[#ff4500] hover:bg-[#e03d00] text-white font-semibold px-4 py-2.5 rounded-xl text-sm",
                            ),
                            justify="between",
                            width="100%",
                            align="center",
                        ),
                        class_name="sticky top-0 z-10 bg-white px-5 md:px-6 pt-5 md:pt-6 pb-4 border-b border-slate-200",
                    ),
                    rx.el.div(
                        rx.cond(
                            AppState.posts_loading,
                            rx.el.div(
                                rx.el.div(class_name="h-5 w-40 bg-slate-200 rounded animate-pulse mb-3"),
                                rx.el.div(class_name="h-4 w-64 bg-slate-100 rounded animate-pulse mb-3"),
                                rx.el.div(class_name="h-24 w-full bg-slate-100 rounded-xl animate-pulse"),
                                class_name="py-8",
                            ),
                            rx.cond(
                                AppState.my_posts.length() == 0,
                                rx.center(
                                    rx.vstack(
                                        rx.icon("inbox", size=18, class_name="text-slate-400"),
                                        rx.text("Bạn chưa đăng tin nào.", class_name="text-sm font-medium text-slate-500"),
                                        rx.link(
                                            "Đăng tin ngay",
                                            href="/post",
                                            class_name="bg-[#ff4500] text-white text-sm font-semibold px-5 py-2.5 rounded-xl",
                                        ),
                                        spacing="3",
                                    ),
                                    class_name="py-16",
                                ),
                                rx.vstack(rx.foreach(AppState.my_posts, _post_item), spacing="3"),
                            ),
                        ),
                        class_name="flex-1 px-5 md:px-6 pb-5 md:pb-6 overflow-y-auto",
                    ),
                    class_name="bg-white rounded-2xl shadow-sm border border-slate-200 min-h-[440px] h-[calc(100vh-140px)] overflow-hidden flex flex-col",
                ),
                class_name="w-full max-w-7xl mx-auto px-4 md:px-8 lg:px-10 py-8",
            ),
            class_name="w-full bg-[#f8fafc] min-h-screen",
            on_mount=AppState.load_my_posts,
        ),
        rx.center(
            rx.vstack(
                rx.text("Vui lòng đăng nhập để quản lý bài đăng.", class_name="text-gray-500"),
                rx.link("Đăng nhập ngay", href="/login", class_name="text-red-500 hover:underline"),
                spacing="2",
            ),
            class_name="min-h-[60vh]",
        ),
    )

