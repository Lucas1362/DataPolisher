# main.py
import tkinter as tk

from cleaner import DataCleanerApp  # Funcionalidades
from interface import DataCleanerInterface  # Interface

if __name__ == "__main__":
    root = tk.Tk()
    
    cleaner_app = DataCleanerApp(root)  # Instancia o DataCleanerApp com funcionalidades
    interface_app = DataCleanerInterface(root, cleaner_app)  # Passa o DataCleanerApp para a interface
    
    root.mainloop()
