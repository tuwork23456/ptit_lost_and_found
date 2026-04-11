import reflex as rx

from ptit_lost_and_found.state import AppState


def left_sidebar() -> rx.Component:
    current_path = AppState.router.page.path
    base_cls = "flex items-center gap-2 px-3 py-2 rounded-lg text-sm transition"
    active_cls = "bg-orange-50 text-[#ff4500] font-semibold"
    inactive_cls = "text-slate-700 hover:bg-slate-100"

    def _item(icon: str, label: str, href: str) -> rx.Component:
        return rx.link(
            rx.icon(icon, size=16),
            rx.text(label),
            href=href,
            class_name=base_cls + " " + rx.cond(current_path == href, active_cls, inactive_cls),
        )

    return rx.el.aside(
        rx.el.div(
            rx.text("Khám phá", class_name="text-[11px] font-semibold uppercase tracking-wide text-slate-400 px-3 pb-1"),
            _item("house", "Trang chủ", "/"),
            _item("search", "Tìm kiếm", "/search"),
            _item("square-pen", "Đăng tin", "/post"),
            rx.el.div(class_name="h-px bg-slate-100 my-2"),
            rx.text("Cá nhân", class_name="text-[11px] font-semibold uppercase tracking-wide text-slate-400 px-3 pb-1"),
            _item("folder-kanban", "Quản lý bài đăng", "/manage-post"),
            _item("bookmark", "Bài đã lưu", "/saved-posts"),
            rx.cond(
                AppState.is_admin,
                rx.fragment(
                    rx.el.div(class_name="h-px bg-slate-100 my-2"),
                    rx.text(
                        "Quản trị",
                        class_name="text-[11px] font-semibold uppercase tracking-wide text-slate-400 px-3 pb-1",
                    ),
                    _item("shield-check", "Duyệt bài", "/admin"),
                ),
            ),
            class_name="bg-white rounded-xl border border-slate-200 p-3 shadow-sm",
        ),
        class_name="hidden lg:block lg:w-[220px] lg:flex-shrink-0 lg:self-start lg:sticky lg:top-24 lg:max-h-[calc(100vh-7rem)] lg:overflow-y-auto",
    )


def right_panel() -> rx.Component:
    return rx.el.aside(
        rx.vstack(
            rx.el.div(
                rx.text("Cẩm nang sử dụng", class_name="text-sm font-bold uppercase tracking-wide text-[#ff4500] px-1 pb-2"),
                rx.el.ul(
                    rx.el.li("Trang chủ: Cập nhật tin mới nhất mỗi giây."),
                    rx.el.li("Tìm kiếm: Lọc thông minh theo tòa nhà và loại đồ."),
                    rx.el.li("Đăng tin: Mô tả kỹ để tăng 80% cơ hội tìm thấy."),
                    rx.el.li("Nhắn tin: Kết nối trực tiếp, trao đổi an toàn."),
                    class_name="text-sm text-slate-700 list-disc pl-5 space-y-2 leading-6",
                ),
                class_name="bg-white rounded-xl border border-slate-200 p-3 shadow-sm",
            ),
            rx.el.div(
                rx.text("Bí kíp tránh lừa đảo", class_name="text-sm font-bold uppercase tracking-wide text-[#ff4500] px-1 pb-2"),
                rx.el.ul(
                    rx.el.li(
                        "Xác minh chính chủ: Yêu cầu người nhặt được mô tả đặc điểm bí mật của đồ vật (ví dụ: vết xước, hình nền điện thoại)."
                    ),
                    rx.el.li(
                        "Giao dịch trực tiếp: Ưu tiên hẹn gặp tại sảnh các tòa A2, A3 hoặc phòng Bảo vệ. Tuyệt đối không chuyển khoản trước (phí ship, tiền hậu tạ)."
                    ),
                    rx.el.li(
                        "Bảo mật thông tin: Không nên chụp rõ toàn bộ số CCCD hoặc mặt trước thẻ ATM lên bài đăng công khai."
                    ),
                    class_name="text-sm text-slate-700 list-disc pl-5 space-y-2 leading-6",
                ),
                class_name="bg-white rounded-xl border border-slate-200 p-3 shadow-sm",
            ),
            spacing="3",
            class_name="sticky top-[72px] z-20",
        ),
        class_name="hidden lg:block lg:w-[220px] lg:flex-shrink-0 lg:self-start",
    )
