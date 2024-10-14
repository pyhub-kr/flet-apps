import flet as ft


def main(page: ft.Page) -> None:
    page.add(ft.Text("hello flet"))


ft.app(target=main)

