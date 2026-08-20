import customtkinter as ctk
from interface import DataCleanerApp

if __name__ == "__main__":
    # Configurações globais do visual moderno
    ctk.set_appearance_mode("Dark")  # Modos: "System" (Padrão), "Dark", "Light"
    ctk.set_default_color_theme("dark-blue")  # Temas: "blue", "green", "dark-blue"
    
    root = ctk.CTk()  # Aqui criamos a janela CustomTkinter
    root.geometry("950x650")

    root.attributes("-alpha", 0.80)  # Define a opacidade da janela (0.0 a 1.0)
    app = DataCleanerApp(root)
    root.mainloop()