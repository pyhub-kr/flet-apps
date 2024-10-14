from abc import ABC, abstractmethod
from typing import Optional, Any, List, Type

import flet as ft


class BaseRootView(ft.Container, ABC):
    page: ft.Page
    appbar: ft.AppBar

    path: Optional[str] = None
    nav_icon: Optional[str] = None
    nav_label: Optional[str] = None

    def __init__(self, *args, page: ft.Page = None, **kwargs):
        if page is None:
            raise TypeError(
                f"{self.__class__.__name__} 인스턴스는 반드시 page 인자를 지정해주셔야 합니다."
            )
        else:
            self.page = page

        super().__init__(*args, **kwargs)
        self.appbar = self.make_appbar()

    # page 바인딩될 때마다 호출됩니다.
    def build(self) -> None:
        self.width = self.page.width
        self.content = self.make_layout()

    # noinspection PyMethodMayBeStatic
    def make_appbar(self) -> Optional[ft.AppBar]:
        return None

    @abstractmethod
    def make_layout(self) -> ft.Control:
        pass

    def redirect(
        self, route: str, skip_route_change_event: bool = False, **kwargs: Any
    ) -> None:
        self.page.go(
            route=route, skip_route_change_event=skip_route_change_event, **kwargs
        )


class MainPage:
    def __init__(
        self,
        root_view_classes: List[Type[BaseRootView]],
        page: ft.Page,
    ) -> None:
        self.page = page

        self.root_views = [cls(page=page) for cls in root_view_classes]
        assert (
            len(self.root_views) > 0
        ), "root_view_classes 속성에 반드시 1개 이상의 루트 뷰를 지정해야 합니다."

        self.page.navigation_bar = ft.NavigationBar(
            destinations=[
                ft.NavigationBarDestination(
                    icon=view.nav_icon,
                    label=view.nav_label,
                )
                for view in self.root_views
            ],
            selected_index=0,
        )

        self.page.navigation_bar.on_change = self.page__navigation_bar__on_change
        self.page.on_route_change = self.page__on_route_change
        self.page.on_view_pop = self.page__on_view_pop

        self.root_container = ft.Container(
            content=self.root_views[0],
            alignment=ft.alignment.center,
            expand=True,
        )

        page.appbar = self.root_views[0].appbar
        page.on_resized = self.page__on_resized

        page.add(self.root_container)
        page.go(self.root_views[0].path)

    def page__on_resized(self, e: ft.WindowResizeEvent) -> None:
        # page에 다시 붙으면 resize가 됩니다.
        pass

    def page__navigation_bar__on_change(self, e: ft.ControlEvent) -> None:
        self.page.go(self.root_views[e.control.selected_index].path)

    def page__on_route_change(self, e: ft.RouteChangeEvent) -> None:
        template_route = ft.TemplateRoute(e.route)

        for view_index, view in enumerate(self.root_views):
            if template_route.match(view.path):
                if len(self.page.views) >= 1:
                    del self.page.views[1:]

                self.root_container.content = view
                self.page.appbar = view.appbar
                self.page.navigation_bar.selected_index = view_index

                self.page.update()  # FIXME: 탭 전환이 느릴 수도.

                break
        else:
            # TODO: 다른 서브 페이지

            print(f"NO MATCH :", e.route)  # TODO

    def page__on_view_pop(self, e: ft.ViewPopEvent) -> None:
        self.page.views.pop()
        top_view = self.page.views[-1]
        self.page.go(top_view.route)
