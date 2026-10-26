import time

import flet as ft

# Палитра из макета
BG, CARD, PINK, CYAN, MUTED, LINE = "#0E0E11", "#1A1B1F", "#FF2D55", "#14E5FF", "#8E8E93", "#2A2B30"
CENTER = ft.alignment.center
MAIN_C = ft.MainAxisAlignment.CENTER
CROSS_C = ft.CrossAxisAlignment.CENTER
BOLD = ft.FontWeight.BOLD
GRAD = ft.LinearGradient(
    begin=ft.alignment.center_left, end=ft.alignment.center_right, colors=[CYAN, "#E946E8"]
)

VIDEOS = [
    dict(bg="feed_photo.jpg", user="@winlents", caption="Лучшие моменты — здесь! ✨",
         tags="#WinLents #тренды #видео", likes=125400, comments=2300, shares=8100,
         sound="Оригинальный звук"),
    dict(bg="feed_waves.jpg", user="@neon.vibes", caption="Неоновые волны после заката",
         tags="#неон #вайб", likes=48200, comments=914, shares=1200, sound="Neon Dreams"),
    dict(bg="feed_grad_a.jpg", user="@creator", caption="Создавай. Делись. Вдохновляй.",
         tags="#создавай #идеи", likes=9800, comments=233, shares=410, sound="Оригинальный звук"),
    dict(bg="feed_grad_b.jpg", user="@trendy", caption="Будь в тренде каждый день 🔥",
         tags="#тренды #топ", likes=77100, comments=1500, shares=3300, sound="Trend Beat"),
]
COMMENTS = [("@anna", "Огонь! 🔥"), ("@max_k", "Где это снято?"), ("@lera", "Лучшее видео за сегодня 😍")]
ONBOARDING = [
    (ft.Icons.PLAY_CIRCLE_OUTLINE, "Короткие видео", "Бесконечная лента интересного контента"),
    (ft.Icons.PERSON_ADD_ALT_OUTLINED, "Создавай", "Делись своими идеями и талантами"),
    (ft.Icons.LOCAL_FIRE_DEPARTMENT_OUTLINED, "Будь в тренде", "Следи за тем, что сейчас в топе"),
]


def fmt(n):
    return f"{n / 1000:.1f}K" if n >= 1000 else str(n)


def ico(name, size=26, opacity=1.0):
    return ft.Image(src=f"icons/{name}.png", width=size, height=size,
                    fit=ft.ImageFit.CONTAIN, opacity=opacity)


def button(text, on_click, bg=None, gradient=None, width=300):
    return ft.Container(
        content=ft.Text(text, size=16, weight=ft.FontWeight.W_600, color="white"),
        alignment=CENTER, width=width, height=50, border_radius=25,
        bgcolor=bg, gradient=gradient, on_click=on_click,
    )


