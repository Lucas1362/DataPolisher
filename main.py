# main.py
import tkinter as tk

from cleaner import DataCleanerApp  # Funcionalidades


if __name__ == "__main__":
    root = tk.Tk()
    
    cleaner_app = DataCleanerApp(root)  # Instancia o DataCleanerApp com funcionalidades
    # Passa o DataCleanerApp para a interface
    
    root.mainloop()
