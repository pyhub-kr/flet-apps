import flet as ft


def main(page: ft.Page) -> None:
    page.add(ft.Text("hello flet #2"))


ft.app(target=main)

