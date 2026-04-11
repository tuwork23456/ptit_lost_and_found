import reflex as rx
from ptit_lost_and_found.state import AppState

def _admin_post_card(post: dict) -> rx.Component:
    pid = post.get("id", 0)
    has_image = (post.get("image") != None) & (post.get("image") != "")
    post_type = rx.cond(post.get("type") == "LOST", "Mất đồ", "Nhặt được")
    return rx.el.div(
        rx.el.div(
            rx.vstack(
                rx.el.div(
                    rx.cond(
                        has_image,
                        rx.image(src=post.get("image"), class_name="w-full h-full object-cover object-center"),
                        rx.el.div(
                            rx.icon("image-off", size=16, class_name="text-slate-300"),
                            class_name="w-full h-full flex items-center justify-center bg-slate-100",
                        ),
                    ),
                    class_name="w-full md:w-52 h-40 md:h-32 rounded-xl overflow-hidden",
                ),
                rx.hstack(
                    rx.el.span(post_type, class_name="bg-orange-50 text-[#ff4500] text-[10px] font-bold px-2 py-1 rounded-full"),
                    rx.el.span(post.get("category", "Uncategorized"), class_name="bg-purple-50 text-purple-600 text-[10px] font-bold px-2 py-1 rounded-full"),
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
                    rx.text(post.get("title", "Không có tiêu đề"), class_name="text-sm font-bold text-slate-900 truncate"),
                    spacing="2",
                    align="center",
                    width="100%",
                    class_name="mb-1.5",
                ),
                rx.hstack(
                    rx.text("Mô tả:", class_name="text-sm font-semibold text-slate-500 min-w-[74px]"),
                    rx.text(post.get("description", ""), class_name="text-sm text-slate-700 truncate"),
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
                    rx.button(
                        "DUYỆT",
                        on_click=AppState.admin_moderate_post(pid, "approve"),
                        class_name="inline-flex items-center justify-center h-10 min-w-[96px] text-xs font-semibold text-emerald-700 bg-emerald-50 px-3 py-2 rounded-lg hover:bg-emerald-100 transition-all",
                    ),
                    rx.button(
                        "TỪ CHỐI",
                        on_click=AppState.admin_moderate_post(pid, "reject"),
                        class_name="inline-flex items-center justify-center h-10 min-w-[96px] text-xs font-semibold text-red-600 bg-red-50 px-3 py-2 rounded-lg hover:bg-red-100 transition-all",
                    ),
                    spacing="2",
                    class_name="mt-3",
                ),
                class_name="flex-1",
            ),
            class_name="w-full group flex flex-col md:flex-row gap-5 p-4 border border-slate-200 rounded-2xl hover:border-slate-300 hover:shadow-sm transition-all bg-white",
        ),
        class_name="w-full",
    )


