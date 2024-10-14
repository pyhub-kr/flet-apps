import flet as ft
from core import BaseRootView, MainPage


class WebtoonView(BaseRootView):
    path = "/webtoons/"
    nav_icon = ft.icons.HOME
    nav_label = "웹툰"
    title = "알아서 딱!"

    def make_appbar(self) -> ft.AppBar:
        return ft.AppBar(
            leading=ft.GestureDetector(
                ft.Icon(ft.icons.HOME), on_tap=lambda e: print("clicked leading")
            ),
            title=ft.Text(self.title),
            actions=[
                ft.IconButton(icon=ft.icons.SEARCH),
            ],
        )

    def make_layout(self) -> ft.Control:
        return ft.Column(
            [
                ft.Text("알아서 딱! 페이지"),
            ]
        )


class WebtoonRecommendView(BaseRootView):
    path = "/recommend/"
    nav_icon = ft.icons.ADD
    nav_label = "추천완결"
    title = "추천완결"

    def make_appbar(self) -> ft.AppBar:
        return ft.AppBar(
            title=ft.Text(self.nav_label),
            actions=[
                ft.IconButton(icon=ft.icons.SEARCH),
            ],
        )

    def make_layout(self) -> ft.Control:
        return ft.Column(
            [
                ft.Text("추천완결 페이지"),
            ]
        )


def main(page: ft.Page) -> None:
    page.adaptive = True  # 적응형 옵션 활성화
    page.padding = 0
    page.window.min_width = 480

    MainPage(
        root_view_classes=[
            WebtoonView,
            WebtoonRecommendView,
        ],
        page=page,
    )


ft.app(target=main)

# TODO: Drawer
# TODO: API 호출
# TODO: 인증 (JWT, Token, Session)
# TODO: 설정
# TODO: Push Notification
# TODO: 파이썬 코드만 업데이트할려면 ???
# TODO: splash, icon, 각종 설정
