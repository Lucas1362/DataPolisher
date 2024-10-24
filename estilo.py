import tkinter as tk
from tkinter import ttk

def aplicar_estilo(tk_root, is_dark_mode):
    # Definições de cores para os modos
    cores = {
        "dark": {
            "bg_color": "#1e1e1e",  # Fundo mais escuro
            "fg_color": "#f1f1f1",  # Texto branco suave
            "button_bg_color": "#3b3b3b",  # Botão com fundo mais escuro
            "entry_bg_color": "#2c2c2c",  # Fundo da entrada mais escuro
            "label_bg_color": "#1e1e1e",
            "border_color": "#5c5c5c",  # Cor da borda
            "hover_color": "#444444",  # Cor ao passar o mouse
            "highlight_color": "#ffcc00"  # Cor de destaque ao focar
        },
        "light": {
            "bg_color": "#f0f0f0",  # Fundo claro
            "fg_color": "#2e2e2e",  # Texto escuro
            "button_bg_color": "#4CAF50",  # Botão verde
            "entry_bg_color": "#ffffff",  # Fundo da entrada claro
            "label_bg_color": "#f0f0f0",
            "border_color": "#cccccc",  # Cor da borda
            "hover_color": "#45a049",  # Cor ao passar o mouse
            "highlight_color": "#0066ff"  # Cor de destaque ao focar
        }
    }

    # Escolhe as cores com base no modo
    tema = cores["dark"] if is_dark_mode else cores["light"]

    # Aplicar cor de fundo ao root
    tk_root.config(bg=tema["bg_color"])

    # Cria um estilo para widgets `ttk`
    estilo = ttk.Style()

    estilo.configure("TButton", background=tema["button_bg_color"], foreground=tema["fg_color"], bordercolor=tema["border_color"])
    estilo.map("TButton", background=[("active", tema["hover_color"])])

    estilo.configure("TLabel", background=tema["label_bg_color"], foreground=tema["fg_color"])
    estilo.configure("TEntry", fieldbackground=tema["entry_bg_color"], foreground=tema["fg_color"], highlightcolor=tema["highlight_color"])

    estilo.configure("TFrame", background=tema["bg_color"])

    # Função para lidar com o hover dos botões normais
    def on_enter(e, widget):
        widget.config(bg=tema["hover_color"])

    def on_leave(e, widget):
        widget.config(bg=tema["button_bg_color"])

    # Alterar os estilos de widgets padrão
    for widget in tk_root.winfo_children():
        if isinstance(widget, tk.Button):
            widget.config(bg=tema["button_bg_color"], fg=tema["fg_color"], relief=tk.FLAT, activebackground=tema["hover_color"])
            widget.bind("<Enter>", lambda e, w=widget: on_enter(e, w))
            widget.bind("<Leave>", lambda e, w=widget: on_leave(e, w))
        elif isinstance(widget, tk.Entry):
            widget.config(bg=tema["entry_bg_color"], fg=tema["fg_color"], insertbackground=tema["fg_color"])  # Modifica a cor do cursor
        elif isinstance(widget, tk.Label):
            widget.config(bg=tema["label_bg_color"], fg=tema["fg_color"])
        elif isinstance(widget, tk.Frame):
            widget.config(bg=tema["bg_color"])
        elif isinstance(widget, ttk.Button):
            widget.config(style="TButton")  # Usa estilo para botões ttk
        elif isinstance(widget, ttk.Entry):
            widget.config(style="TEntry")  # Usa estilo para entradas ttk
        elif isinstance(widget, ttk.Label):
            widget.config(style="TLabel")  # Usa estilo para rótulos ttk
        elif isinstance(widget, ttk.Frame):
            widget.config(style="TFrame")  # Usa estilo para frames ttk

    # Personaliza o scrollbar no modo escuro (se necessário)
    scrollbar_estilo = ttk.Style()
    scrollbar_estilo.configure("TScrollbar", troughcolor=tema["bg_color"], background=tema["button_bg_color"], arrowcolor=tema["fg_color"])

