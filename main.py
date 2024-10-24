# main.py
import tkinter as tk
from interface import DataCleanerApp

if __name__ == "__main__":
    root = tk.Tk()  # Cria a janela principal
    app = DataCleanerApp(root)  # Inicializa a aplicação
    root.mainloop()  # Inicia o loop da interface gráfica
