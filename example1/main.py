import flet as ft


def main(page: ft.Page) -> None:
    page.add(
        ft.Container(
            content=ft.Text("hello flet #5", size=48),
            alignment=ft.alignment.center,
            expand=True
        )
    )


ft.app(target=main)
