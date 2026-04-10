import reflex as rx


def simple_page(title: str) -> rx.Component:
    return rx.center(
        rx.vstack(
            rx.heading(title, size="7"),
            rx.text("Đã có route. Sẽ migrate đầy đủ UI/logic ở bước tiếp theo."),
            spacing="3",
            align="center",
        ),
        min_height="70vh",
    )
