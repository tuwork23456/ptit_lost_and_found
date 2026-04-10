import reflex as rx
from reflex.plugins import SitemapPlugin


config = rx.Config(
    app_name="ptit_lost_and_found",
    plugins=[
        rx.plugins.TailwindV4Plugin(),
    ],
    disable_plugins=[SitemapPlugin],
)