def _admin_removed_post_card(post: dict) -> rx.Component:
    has_image = (post.get("image") != None) & (post.get("image") != "")
    post_type = rx.cond(post.get("type") == "LOST", "Mất đồ", "Nhặt được")
    return rx.el.div(
        rx.el.div(
            rx.vstack(
                rx.el.div(
                    rx.cond(
                        has_image,
                        rx.image(src=post.get("image"), class_name="w-full h-full object-cover object-center"),
                        rx.el.div(
                            rx.icon("image-off", size=16, class_name="text-slate-300"),
                            class_name="w-full h-full flex items-center justify-center bg-slate-100",
                        ),
                    ),
                    class_name="w-full md:w-52 h-40 md:h-32 rounded-xl overflow-hidden",
                ),
                rx.hstack(
                    rx.el.span(post_type, class_name="bg-orange-50 text-[#ff4500] text-[10px] font-bold px-2 py-1 rounded-full"),
                    rx.el.span(post.get("category", "Uncategorized"), class_name="bg-purple-50 text-purple-600 text-[10px] font-bold px-2 py-1 rounded-full"),
                    rx.el.span("Đã xóa", class_name="bg-slate-100 text-slate-600 text-[10px] font-bold px-2 py-1 rounded-full"),
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
                    rx.text(post.get("title", "Không có tiêu đề"), class_name="text-sm font-bold text-slate-900 truncate"),
                    spacing="2",
                    align="center",
                    width="100%",
                    class_name="mb-1.5",
                ),
                rx.hstack(
                    rx.text("Mô tả:", class_name="text-sm font-semibold text-slate-500 min-w-[74px]"),
                    rx.text(post.get("description", ""), class_name="text-sm text-slate-700 truncate"),
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
                class_name="flex-1",
            ),
            class_name="w-full group flex flex-col md:flex-row gap-5 p-4 border border-slate-200 rounded-2xl bg-white",
        ),
        class_name="w-full",
    )

def _admin_report_card(report: dict) -> rx.Component:
    rid = report.get("id", 0)
    pid = report.get("post_id", 0)
    r_name = report.get("reporter_username", "Người dùng")
    has_image = (report.get("post_image") != None) & (report.get("post_image") != "")
    post_type = rx.cond(report.get("post_type") == "LOST", "Mất đồ", "Nhặt được")
    return rx.el.div(
        rx.el.div(
            rx.vstack(
                rx.el.div(
                    rx.cond(
                        has_image,
                        rx.image(src=report.get("post_image"), class_name="w-full h-full object-cover object-center"),
                        rx.el.div(
                            rx.icon("image-off", size=16, class_name="text-slate-300"),
                            class_name="w-full h-full flex items-center justify-center bg-slate-100",
                        ),
                    ),
                    class_name="w-full md:w-52 h-40 md:h-32 rounded-xl overflow-hidden",
                ),
                rx.hstack(
                    rx.el.span(post_type, class_name="bg-orange-50 text-[#ff4500] text-[10px] font-bold px-2 py-1 rounded-full"),
                    rx.el.span(report.get("post_category", "Uncategorized"), class_name="bg-purple-50 text-purple-600 text-[10px] font-bold px-2 py-1 rounded-full"),
                    rx.hstack(
                        rx.icon("circle-alert", size=12, class_name="text-red-500"),
                        rx.text("Báo cáo", class_name="text-[10px] font-bold text-red-600"),
                        spacing="1",
                        align="center",
                        class_name="bg-red-50 px-2 py-1 rounded-full",
                    ),
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
                    rx.text("Người dùng", class_name="text-sm font-bold text-[#ff4500]"),
                    spacing="2",
                    align="center",
                    width="100%",
                    class_name="mb-1.5",
                ),
                rx.hstack(
                    rx.text("Tiêu đề:", class_name="text-sm font-semibold text-slate-500 min-w-[74px]"),
                    rx.text(report.get("post_title", "Bài viết bị báo cáo"), class_name="text-sm font-bold text-slate-900 truncate"),
                    spacing="2",
                    align="center",
                    width="100%",
                    class_name="mb-1.5",
                ),
                rx.hstack(
                    rx.text("Mô tả:", class_name="text-sm font-semibold text-slate-500 min-w-[74px]"),
                    rx.text(report.get("post_description", ""), class_name="text-sm text-slate-700 truncate"),
                    spacing="2",
                    align="center",
                    width="100%",
                ),
                rx.hstack(
                    rx.text("Báo cáo từ:", class_name="text-sm font-semibold text-slate-500 min-w-[74px]"),
                    rx.text(r_name, class_name="text-sm font-semibold text-slate-700"),
                    spacing="2",
                    align="center",
                    width="100%",
                ),
                rx.hstack(
                    rx.cond(
                        (report.get("post_location") != None) & (report.get("post_location") != ""),
                        rx.hstack(
                            rx.icon("map-pin", size=12),
                            rx.text(report.get("post_location"), class_name="text-xs font-medium"),
                            spacing="2",
                            align="center",
                            class_name="px-2 py-1 rounded-md bg-slate-50 border border-slate-200/80",
                        ),
                    ),
                    rx.hstack(
                        rx.icon("calendar", size=12),
                        rx.text(report.get("post_created_date"), class_name="text-xs font-medium"),
                        spacing="2",
                        align="center",
                        class_name="px-2 py-1 rounded-md bg-slate-50 border border-slate-200/80",
                    ),
                    rx.cond(
                        (report.get("post_created_time") != None) & (report.get("post_created_time") != ""),
                        rx.hstack(
                            rx.icon("clock-3", size=12),
                            rx.text(report.get("post_created_time"), class_name="text-xs font-medium"),
                            spacing="2",
                            align="center",
                            class_name="px-2 py-1 rounded-md bg-slate-50 border border-slate-200/80",
                        ),
                    ),
                    class_name="text-slate-500 mt-2",
                    spacing="2",
                    wrap="wrap",
                    align="center",
                ),
                rx.el.div(
                    rx.text("Ly do:", class_name="text-xs font-semibold text-slate-600"),
                    rx.text(
                        rx.cond(report.get("reason") != None, report.get("reason"), ""),
                        class_name="text-xs text-slate-600 italic",
                    ),
                    class_name="mt-2 bg-red-50 border border-red-100 rounded-lg p-2.5",
                ),
                rx.hstack(
                    rx.link(
                        "Xem bài viết",
                        href=f"/post/{pid}",
                        class_name="inline-flex items-center justify-center h-10 min-w-[110px] text-xs font-semibold text-blue-600 bg-blue-50 px-3 py-2 rounded-lg hover:bg-blue-100 transition-all",
                    ),
                    rx.button(
                        "GỠ BÀI VIẾT",
                        on_click=AppState.admin_delete_post_report(pid, rid),
                        class_name="inline-flex items-center justify-center h-10 min-w-[110px] text-xs font-semibold text-red-600 bg-red-50 px-3 py-2 rounded-lg hover:bg-red-100 transition-all",
                    ),
                    spacing="2",
                    class_name="mt-3",
                ),
                class_name="flex-1",
            ),
            class_name="w-full group flex flex-col md:flex-row gap-5 p-4 border border-slate-200 rounded-2xl hover:border-slate-300 hover:shadow-sm transition-all bg-white",
        ),
        class_name="w-full",
    )

def admin_page() -> rx.Component:
    return rx.el.div(
        rx.el.div(
            rx.cond(
                AppState.is_admin,
                rx.el.div(
                    rx.el.div(
                        rx.el.div(
                            rx.hstack(
                                rx.icon("shield-check", size=24, class_name="text-[#ff4500]"),
                                rx.heading("Bảng quản trị", size="6"),
                                spacing="2",
                                align="center",
                                class_name="mb-6"
                            ),
                            # TABS
                            rx.hstack(
                                rx.button(
                                    "Duyệt bài",
                                    on_click=lambda: AppState.set_admin_tab("posts"),
                                    class_name=rx.cond(
                                        AppState.admin_tab == "posts",
                                        "bg-[#ff4500] text-white px-4 py-2 rounded-full text-sm font-bold shadow-md transition-all",
                                        "bg-white text-slate-600 border border-slate-200 px-4 py-2 rounded-full text-sm font-medium hover:bg-slate-50 transition-all"
                                    )
                                ),
                                rx.button(
                                    "Danh sách báo cáo",
                                    on_click=lambda: AppState.set_admin_tab("reports"),
                                    class_name=rx.cond(
                                        AppState.admin_tab == "reports",
                                        "bg-[#ff4500] text-white px-4 py-2 rounded-full text-sm font-bold shadow-md transition-all",
                                        "bg-white text-slate-600 border border-slate-200 px-4 py-2 rounded-full text-sm font-medium hover:bg-slate-50 transition-all"
                                    )
                                ),
                                rx.button(
                                    "Các bài đã xóa",
                                    on_click=lambda: AppState.set_admin_tab("removed"),
                                    class_name=rx.cond(
                                        AppState.admin_tab == "removed",
                                        "bg-[#ff4500] text-white px-4 py-2 rounded-full text-sm font-bold shadow-md transition-all",
                                        "bg-white text-slate-600 border border-slate-200 px-4 py-2 rounded-full text-sm font-medium hover:bg-slate-50 transition-all"
                                    )
                                ),
                                spacing="3",
                                class_name="mb-6"
                            ),
                            rx.cond(
                                AppState.admin_action_message != "",
                                rx.el.div(
                                    AppState.admin_action_message,
                                    class_name="w-full p-3 mb-4 bg-emerald-50 text-emerald-700 border border-emerald-200 rounded-xl text-sm font-medium animate-pulse"
                                )
                            ),
                            class_name="sticky top-0 z-10 bg-white px-6 pt-6 pb-4 border-b border-slate-200"
                        ),
                        rx.el.div(
                            rx.cond(
                                AppState.admin_loading,
                                rx.center(rx.spinner(color="#ff4500", size="3"), class_name="py-20 w-full"),
                                rx.cond(
                                    AppState.admin_tab == "posts",
                                    # TAB POSTS
                                    rx.vstack(
                                        rx.cond(
                                            AppState.admin_pending_posts.length() == 0,
                                            rx.center(
                                                rx.vstack(
                                                    rx.icon("check-check", size=48, class_name="text-slate-200"),
                                                    rx.text("Không có bài nào chờ duyệt.", class_name="text-slate-400 font-medium"),
                                                    align="center"
                                                ),
                                                class_name="py-20 w-full"
                                            ),
                                            rx.vstack(
                                                rx.foreach(AppState.admin_pending_posts, _admin_post_card),
                                                spacing="4",
                                                width="100%"
                                            )
                                        ),
                                        width="100%"
                                    ),
                                    rx.cond(
                                        AppState.admin_tab == "reports",
                                        # TAB REPORTS
                                        rx.vstack(
                                            rx.cond(
                                                AppState.admin_reports.length() == 0,
                                                rx.center(
                                                    rx.vstack(
                                                        rx.icon("flag", size=48, class_name="text-slate-200"),
                                                        rx.text("Không có báo cáo nào.", class_name="text-slate-400 font-medium"),
                                                        align="center"
                                                    ),
                                                    class_name="py-20 w-full"
                                                ),
                                                rx.vstack(
                                                    rx.foreach(AppState.admin_reports, _admin_report_card),
                                                    spacing="4",
                                                    width="100%"
                                                )
                                            ),
                                            width="100%"
                                        ),
                                        # TAB REMOVED
                                        rx.vstack(
                                            rx.cond(
                                                AppState.admin_removed_posts.length() == 0,
                                                rx.center(
                                                    rx.vstack(
                                                        rx.icon("archive-x", size=48, class_name="text-slate-200"),
                                                        rx.text("Chưa có bài nào trong mục đã xóa.", class_name="text-slate-400 font-medium"),
                                                        align="center"
                                                    ),
                                                    class_name="py-20 w-full"
                                                ),
                                                rx.vstack(
                                                    rx.foreach(AppState.admin_removed_posts, _admin_removed_post_card),
                                                    spacing="4",
                                                    width="100%"
                                                )
                                            ),
                                            width="100%"
                                        )
                                    )
                                )
                            ),
                            class_name="flex-1 px-6 pb-6 overflow-y-auto"
                        ),
                        width="100%",
                        align="start",
                        class_name="h-[calc(100vh-140px)] min-h-[500px] flex flex-col"
                    ),
                    class_name="bg-white rounded-2xl shadow-sm border border-slate-200 overflow-hidden"
                ),
                rx.center(
                    rx.vstack(
                        rx.icon("lock", size=48, class_name="text-slate-200"),
                        rx.text("Bạn không có quyền truy cập vào trang này.", class_name="text-slate-500 font-medium"),
                        rx.link("Về trang chủ", href="/", class_name="text-[#ff4500] hover:underline"),
                        align="center",
                        spacing="3"
                    ),
                    class_name="h-[60vh] w-full"
                ),
            ),
            class_name="w-full max-w-7xl mx-auto px-4 md:px-8 lg:px-10 py-8",
        ),
        class_name="w-full bg-[#f8fafc] min-h-screen",
        on_mount=AppState.load_admin_pending_posts
    )
