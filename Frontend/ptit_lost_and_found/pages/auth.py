import reflex as rx

from ptit_lost_and_found.state import AppState


def _auth_banner() -> rx.Component:
    return rx.el.div(
        rx.el.div(class_name="absolute top-[10%] left-[10%] w-32 h-12 bg-white/10 rounded-full blur-md animate-pulse"),
        rx.el.div(class_name="absolute top-[20%] right-[15%] w-24 h-8 bg-white/10 rounded-full blur-sm animate-pulse"),
        rx.el.div(class_name="absolute bottom-[30%] left-[15%] w-28 h-10 bg-white/10 rounded-full blur-md animate-pulse"),
        rx.el.div(
            rx.el.span(
                "Cong dong sinh vien PTIT",
                class_name="inline-flex items-center rounded-full bg-white/20 px-3 py-1 text-xs font-semibold tracking-wide mb-4",
            ),
            rx.el.h1(
                "Tìm đồ thất lạc PTIT",
                rx.el.br(),
                "Ket noi sinh vien va tim lai do that lac trong hoc vien",
                class_name="text-4xl font-bold leading-tight mb-4",
            ),
            rx.el.p(
                "Nen tang chi phuc vu cong dong sinh vien Hoc vien Cong nghe Buu chinh Vien thong.",
                class_name="text-sm md:text-base text-white/90 max-w-md",
            ),
            class_name="relative z-10 text-white max-w-lg",
        ),
        class_name="relative hidden w-1/2 flex-col items-center justify-center bg-gradient-to-br from-[#ff6a3d] via-[#ff4500] to-[#c43300] p-12 lg:flex overflow-hidden",
    )


def login_page() -> rx.Component:
    return rx.el.div(
        _auth_banner(),
        rx.el.div(
            rx.el.div(
                rx.el.h2("Đăng nhập", class_name="text-2xl font-bold text-slate-800 mb-2"),
                rx.el.p(
                    "Su dung tai khoan sinh vien PTIT de tiep tuc.",
                    class_name="text-sm text-slate-500 mb-6",
                ),
                rx.cond(
                    AppState.error_message != "",
                    rx.el.div(
                        AppState.error_message,
                        class_name="mb-4 rounded-lg bg-red-50 p-3 text-sm text-red-500 border border-red-100",
                    ),
                ),
                rx.cond(
                    AppState.success_message != "",
                    rx.el.div(
                        AppState.success_message,
                        class_name="mb-4 rounded-lg bg-emerald-50 p-3 text-sm text-emerald-600 border border-emerald-100",
                    ),
                ),
                rx.form(
                    rx.vstack(
                        rx.vstack(
                            rx.el.label("Email", class_name="text-sm font-semibold text-gray-600 mb-1 block"),
                            rx.input(
                                placeholder="Nhập email tại đây",
                                name="email",
                                type="email",
                                auto_complete=True,
                                value=AppState.login_email,
                                on_change=AppState.set_login_email,
                                class_name="w-full h-12 rounded-xl border border-gray-200 bg-white px-4 text-base leading-6 text-gray-800 placeholder:text-gray-400 placeholder:leading-6 outline-none focus:border-[#319795] focus:ring-2 focus:ring-[#319795]/20",
                            ),
                            spacing="2",
                            width="100%",
                        ),
                        rx.vstack(
                            rx.el.label("Mật khẩu", class_name="text-sm font-semibold text-gray-600 mb-1 block"),
                            rx.input(
                                placeholder="Nhập mật khẩu tại đây",
                                name="password",
                                type="password",
                                auto_complete=True,
                                value=AppState.login_password,
                                on_change=AppState.set_login_password,
                                class_name="w-full h-12 rounded-xl border border-gray-200 bg-white px-4 text-base leading-6 text-gray-800 placeholder:text-gray-400 placeholder:leading-6 outline-none focus:border-[#319795] focus:ring-2 focus:ring-[#319795]/20",
                            ),
                            spacing="2",
                            width="100%",
                        ),
                        rx.button(
                            rx.cond(AppState.loading, "ĐANG XỬ LÝ...", "ĐĂNG NHẬP"),
                            type="submit",
                            disabled=AppState.loading,
                            class_name="w-full rounded-xl py-3.5 font-bold text-white bg-[#319795] hover:bg-[#2c7a7b] transition-all",
                        ),
                        spacing="4",
                        width="100%",
                    ),
                    on_submit=AppState.submit_login,
                ),
                rx.text(
                    "Bạn chưa có tài khoản? ",
                    rx.link("Đăng ký ngay", href="/register", class_name="text-[#ff4500] hover:underline font-semibold"),
                    class_name="mt-8 text-center text-sm font-medium text-gray-500",
                ),
                class_name="w-full max-w-sm",
            ),
            class_name="flex w-full flex-col items-center justify-center bg-white px-8 md:px-16 lg:w-1/2",
        ),
        class_name="flex min-h-screen w-full font-sans bg-white",
        on_mount=AppState.clear_messages,
    )


