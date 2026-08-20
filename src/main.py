import customtkinter as ctk
from interface import DataCleanerApp

if __name__ == "__main__":
    # Configurações globais do visual moderno
    ctk.set_appearance_mode("dark")  # Modos: "System" (Padrão), "Dark", "Light"
    ctk.set_default_color_theme("blue")  # Temas: "blue", "green", "dark-blue"
    
    root = ctk.CTk()  # Aqui criamos a janela CustomTkinter
    root.geometry("900x600") 
    
    app = DataCleanerApp(root)
    root.mainloop()