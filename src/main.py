import customtkinter as ctk
from interface import DataCleanerApp

if __name__ == "__main__":
    # Configurações globais do visual moderno e acolhedor
    ctk.set_appearance_mode("Light")  # Modos: "System" (Padrão), "Dark", "Light"
    ctk.set_default_color_theme("blue")  # Temas: "blue", "green", "dark-blue"

    root = ctk.CTk()  # Aqui criamos a janela CustomTkinter
    root.geometry("1120x900")
    root.attributes("-alpha", 0.96)  # Efeito vidro sutil na janela

    app = DataCleanerApp(root)
    root.mainloop()