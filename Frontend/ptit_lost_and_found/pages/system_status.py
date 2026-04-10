import reflex as rx

from ptit_lost_and_found.state import AppState


def system_status_page() -> rx.Component:
    status_badge = rx.cond(
        AppState.health_status == "ok",
        rx.el.span("OK", class_name="px-3 py-1 rounded-full text-xs font-bold bg-emerald-100 text-emerald-700"),
        rx.cond(
            AppState.health_status == "error",
            rx.el.span("ERROR", class_name="px-3 py-1 rounded-full text-xs font-bold bg-red-100 text-red-700"),
            rx.cond(
                AppState.health_status == "checking",
                rx.el.span("CHECKING", class_name="px-3 py-1 rounded-full text-xs font-bold bg-amber-100 text-amber-700"),
                rx.el.span("UNKNOWN", class_name="px-3 py-1 rounded-full text-xs font-bold bg-gray-100 text-gray-700"),
            ),
        ),
    )
    return rx.el.div(
        rx.el.div(
            rx.hstack(
                rx.heading("Trạng thái hệ thống", size="6"),
                rx.spacer(),
                status_badge,
                width="100%",
                align="center",
            ),
            rx.text("Kiểm tra nhanh kết nối Frontend -> backend FastAPI.", class_name="text-sm text-gray-500 mt-1"),
            rx.hstack(
                rx.button(
                    "Kiểm tra kết nối",
                    on_click=AppState.run_health_check,
                    class_name="bg-[#dc2626] hover:bg-[#b91c1c] text-white text-sm font-bold px-5 py-2.5 rounded-xl",
                ),
                rx.link(
                    "Mở API Docs",
                    href="http://127.0.0.1:8000/docs",
                    is_external=True,
                    class_name="text-sm text-red-500 hover:underline",
                ),
                spacing="4",
                class_name="mt-5",
            ),
            rx.cond(
                AppState.health_message != "",
                rx.el.div(
                    AppState.health_message,
                    class_name="mt-5 rounded-xl border border-gray-100 bg-gray-50 px-4 py-3 text-sm text-gray-700",
                ),
            ),
            class_name="bg-white rounded-3xl shadow-sm border border-gray-100 p-6 md:p-8",
        ),
        class_name="w-full bg-[#f0f2f5] min-h-screen xl:px-[250px] px-4 md:px-10 py-8",
    )

