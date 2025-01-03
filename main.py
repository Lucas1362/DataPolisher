import tkinter as tk
<<<<<<< HEAD
from interface import DataCleanerApp
from estilo import aplicar_estilo_botao, aplicar_estilo_entry

if __name__ == "__main__":
    root = tk.Tk()  # Cria a janela principal
    app = DataCleanerApp(root)  # Inicializa a aplicação
    root.mainloop()  # Inicia o loop da interface gráfica
=======
from cleaner import DataCleanerApp

if __name__ == "__main__":
    root = tk.Tk()
    app = DataCleanerApp(root)
    root.mainloop()
>>>>>>> parent of 4bf3b48 (criação de uma pasta apaneas para a interface com o intuito de diexar o codigo mais maleavel)
