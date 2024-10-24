# estilo.py
import tkinter as tk

def aplicar_estilo(tk_root, is_dark_mode):
    # Definições de cores para os modos
    if is_dark_mode:
        bg_color = "#222222"
        fg_color = "white"
        button_bg_color = "#555555"
        entry_bg_color = "#333333"
        label_bg_color = "#222222"
    else:
        bg_color = "#f9f9f9"
        fg_color = "#333333"
        button_bg_color = "#4CAF50"
        entry_bg_color = "#f0f0f0"
        label_bg_color = "#f9f9f9"

    # Aplicar cores ao root
    tk_root.config(bg=bg_color)

    # Alterar os estilos de widgets padrão
    for widget in tk_root.winfo_children():
        if isinstance(widget, tk.Button):
            widget.config(bg=button_bg_color, fg=fg_color)
            widget.bind("<Enter>", lambda e: widget.config(bg="#45a049" if not is_dark_mode else "#666666"))
            widget.bind("<Leave>", lambda e: widget.config(bg=button_bg_color))
        elif isinstance(widget, tk.Entry):
            widget.config(bg=entry_bg_color, fg=fg_color)
        elif isinstance(widget, tk.Label):
            widget.config(bg=label_bg_color, fg=fg_color)
        elif isinstance(widget, tk.Frame):
            widget.config(bg=bg_color)
