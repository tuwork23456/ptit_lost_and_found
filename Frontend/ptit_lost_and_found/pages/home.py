import reflex as rx
from ptit_lost_and_found.components.latest_news import latest_news
from ptit_lost_and_found.state import AppState


def home_page() -> rx.Component:
    return rx.el.div(
        rx.el.div(
            rx.el.section(
                latest_news(),
                class_name="w-full py-2 md:py-4 min-h-screen",
            ),
            class_name="w-full max-w-7xl mx-auto px-4 md:px-8 lg:px-10",
        ),
        class_name="w-full bg-[#f8fafc] min-h-screen",
    )


def home_page_with_load() -> rx.Component:
    return rx.el.div(
        home_page(),
        on_mount=[AppState.load_posts, AppState.load_saved_post_ids],
    )