def register_page() -> rx.Component:
    return rx.el.div(
        _auth_banner(),
        rx.el.div(
            rx.el.div(
                rx.el.h2("Đăng ký tài khoản", class_name="text-2xl font-bold text-slate-800 mb-2"),
                rx.el.p(
                    "Tao tai khoan de tham gia dien dan tim do that lac cua sinh vien PTIT.",
                    class_name="text-slate-500 text-sm mb-6 font-medium",
                ),
                rx.cond(
                    AppState.error_message != "",
                    rx.el.div(
                        AppState.error_message,
                        class_name="mb-4 rounded-lg bg-red-50 p-3 text-xs text-red-500 border border-red-100",
                    ),
                ),
                rx.cond(
                    AppState.success_message != "",
                    rx.el.div(
                        AppState.success_message,
                        class_name="mb-4 rounded-lg bg-emerald-50 p-3 text-xs text-emerald-600 border border-emerald-100",
                    ),
                ),
                rx.form(
                    rx.vstack(
                        rx.input(
                            placeholder="Họ và tên",
                            name="username",
                            value=AppState.register_username,
                            on_change=AppState.set_register_username,
                            class_name="w-full h-12 rounded-xl border border-gray-200 bg-white px-4 text-base leading-6 text-gray-800 placeholder:text-gray-400 placeholder:leading-6 outline-none focus:border-[#319795] focus:ring-2 focus:ring-[#319795]/20",
                        ),
                        rx.input(
                            placeholder="Email",
                            name="email",
                            type="email",
                            auto_complete=True,
                            value=AppState.register_email,
                            on_change=AppState.set_register_email,
                            class_name="w-full h-12 rounded-xl border border-gray-200 bg-white px-4 text-base leading-6 text-gray-800 placeholder:text-gray-400 placeholder:leading-6 outline-none focus:border-[#319795] focus:ring-2 focus:ring-[#319795]/20",
                        ),
                        rx.input(
                            placeholder="Mật khẩu",
                            name="password",
                            type="password",
                            auto_complete=True,
                            value=AppState.register_password,
                            on_change=AppState.set_register_password,
                            class_name="w-full h-12 rounded-xl border border-gray-200 bg-white px-4 text-base leading-6 text-gray-800 placeholder:text-gray-400 placeholder:leading-6 outline-none focus:border-[#319795] focus:ring-2 focus:ring-[#319795]/20",
                        ),
                        rx.input(
                            placeholder="Xác nhận mật khẩu",
                            name="confirm_password",
                            type="password",
                            auto_complete=True,
                            value=AppState.register_confirm_password,
                            on_change=AppState.set_register_confirm_password,
                            class_name="w-full h-12 rounded-xl border border-gray-200 bg-white px-4 text-base leading-6 text-gray-800 placeholder:text-gray-400 placeholder:leading-6 outline-none focus:border-[#319795] focus:ring-2 focus:ring-[#319795]/20",
                        ),
                        rx.button(
                            rx.cond(AppState.loading, "ĐANG TẠO TÀI KHOẢN...", "ĐĂNG KÝ NGAY"),
                            type="submit",
                            disabled=AppState.loading,
                            class_name="w-full rounded-xl py-3.5 font-bold text-white bg-[#319795] hover:bg-[#2c7a7b] transition-all",
                        ),
                        spacing="3",
                        width="100%",
                    ),
                    on_submit=AppState.submit_register,
                ),
                rx.text(
                    "Đã có tài khoản? ",
                    rx.link("Đăng nhập ngay", href="/login", class_name="text-[#ff4500] hover:underline font-semibold"),
                    class_name="mt-8 text-center text-sm font-medium text-gray-500",
                ),
                class_name="w-full max-w-sm",
            ),
            class_name="flex w-full flex-col items-center justify-center bg-white px-8 md:px-16 lg:w-1/2 py-10 overflow-y-auto",
        ),
        class_name="flex min-h-screen w-full font-sans bg-white",
        on_mount=AppState.clear_messages,
    )

