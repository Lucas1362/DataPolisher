"""
Este módulo inicializa a janela principal, define a aparência global do
aplicativo e instancia a classe principal da interface. Ele serve como
ponto de entrada do sistema e não guarda regras de negócio.
"""

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
    root.geometry("1920x1080")  # Define o tamanho inicial da janela
    # Verifica o sistema operacional. Se NÃO for Windows, aplica o vidro.
    if sys.platform != "win32":
        root.attributes("-alpha", 0.85)  # Efeito de vidro sutil na janela

    # Instancia a interface principal, que concentra as funcionalidades.
    app = DataCleanerApp(root)
    root.mainloop()
