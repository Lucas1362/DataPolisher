"""
Este módulo inicializa a janela principal, define a aparência global do
aplicativo e instancia a classe principal da interface. Ele serve como
ponto de entrada do sistema e não guarda regras de negócio.
"""
import sys
import platform
import customtkinter as ctk
from tkinterdnd2 import TkinterDnD
from interface import DataCleanerApp

if __name__ == "__main__":
    # Configuração global do visual do programa.
    # Define o tema base e a aparência inicial da aplicação.
    ctk.set_appearance_mode("Light")  # Modos: "System", "Dark", "Light"
    ctk.set_default_color_theme("blue")  # Temas: "blue", "green", "dark-blue"

    # Cria a janela principal do app com suporte ao drag-and-drop.
    root = TkinterDnD.Tk()
    root.minsize(980, 700)
    root.update_idletasks()

    # Começa proporcional à tela e centralizada, mantendo o redimensionamento.
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    window_width = max(980, int(screen_width * 0.80))
    window_height = max(700, int(screen_height * 0.85))
    position_x = max(0, (screen_width - window_width) // 2)
    position_y = max(0, (screen_height - window_height) // 2)
    root.geometry(f"{window_width}x{window_height}+{position_x}+{position_y}")
    root.resizable(True, True)
    # Transparência nativa cria o efeito de vidro sem alterar os widgets.
    # O alpha da janela é suportado pelo Tk no Windows, macOS e Linux.
    if platform.system() in {"Windows", "Darwin", "Linux"}:
        root.attributes("-alpha", 0.92)

    # Instancia a interface principal, que concentra as funcionalidades.
    app = DataCleanerApp(root)
    root.mainloop()