def main(page: ft.Page):
    page.title = "WinLents"
    page.bgcolor = BG
    page.padding = 0
    page.spacing = 0
    page.theme_mode = ft.ThemeMode.DARK

    state = {"tab": 0, "following": False}
    body = ft.Container(expand=True)
    nav = ft.Container(bgcolor="#000000", padding=ft.padding.symmetric(vertical=6))

    def toast(text):
        page.open(ft.SnackBar(ft.Text(text), bgcolor=CARD))

    # ---------------------------------------------------------------- Лента
    def feed(start=0):
        st = {"i": start, "drag": 0, "liked": set()}
        holder = ft.Container(expand=True)

        def show(pop=False):
            holder.content = card(pop)
            holder.update()

        def step(k):
            st["i"] = (st["i"] + k) % len(VIDEOS)
            show()

        def like(e):
            st["liked"] ^= {st["i"]}
            show()

        def double_tap(e):
            st["liked"].add(st["i"])
            show(pop=True)
            time.sleep(0.6)
            show()

        def drag_update(e):
            st["drag"] += e.delta_y

        def drag_end(e):
            d, st["drag"] = st["drag"], 0
            if d < -40:
                step(1)
            elif d > 40:
                step(-1)

        def share(e):
            page.set_clipboard(f"https://winlents.app/v/{st['i']}")
            toast("Ссылка скопирована")

        def open_comments(e):
            items = ft.ListView(expand=True, spacing=10,
                                controls=[ft.Text(f"{u}  {t}") for u, t in COMMENTS])
            field = ft.TextField(hint_text="Добавить комментарий…", filled=True, bgcolor=CARD,
                                 border_radius=24, border_color=ft.Colors.TRANSPARENT)

            def send(e):
                text = (field.value or "").strip()
                if text:
                    items.controls.append(ft.Text(f"@you  {text}"))
                    field.value = ""
                    page.update()

            field.on_submit = send
            page.open(ft.BottomSheet(
                ft.Container(height=420, padding=16, content=ft.Column(
                    [ft.Text("Комментарии", weight=BOLD, size=16), items, field])),
                bgcolor=BG, show_drag_handle=True, is_scroll_controlled=True))

        def card(pop=False):
            i = st["i"]
            v = VIDEOS[i]
            liked = i in st["liked"]

            def action(icon, label, on_click):
                return ft.Container(on_click=on_click, content=ft.Column(
                    [ico(icon, 34), ft.Text(label, size=12, weight=ft.FontWeight.W_600)],
                    spacing=2, horizontal_alignment=CROSS_C))

            avatar = ft.Stack(width=50, height=58, controls=[
                ft.Container(width=48, height=48, border_radius=24, bgcolor="#000000",
                             border=ft.border.all(2, "white"), padding=9, content=ico("w_mark", 30)),
                ft.Container(left=16, bottom=0, width=18, height=18, border_radius=9, bgcolor=PINK,
                             alignment=CENTER, content=ft.Icon(ft.Icons.ADD, size=12, color="white")),
            ])
            side = ft.Column(spacing=16, horizontal_alignment=CROSS_C, controls=[
                avatar,
                action("heart_on" if liked else "heart", fmt(v["likes"] + liked), like),
                action("comment", fmt(v["comments"]), open_comments),
                action("share", fmt(v["shares"]), share),
                action("save", "", lambda e: toast("Сохранено в закладки")),
            ])
            info = ft.Column(spacing=4, controls=[
                ft.Text(v["user"], weight=BOLD, size=15),
                ft.Text(v["caption"], size=14),
                ft.Text(v["tags"], size=14, weight=ft.FontWeight.W_600),
                ft.Row([ft.Icon(ft.Icons.MUSIC_NOTE, size=14), ft.Text(v["sound"], size=13)], spacing=4),
            ])
            tabs = ft.Row(alignment=MAIN_C, spacing=22, controls=[
                ft.Text("Подписки", size=16, color=ft.Colors.with_opacity(0.7, "white")),
                ft.Column(spacing=3, horizontal_alignment=CROSS_C, controls=[
                    ft.Text("Рекомендации", size=16, weight=BOLD),
                    ft.Container(width=56, height=2, gradient=GRAD)]),
            ])
            shade = ft.LinearGradient(
                begin=ft.alignment.top_center, end=ft.alignment.bottom_center,
                colors=[ft.Colors.with_opacity(0.25, "black"), ft.Colors.TRANSPARENT,
                        ft.Colors.with_opacity(0.78, "black")])
            layers = [
                ft.Image(src=v["bg"], fit=ft.ImageFit.COVER, left=0, top=0, right=0, bottom=0),
                ft.Container(left=0, top=0, right=0, bottom=0, gradient=shade),
                ft.Container(top=10, left=0, right=0, content=tabs),
                ft.Container(left=14, right=90, bottom=16, content=info),
                ft.Container(right=10, bottom=24, content=side),
            ]
            if pop:
                layers.append(ft.Container(left=0, top=0, right=0, bottom=0, alignment=CENTER,
                                           content=ft.Icon(ft.Icons.FAVORITE, size=110, color=PINK)))
            return ft.GestureDetector(content=ft.Stack(layers), on_double_tap=double_tap,
                                      on_vertical_drag_update=drag_update, on_vertical_drag_end=drag_end)

        holder.content = card()
        return holder

    # ------------------------------------------------------------ Интересное
    def explore():
        cats = [("fire", "Популярное"), ("explore", "Интересное"), ("friends", "Друзья"),
                ("music", "Музыка"), ("games", "Игры")]
        chips = ft.Row(scroll=ft.ScrollMode.AUTO, spacing=22, controls=[
            ft.Column([ico(n, 28), ft.Text(t, size=12)], spacing=4, horizontal_alignment=CROSS_C)
            for n, t in cats])
        search = ft.TextField(hint_text="Поиск", prefix_icon=ft.Icons.SEARCH, filled=True, bgcolor=CARD,
                              border_radius=25, border_color=ft.Colors.TRANSPARENT)

        def tile(i):
            v = VIDEOS[i % len(VIDEOS)]
            return ft.Container(
                border_radius=14, clip_behavior=ft.ClipBehavior.ANTI_ALIAS,
                on_click=lambda e, k=i % len(VIDEOS): go(0, k),
                content=ft.Stack([
                    ft.Image(src=v["bg"], fit=ft.ImageFit.COVER, left=0, top=0, right=0, bottom=0),
                    ft.Container(left=8, right=8, bottom=8, content=ft.Column([
                        ft.Text(v["caption"], size=12, max_lines=2),
                        ft.Text(f"♥ {fmt(v['likes'])}", size=12, weight=BOLD)], spacing=2)),
                ]))

        grid = ft.GridView(expand=True, runs_count=2, spacing=8, run_spacing=8,
                           child_aspect_ratio=0.62, controls=[tile(i) for i in range(6)])
        return ft.Container(padding=16, expand=True,
                            content=ft.Column([search, chips, grid], spacing=16, expand=True))

    # --------------------------------------------------------- Создать / Входящие
    def create():
        return ft.Container(expand=True, alignment=CENTER, padding=30, content=ft.Column([
            ico("plus", 96),
            ft.Text("Создай своё видео", size=22, weight=BOLD),
            ft.Text("Запись и загрузка видео появятся в следующей версии", color=MUTED,
                    text_align=ft.TextAlign.CENTER),
            button("Смотреть ленту", lambda e: go(0), gradient=GRAD),
        ], alignment=MAIN_C, horizontal_alignment=CROSS_C, spacing=16))

    def inbox():
        def bubble(icon, text):
            return ft.Container(
                padding=ft.padding.symmetric(horizontal=18, vertical=12), bgcolor=PINK, border_radius=16,
                content=ft.Row([ft.Icon(icon, color="white"), ft.Text(text, size=20, weight=BOLD)], tight=True))
        return ft.Container(padding=20, expand=True, content=ft.Column([
            ft.Text("Входящие", size=24, weight=BOLD),
            bubble(ft.Icons.FAVORITE, "1.2K"),
            bubble(ft.Icons.MODE_COMMENT, "342"),
            bubble(ft.Icons.PERSON_ADD, "+ 856"),
            ft.Text("Новые лайки, комментарии и подписчики появятся здесь", color=MUTED),
        ], spacing=14))

    # ------------------------------------------------------------------ Профиль
    def profile():
        def stat(n, t):
            return ft.Column([ft.Text(n, size=18, weight=BOLD), ft.Text(t, size=12, color=MUTED)],
                             spacing=0, horizontal_alignment=CROSS_C)

        follow = ft.Container()

        def render():
            f = state["following"]
            follow.content = button("Подписки" if f else "Подписаться", toggle,
                                    bg=LINE if f else PINK, width=260)

        def toggle(e):
            state["following"] = not state["following"]
            render()
            follow.update()

        render()
        sound = ft.Container(
            padding=ft.padding.symmetric(horizontal=18, vertical=10), border_radius=24, bgcolor=CARD,
            border=ft.border.all(1, LINE),
            content=ft.Row([ft.Icon(ft.Icons.MUSIC_NOTE, size=18), ft.Text("Оригинальный звук")], tight=True))
        return ft.Container(expand=True, padding=24, content=ft.Column([
            ft.Container(width=96, height=96, border_radius=48, bgcolor="#000000", padding=16,
                         content=ico("w_mark", 64)),
            ft.Text("@winlents", size=20, weight=BOLD),
            ft.Row([stat("128", "Подписки"), stat("12.4K", "Подписчики"), stat("340K", "Лайки")],
                   alignment=ft.MainAxisAlignment.SPACE_EVENLY),
            follow, sound,
        ], horizontal_alignment=CROSS_C, spacing=16))

    # ------------------------------------------------------------ Навигация
    def render_nav():
        def tab(i, icon, label):
            on = state["tab"] == i
            return ft.Container(expand=True, on_click=lambda e: go(i), content=ft.Column(
                [ico(icon, 24, 1.0 if on else 0.55),
                 ft.Text(label, size=10, color="white" if on else MUTED)],
                spacing=3, horizontal_alignment=CROSS_C))
        nav.content = ft.Row(vertical_alignment=CROSS_C, controls=[
            tab(0, "home", "Главная"), tab(1, "search", "Интересное"),
            ft.Container(expand=True, alignment=CENTER, on_click=lambda e: go(2), content=ico("plus", 46)),
            tab(3, "inbox", "Входящие"), tab(4, "profile", "Профиль"),
        ])

    screens = [None, explore, create, inbox, profile]

    def go(i, start=0):
        state["tab"] = i
        body.content = feed(start) if i == 0 else screens[i]()
        render_nav()
        page.update()

    def start_app():
        page.clean()
        page.add(ft.SafeArea(ft.Column([body, nav], spacing=0, expand=True), expand=True))
        go(0)

    # --------------------------------------------------- Приветствие и онбординг
    def splash():
        bar = ft.Row(alignment=MAIN_C, spacing=6, controls=[
            ft.Container(width=46, height=4, border_radius=2, bgcolor=CYAN),
            ft.Container(width=26, height=4, border_radius=2, bgcolor=PINK)])
        page.add(ft.Container(expand=True, bgcolor="#000000", alignment=CENTER, content=ft.Column([
            ft.Image(src="logo_stack.png", width=210),
            ft.Text("Смотри. Создавай.\nБудь в тренде.", size=16, color="#D0D0D5",
                    text_align=ft.TextAlign.CENTER),
            bar,
        ], alignment=MAIN_C, horizontal_alignment=CROSS_C, spacing=28)))
        page.update()
        time.sleep(1.8)

    def onboarding(i=0):
        icon, title, sub = ONBOARDING[i]
        last = i == len(ONBOARDING) - 1
        box = ft.Container(width=300, padding=28, bgcolor=CARD, border=ft.border.all(1, LINE),
                           border_radius=24, content=ft.Column([
                               ft.Icon(icon, size=64, color=PINK),
                               ft.Text(title, size=22, weight=BOLD),
                               ft.Text(sub, size=14, color=MUTED, text_align=ft.TextAlign.CENTER),
                           ], horizontal_alignment=CROSS_C, spacing=12))
        dots = ft.Row(alignment=MAIN_C, spacing=6, controls=[
            ft.Container(width=22 if j == i else 8, height=8, border_radius=4,
                         bgcolor=CYAN if j == i else "#3A3B40") for j in range(len(ONBOARDING))])
        page.clean()
        page.add(ft.SafeArea(ft.Column([
            ft.Image(src="logo_wordmark.png", width=190), box, dots,
            button("Смотреть" if last else "Далее",
                   (lambda e: start_app()) if last else (lambda e, n=i + 1: onboarding(n)), gradient=GRAD),
            ft.TextButton("Пропустить", on_click=lambda e: start_app()) if not last else ft.Container(height=40),
        ], alignment=MAIN_C, horizontal_alignment=CROSS_C, spacing=24, expand=True), expand=True))

    splash()
    onboarding(0)


ft.app(main, assets_dir="assets")
