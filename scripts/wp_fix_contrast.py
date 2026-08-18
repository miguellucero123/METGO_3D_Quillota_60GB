"""Re-publish home + planes + innovaciones + contacto (contrast fix)."""
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))
from wp_apply_venta import (  # noqa: E402
    contacto_content,
    home_content,
    innovaciones_content,
    planes_content,
    upsert_page,
)
from wp_rest import request  # noqa: E402


def main() -> None:
    request(
        "POST",
        "/wp/v2/pages/211",
        {"title": "Inicio", "content": home_content(), "status": "publish"},
    )
    print("home ok")
    upsert_page("planes", "Planes", planes_content(), 40)
    upsert_page("innovaciones", "Innovaciones", innovaciones_content(), 30)
    upsert_page("contacto", "Contacto", contacto_content(), 50)
    print("DONE contrast fix")


if __name__ == "__main__":
    main()
