import reflex as rx


def footer() -> rx.Component:
    return rx.el.footer(
        rx.el.div(
            rx.el.div(rx.el.h3("PTIT Lost & Found", class_name="text-base font-bold text-slate-800"), rx.el.p("Cong dong tim do that lac cho sinh vien.", class_name="text-sm text-slate-500"), class_name="space-y-2"),
            rx.el.div(
                rx.el.h3("Ho tro", class_name="text-sm font-semibold text-slate-700 uppercase tracking-wide"),
                rx.el.div(
                    rx.el.p("Huong dan dang tin", class_name="text-sm text-slate-500"),
                    rx.el.p("Cau hoi thuong gap", class_name="text-sm text-slate-500"),
                    rx.el.p("Bao cao vi pham", class_name="text-sm text-slate-500"),
                    class_name="space-y-1.5",
                ),
                class_name="space-y-2",
            ),
            rx.el.div(
                rx.el.h3("Lien he", class_name="text-sm font-semibold text-slate-700 uppercase tracking-wide"),
                rx.el.div(
                    rx.el.p("support@sinhvien.edu.vn", class_name="text-sm text-slate-500"),
                    rx.el.p("PTIT Campus", class_name="text-sm text-slate-500"),
                    class_name="space-y-1.5",
                ),
                class_name="space-y-2",
            ),
            class_name="max-w-7xl mx-auto px-4 md:px-6 lg:px-8 py-10 grid grid-cols-1 md:grid-cols-3 gap-8",
        ),
        rx.el.div(
            rx.el.p(
                "© 2026 Tim Do Sinh Vien. Bao luu moi quyen.",
                class_name="text-center text-xs text-slate-500 font-medium",
            ),
            class_name="w-full border-t border-slate-200 py-3",
        ),
        class_name="w-full bg-white mt-8",
    )

