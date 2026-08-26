import flet as ft
from interface import DataCleanerApp

def main(page: ft.Page):
    page.title = "DataPolisher Studio"
    page.theme_mode = ft.ThemeMode.LIGHT
    page.window.width = 1280
    page.window.height = 720
    page.padding = 5
    page.bgcolor = ft.Colors.BLUE_GREY_50

    # Instancia a interface e joga na tela (sem tentar puxar pickers antigos)
    app = DataCleanerApp(page)
    page.add(app)

if __name__ == "__main__":
    ft.app(target=main)