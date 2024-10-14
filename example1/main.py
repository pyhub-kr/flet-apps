import asyncio
from dataclasses import field, dataclass
from datetime import date

import httpx
import repath
from abc import abstractmethod, ABC
from typing import Optional, List, Type

import flet as ft


@dataclass
class Song:
    곡일련번호: int
    순위: str
    album_uid: int
    album_name: str
    곡명: str
    artist_uid: int
    artist_name: str
    커버이미지_주소: str
    가사: str
    발매일: date
    좋아요: int
    장르: List[str] = field(default_factory=list)

    def __post_init__(self):
        # 발매일을 문자열에서 date 객체로 변환
        if isinstance(self.발매일, str):
            self.발매일 = date.fromisoformat(self.발매일)


class BaseView(ft.View, ABC):
    route: Optional[str] = None

    @abstractmethod
    def build(self) -> None:
        pass

    @classmethod
    def test_route(cls, next_route: str) -> Optional[dict]:
        if cls.route is None:
            return None

        matched = repath.match(cls.route, next_route)
        if matched is None:
            return None

        return matched.groupdict()

    def navigate(self, view_cls: Type["BaseView"], **params) -> None:
        if view_cls.route is None:
            raise ValueError(f"route is not defined for {view_cls.__name__}")

        next_route = view_cls.route

        for key, value in params.items():
            placeholder = f":{key}"
            next_route = next_route.replace(placeholder, str(value))

        self.page.go(route=next_route)

    def alert(self, message: str) -> None:
        self.page.open(ft.AlertDialog(content=ft.Text(message, size=30)))


class RootView(BaseView):
    route = "/"

    def build(self) -> None:
        self.appbar = ft.AppBar(title=ft.Text("Flet app"))
        self.controls = [
            ft.ElevatedButton(
                text="블로그로 이동", on_click=lambda __: self.navigate(BlogHome)
            ),
            ft.ElevatedButton(
                text="멜론 TOP100", on_click=lambda __: self.navigate(MelonView)
            ),
        ]


class BlogHome(BaseView):
    route = "/blog/"

    def build(self) -> None:
        self.appbar = ft.AppBar(title=ft.Text("블로그 홈"))
        self.controls = [
            ft.ElevatedButton(
                text="홈으로", on_click=lambda _: self.navigate(RootView)
            ),
            ft.ElevatedButton(
                text=f"#{100} 포스팅 보기",
                on_click=lambda __: self.navigate(BlogPostDetailView, post_id=100),
            ),
        ]


class BlogPostDetailView(BaseView):
    route = "/blog/:post_id"

    def __init__(self, post_id: int) -> None:
        self.post_id = post_id
        super().__init__()

    def build(self) -> None:
        self.appbar = ft.AppBar(title=ft.Text(f"#{self.post_id} 포스팅"))
        self.controls = [
            ft.ElevatedButton(
                text="홈으로 한 번에 점프", on_click=lambda __: self.navigate(RootView)
            ),
        ]


class MelonView(BaseView):
    route = "/melon/top100/"

    def __init__(self):
        super().__init__()
        self.ref = ft.Ref[ft.GridView]()

    def build(self) -> None:
        self.appbar = ft.AppBar(title=ft.Text("멜론 TOP100"))
        self.controls = [
            ft.Container(
                content=ft.GridView(
                    ref=self.ref,
                    runs_count=5,
                    max_extent=150,
                    child_aspect_ratio=1,
                    spacing=10,
                    run_spacing=10,
                    padding=10,
                ),
                expand=True,
            )
        ]

    def did_mount(self) -> None:
        asyncio.run(self.update_data_sync())

    async def update_data_sync(self) -> None:
        async with httpx.AsyncClient() as client:
            response = await client.get("https://pyhub.kr/melon/20241011.json")
            obj_list = response.json()
            song_list = [Song(**obj) for obj in obj_list]

        view = self.ref.current
        view.controls = [self._make_tile(song) for song in song_list]
        # view가 page에 추가된 후에는 update 메서드를 호출하여 UI 부분 갱신 수행
        if view.page:
            view.update()

    def _make_tile(self, song: Song) -> ft.Control:
        return ft.GestureDetector(
            content=ft.Container(
                content=ft.Column(
                    [
                        ft.Image(
                            src=song.커버이미지_주소,
                            width=100,
                            height=100,
                            fit=ft.ImageFit.COVER,
                        ),
                        ft.Text(
                            song.곡명,
                            style=ft.TextStyle(weight=ft.FontWeight.BOLD),
                            overflow=ft.TextOverflow.ELLIPSIS,
                        ),
                    ],
                    spacing=0,
                    alignment=ft.MainAxisAlignment.CENTER,
                ),
                width=150,
                height=150,
                padding=3,
                alignment=ft.alignment.center,
            ),
            # on_tap=lambda _: self.alert(f"{song.곡명} - {song.artist_name}"),
            on_tap=lambda _: self.page.launch_url(
                f"https://www.melon.com/song/detail.htm?songId={song.곡일련번호}"
            ),
            mouse_cursor=ft.MouseCursor.CLICK,
        )


def init_routes(page: ft.Page, view_cls_list: List[Type[BaseView]]) -> None:
    initial_route: str = RootView.route

    def on_route_change(e: ft.RouteChangeEvent) -> None:
        # print(f"Route changed to {e}")
        next_url: str = e.route

        root_view_cls = view_cls_list[0]

        if (kwargs := root_view_cls.test_route(next_url)) is not None:
            if len(page.views) > 1:
                del page.views[1:]
            else:
                page.views.append(root_view_cls(**kwargs))
        else:
            for view_cls in view_cls_list[1:]:
                if (kwargs := view_cls.test_route(next_url)) is not None:
                    page.views.append(view_cls(**kwargs))
                    break
            else:
                page.open(
                    ft.SnackBar(
                        content=ft.Text(
                            f"지정 {next_url}에 매칭되는 View가 없습니다.",
                            color=ft.colors.WHITE,
                        ),
                        bgcolor=ft.colors.RED,
                    )
                )

        page.update()

    def view_pop(e: ft.ViewPopEvent) -> None:
        page.views.pop()  # 리스트 마지막 요소를 제거.
        page.update()

    page.on_route_change = on_route_change
    page.on_view_pop = view_pop

    # 기본 root view를 제거하고, route를 통해 View 생성
    page.views.clear()
    page.go(initial_route)


def main(page: ft.Page) -> None:
    init_routes(page, view_cls_list=[RootView, BlogHome, BlogPostDetailView, MelonView])


ft.app(main)
