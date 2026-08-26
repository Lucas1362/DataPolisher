"""
Este módulo inicializa a janela principal, define a aparência global do
aplicativo e instancia a classe principal da interface. Ele serve como
ponto de entrada do sistema e não guarda regras de negócio.
"""
import flet as ft

from interface import DataCleanerApp

def main(page: ft.Page):
    page.title = "DataPolisher"
    page.theme_mode = ft.ThemeMode.LIGHT
    page.window.width = 1280
    page.window.height = 720
    page.padding = 15
    page.bgcolor = ft.Colors.BLUE_GREY_50

    app = DataCleanerApp(page)
    page.add(app)


if __name__ == "__main__":
    ft.run(main)