import reflex as rx

from ptit_lost_and_found.state import AppState


CATEGORIES = [
    "The sinh vien",
    "Can cuoc cong dan",
    "Bang lai xe",
    "The ATM/Ngan hang",
    "Vi/Bop",
    "Dien thoai/Laptop",
    "Chia khoa",
    "Balo/Tui xach",
    "Giay to khac",
    "Khac",
]

LOCATIONS = [
    "Toa A1",
    "Toa A2",
    "Toa A3",
    "Sanh A1",
    "Sanh A2",
    "Can tin",
    "Bai gui xe",
    "Khac",
]


def post_create_page() -> rx.Component:
    return rx.el.div(
        rx.el.div(
            rx.el.div(
                rx.el.div(
                    rx.heading("Tao bai dang moi", size="7", class_name="text-slate-800 tracking-tight"),
                    rx.text(
                        "Dien thong tin can thiet de dang bai mat/nhat do nhanh gon.",
                        class_name="text-sm text-slate-500 mt-1",
                    ),
                    class_name="sticky top-0 z-10 bg-white px-5 md:px-6 pt-5 md:pt-6 pb-4 border-b border-slate-200",
                ),
                rx.el.div(
                    rx.cond(
                        AppState.is_logged_in,
                        rx.vstack(
                            rx.vstack(
                                rx.el.div(
                                    rx.el.label("Loai tin", class_name="text-sm font-semibold text-slate-700 block mb-2"),
                                    rx.hstack(
                                        rx.button(
                                            "Mat do",
                                            type="button",
                                            on_click=AppState.set_create_post_type("LOST"),
                                            class_name=rx.cond(
                                                AppState.create_post_type == "LOST",
                                                "px-4 py-2 rounded-full bg-[#ff4500] text-white font-semibold text-sm",
                                                "px-4 py-2 rounded-full bg-slate-100 text-slate-700 font-semibold text-sm hover:bg-slate-200",
                                            ),
                                        ),
                                        rx.button(
                                            "Nhat duoc",
                                            type="button",
                                            on_click=AppState.set_create_post_type("FOUND"),
                                            class_name=rx.cond(
                                                AppState.create_post_type == "FOUND",
                                                "px-4 py-2 rounded-full bg-[#ff4500] text-white font-semibold text-sm",
                                                "px-4 py-2 rounded-full bg-slate-100 text-slate-700 font-semibold text-sm hover:bg-slate-200",
                                            ),
                                        ),
                                        spacing="1",
                                        class_name="bg-slate-100 p-1 rounded-full inline-flex",
                                    ),
                                ),
                                rx.el.div(
                                    rx.el.label("Tieu de", class_name="text-sm font-semibold text-slate-700 block mb-2"),
                                    rx.input(
                                        placeholder="Vi du: Mat vi mau den tai Toa A1",
                                        value=AppState.create_post_title,
                                        on_change=AppState.set_create_post_title,
                                        class_name="w-full h-12 bg-slate-50 border border-slate-200 rounded-xl px-4 py-0 text-[17px] leading-6 text-slate-800 outline-none",
                                    ),
                                    rx.text("Tieu de se duoc luu truc tiep vao backend va DB.", class_name="text-xs text-slate-500 mt-1"),
                                    class_name="w-full max-w-[760px]",
                                ),
                                rx.vstack(
                                    rx.el.label("Anh minh hoa", class_name="text-sm font-semibold text-slate-700 block"),
                                    rx.text("Anh toi da 5MB (png/jpg/jpeg/webp).", class_name="text-xs text-slate-500"),
                                    rx.upload(
                                        rx.el.div(
                                            rx.cond(
                                                AppState.create_post_image_preview != "",
                                                rx.image(
                                                    src=AppState.create_post_image_preview,
                                                    class_name="w-full h-full object-contain",
                                                ),
                                                rx.vstack(
                                                    rx.hstack(
                                                        rx.icon("upload", size=16),
                                                        rx.text("Tai anh len"),
                                                        spacing="2",
                                                        align="center",
                                                    ),
                                                    rx.text(
                                                        "Nhan de chon anh hoac keo tha vao day",
                                                        class_name="text-xs text-slate-500",
                                                    ),
                                                    spacing="2",
                                                    align="center",
                                                ),
                                            ),
                                            class_name="w-full h-56 rounded-xl border border-dashed border-slate-300 bg-slate-50 hover:bg-slate-100 transition flex items-center justify-center overflow-hidden",
                                        ),
                                        id="post_upload",
                                        max_files=1,
                                        accept={"image/*": [".png", ".jpg", ".jpeg", ".webp"]},
                                        on_drop=AppState.set_create_post_image_preview,
                                    ),
                                    spacing="2",
                                    width="100%",
                                ),
                                rx.vstack(
                                    rx.el.label("Mo ta", class_name="text-sm font-semibold text-slate-700 block mb-1"),
                                    rx.text_area(
                                        placeholder="Mô tả chi tiết món đồ...",
                                        value=AppState.create_post_description,
                                        on_change=AppState.set_create_post_description,
                                        class_name="w-full bg-slate-50 border border-slate-200 rounded-xl px-4 py-3 text-sm min-h-[110px] outline-none",
                                    ),
                                    rx.el.label("Danh muc", class_name="text-sm font-semibold text-slate-700 block mb-1"),
                                    rx.select(
                                        CATEGORIES,
                                        value=AppState.create_post_category,
                                        on_change=AppState.set_create_post_category,
                                        placeholder="Chọn loại đồ",
                                        width="100%",
                                        class_name="h-11",
                                    ),
                                    rx.cond(
                                        AppState.create_post_category == "Khac",
                                        rx.input(
                                            placeholder="Nhập tên đồ vật...",
                                            value=AppState.create_post_custom_category,
                                            on_change=AppState.set_create_post_custom_category,
                                            class_name="w-full h-12 bg-slate-50 border border-slate-200 rounded-xl px-4 py-0 text-[17px] leading-6 text-slate-800 outline-none",
                                        ),
                                    ),
                                    rx.el.label("Khu vuc", class_name="text-sm font-semibold text-slate-700 block mb-1"),
                                    rx.select(
                                        LOCATIONS,
                                        value=AppState.create_post_location,
                                        on_change=AppState.set_create_post_location,
                                        placeholder="Chọn khu vực",
                                        width="100%",
                                        class_name="h-11",
                                    ),
                                    rx.cond(
                                        AppState.create_post_location == "Khac",
                                        rx.input(
                                            placeholder="Nhập khu vực cụ thể...",
                                            value=AppState.create_post_custom_location,
                                            on_change=AppState.set_create_post_custom_location,
                                            class_name="w-full h-12 bg-slate-50 border border-slate-200 rounded-xl px-4 py-0 text-[17px] leading-6 text-slate-800 outline-none",
                                        ),
                                    ),
                                    rx.el.label("Thong tin lien he", class_name="text-sm font-semibold text-slate-700 block mb-1"),
                                    rx.text_area(
                                        placeholder="Thong tin lien he (SDT/Facebook/Zalo...)",
                                        value=AppState.create_post_contact,
                                        on_change=AppState.set_create_post_contact,
                                        class_name="w-full bg-slate-50 border border-slate-200 rounded-xl px-4 py-3 text-sm min-h-[96px] outline-none",
                                    ),
                                    rx.text("Thong tin lien he de nguoi dung de nhan/tra.", class_name="text-xs text-slate-500"),
                                    spacing="3",
                                    width="100%",
                                ),
                                rx.cond(
                                    AppState.error_message != "",
                                    rx.el.div(
                                        AppState.error_message,
                                        class_name="rounded-lg bg-red-50 p-3 text-sm text-red-500 border border-red-100 w-full",
                                    ),
                                ),
                                rx.cond(
                                    AppState.success_message != "",
                                    rx.el.div(
                                        AppState.success_message,
                                        class_name="rounded-lg bg-emerald-50 p-3 text-sm text-emerald-600 border border-emerald-100 w-full",
                                    ),
                                ),
                                rx.hstack(
                                    rx.button(
                                        "Lam moi",
                                        type="button",
                                        on_click=AppState.reset_create_post_form,
                                        class_name="bg-white hover:bg-slate-50 text-slate-700 font-semibold py-3 px-5 rounded-xl border border-slate-200 transition-all",
                                    ),
                                    rx.button(
                                        rx.cond(AppState.loading, "Đang xử lý...", "Đăng tin ngay"),
                                        type="button",
                                        on_click=AppState.submit_create_post_with_file(
                                            rx.upload_files(upload_id="post_upload")
                                        ),
                                        disabled=AppState.loading,
                                        class_name="flex-1 bg-[#ff4500] hover:bg-[#e03d00] disabled:bg-slate-300 text-white font-semibold py-3 rounded-xl transition-all",
                                    ),
                                    spacing="3",
                                    width="100%",
                                    align="center",
                                ),
                                rx.text("Tin co the duoc kiem duyet truoc khi hien thi cong khai.", class_name="text-xs text-slate-500 text-center"),
                                spacing="5",
                                width="100%",
                            ),
                            class_name="bg-white p-5 md:p-6 rounded-2xl border border-slate-200 shadow-sm",
                        ),
                        rx.center(
                            rx.vstack(
                                rx.text("Bạn cần đăng nhập để đăng tin.", class_name="text-gray-600"),
                                rx.link("Đăng nhập ngay", href="/login", class_name="text-red-500 hover:underline"),
                                spacing="2",
                            ),
                            class_name="py-10 text-center bg-slate-50 rounded-xl border border-dashed border-slate-200",
                        ),
                    ),
                    class_name="px-5 md:px-6 pb-5 md:pb-6 overflow-y-auto max-h-[calc(100vh-220px)]",
                ),
                class_name="bg-white rounded-2xl shadow-sm border border-slate-200 overflow-hidden",
            ),
            class_name="max-w-7xl px-4 md:px-8 lg:px-10 mx-auto py-8",
        ),
        class_name="w-full bg-[#f8fafc] min-h-screen",
    )

