import flet as ft
import sys
from pathlib import Path
from interface import DataCleanerApp


def caminho_recurso(nome: str) -> Path:
    """Localiza recursos tanto no código-fonte quanto no executável empacotado."""
    if getattr(sys, "frozen", False):
        diretorio_base = Path(getattr(sys, "_MEIPASS", Path.cwd()))
    else:
        diretorio_base = Path(__file__).resolve().parent.parent
    return diretorio_base / "assets" / nome


def main(page: ft.Page):
    page.title = "DataPolisher Studio"
    page.theme_mode = ft.ThemeMode.LIGHT
    page.window.width = 1280
    page.window.height = 720
    page.padding = 5
    page.bgcolor = ft.Colors.BLUE_GREY_50

    caminho_arquivo = caminho_recurso("iconeData1.ico")
    if caminho_arquivo.exists():
        page.window.icon = str(caminho_arquivo)

    # Instancia a interface e joga na tela (sem tentar puxar pickers antigos)
    app = DataCleanerApp(page)
    page.add(app)


if __name__ == "__main__":
    ft.run(main)