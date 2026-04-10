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
            rx.text("Kham pha", class_name="text-[11px] font-semibold uppercase tracking-wide text-slate-400 px-3 pb-1"),
            _item("house", "Trang chu", "/"),
            _item("search", "Tim kiem", "/search"),
            _item("square-pen", "Dang tin", "/post"),
            rx.el.div(class_name="h-px bg-slate-100 my-2"),
            rx.text("Ca nhan", class_name="text-[11px] font-semibold uppercase tracking-wide text-slate-400 px-3 pb-1"),
            _item("folder-kanban", "Quan ly bai dang", "/manage-post"),
            _item("bookmark", "Bai da luu", "/saved-posts"),
            rx.cond(
                AppState.is_admin,
                rx.fragment(
                    rx.el.div(class_name="h-px bg-slate-100 my-2"),
                    rx.text(
                        "Quan tri",
                        class_name="text-[11px] font-semibold uppercase tracking-wide text-slate-400 px-3 pb-1",
                    ),
                    _item("shield-check", "Duyet bai", "/admin"),
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
                rx.text("Cam nang su dung", class_name="text-sm font-bold uppercase tracking-wide text-[#ff4500] px-1 pb-2"),
                rx.el.ul(
                    rx.el.li("Trang chu: Cap nhat tin moi nhat moi giay."),
                    rx.el.li("Tim kiem: Loc thong minh theo Toa nha va Loai do."),
                    rx.el.li("Dang tin: Mo ta ky de tang 80% co hoi tim thay."),
                    rx.el.li("Nhan tin: Ket noi truc tiep, trao doi an toan."),
                    class_name="text-sm text-slate-700 list-disc pl-5 space-y-2 leading-6",
                ),
                class_name="bg-white rounded-xl border border-slate-200 p-3 shadow-sm",
            ),
            rx.el.div(
                rx.text("Bi kip tranh lua dao", class_name="text-sm font-bold uppercase tracking-wide text-[#ff4500] px-1 pb-2"),
                rx.el.ul(
                    rx.el.li("Xac minh chinh chu: Yeu cau nguoi nhat duoc mo ta dac diem bi mat cua do vat (vi du: vet xuoc, hinh nen dien thoai)."),
                    rx.el.li("Giao dich truc tiep: Uu tien hen gap tai sanh cac toa A2, A3 hoac phong Bao ve. Tuyet doi khong chuyen khoan truoc (phi ship, tien hau ta)."),
                    rx.el.li("Bao mat thong tin: Khong nen chup ro toan bo so CCCD hoac mat truoc the ATM len bai dang cong khai."),
                    class_name="text-sm text-slate-700 list-disc pl-5 space-y-2 leading-6",
                ),
                class_name="bg-white rounded-xl border border-slate-200 p-3 shadow-sm",
            ),
            spacing="3",
            class_name="sticky top-[72px] z-20",
        ),
        class_name="hidden lg:block lg:w-[220px] lg:flex-shrink-0 lg:self-start",
    )

