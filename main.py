import tkinter as tk
from interface import DataCleanerApp
from estilo import aplicar_estilo_botao, aplicar_estilo_entry

if __name__ == "__main__":
    root = tk.Tk()  # Cria a janela principal
    app = DataCleanerApp(root)  # Inicializa a aplicação
    root.mainloop()  # Inicia o loop da interface gráfica