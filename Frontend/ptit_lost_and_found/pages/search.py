import reflex as rx

from ptit_lost_and_found.state import AppState


def _search_card(post: dict) -> rx.Component:
    post_id = post["id"].to_string()
    has_image = (post.get("image") != None) & (post.get("image") != "")
    post_type_label = rx.cond(post["type"] == "LOST", "Mất đồ", "Nhặt được")
    return rx.link(
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
                    rx.el.span(post_type_label, class_name="bg-orange-50 text-[#ff4500] text-[10px] font-bold px-2 py-1 rounded-full"),
                    rx.el.span(post["category"], class_name="bg-purple-50 text-purple-600 text-[10px] font-bold px-2 py-1 rounded-full"),
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
                    rx.text(post["title"], class_name="text-sm font-bold text-slate-900 truncate"),
                    spacing="2",
                    align="center",
                    width="100%",
                    class_name="mb-1.5",
                ),
                rx.hstack(
                    rx.text("Mô tả:", class_name="text-sm font-semibold text-slate-500 min-w-[74px]"),
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
                class_name="flex-1",
            ),
            class_name="w-full group flex flex-col md:flex-row gap-5 p-4 border border-slate-200 rounded-2xl hover:border-slate-300 hover:shadow-sm transition-all cursor-pointer bg-white",
        ),
        href="/post/" + post_id,
        class_name="block w-full",
    )


def search_page() -> rx.Component:
    return rx.el.div(
        rx.el.div(
            rx.el.div(
                rx.el.div(
                    rx.vstack(
                        rx.vstack(
                            rx.text("Tìm nhanh", class_name="text-xs font-semibold uppercase tracking-wide text-[#ff4500]"),
                            rx.form(
                                rx.hstack(
                                    rx.input(
                                        value=AppState.search_query,
                                        on_change=AppState.set_search_query,
                                        placeholder="Nhập từ khóa (ví dụ: thẻ SV, điện thoại, tòa A2...)",
                                        class_name="min-w-[280px] flex-1",
                                    ),
                                    rx.button(
                                        "Tìm nhanh",
                                        type="submit",
                                        class_name="bg-[#ff4500] hover:bg-[#e03d00] text-white font-semibold px-4",
                                    ),
                                    spacing="2",
                                    width="100%",
                                    align="center",
                                ),
                                on_submit=AppState.run_quick_search,
                                class_name="w-full md:max-w-[520px]",
                            ),
                            spacing="2",
                            align="start",
                            width="100%",
                        ),
                        rx.vstack(
                            rx.text("Tìm lọc", class_name="text-xs font-semibold uppercase tracking-wide text-[#ff4500]"),
                            rx.hstack(
                                rx.select(
                                    ["Tất cả loại tin", "Mất đồ", "Nhặt được"],
                                    value=AppState.selected_type,
                                    on_change=AppState.set_selected_type_and_reset,
                                    class_name="min-w-[180px]",
                                ),
                                rx.select(
                                    AppState.available_categories,
                                    value=AppState.selected_category,
                                    on_change=AppState.set_selected_category_and_reset,
                                    class_name="min-w-[200px]",
                                ),
                                rx.select(
                                    AppState.available_locations,
                                    value=AppState.selected_location,
                                    on_change=AppState.set_selected_location_and_reset,
                                    class_name="min-w-[200px]",
                                ),
                                spacing="3",
                                wrap="wrap",
                                width="100%",
                            ),
                            spacing="2",
                            align="start",
                            width="100%",
                        ),
                        spacing="4",
                        width="100%",
                        align="start",
                    ),
                    class_name="sticky top-0 z-10 bg-white px-4 py-3 border-b border-slate-200",
                ),
                rx.el.div(
                    rx.cond(
                        AppState.posts_loading,
                        rx.center(
                            rx.el.div(class_name="animate-spin rounded-full h-8 w-8 border-b-2 border-red-500"),
                            class_name="py-8",
                        ),
                        rx.cond(
                            AppState.paginated_posts.length() == 0,
                            rx.el.div("Không có kết quả phù hợp.", class_name="text-center py-10 text-slate-400"),
                            rx.vstack(rx.foreach(AppState.paginated_posts, _search_card), width="100%", spacing="4", align="stretch"),
                        ),
                    ),
                    class_name="px-4 py-4 overflow-y-auto max-h-[calc(100vh-190px)]",
                ),
                class_name="w-full border border-slate-200 rounded-2xl bg-white shadow-sm overflow-hidden",
            ),
            class_name="w-full max-w-7xl mx-auto px-4 md:px-8 lg:px-10 py-8",
        ),
        class_name="w-full bg-[#f8fafc] min-h-screen flex flex-col items-stretch",
        on_mount=[AppState.load_posts, AppState.reset_search_and_fetch],
    )

