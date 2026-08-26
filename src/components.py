"""Componentes reutilizáveis da interface do DataPolisher.

Este módulo centraliza os widgets visuais que aparecem repetidamente no app,
como botões padronizados e pequenas interações de hover. O objetivo é evitar
repetição de código e deixar a criação de novos controles mais consistente.
"""

import tkinter as tk

import customtkinter as ctk


class GlassBackdrop:
    """Fundo decorativo interativo com planos e fraturas de vidro."""

    def __init__(self, root):
        self.root = root
        self.canvas = tk.Canvas(root, highlightthickness=0, bd=0)
        self.canvas.place(relx=0, rely=0, relwidth=1, relheight=1)
        # Canvas.lower() manipula itens internos e exige um identificador;
        # para ordenar o widget inteiro, usamos o comando de stacking do Tk.
        self.canvas.tk.call("lower", self.canvas._w)
        self.dark = False
        self.pointer_x = 0.5
        self.pointer_y = 0.5
        self._draw_id = None
        self.root.bind("<Configure>", self._redraw, add="+")
        self.root.bind("<Motion>", self._on_motion, add="+")
        self.set_theme(False)

    def set_theme(self, dark):
        """Atualiza as cores e redesenha os fragmentos conforme o tema."""
        self.dark = dark
        self._redraw()

    def _on_motion(self, event):
        """Move os planos poucos pixels para simular profundidade sob o cursor."""
        width = max(self.root.winfo_width(), 1)
        height = max(self.root.winfo_height(), 1)
        self.pointer_x = event.x / width - 0.5
        self.pointer_y = event.y / height - 0.5
        if self._draw_id is None:
            self._draw_id = self.root.after(16, self._redraw)

    def _redraw(self, event=None):
        self._draw_id = None
        if not self.canvas.winfo_exists():
            return
        width = max(self.root.winfo_width(), 1)
        height = max(self.root.winfo_height(), 1)
        if width < 10 or height < 10:
            return

        if self.dark:
            background = "#0c1721"
            shard_colors = ("#132b38", "#173442", "#102630")
            crack = "#5da7aa"
        else:
            background = "#d8e8e5"
            shard_colors = ("#eaf7f3", "#c9e1dd", "#f4fbf8")
            crack = "#78a9a4"

        self.canvas.configure(background=background)
        self.canvas.delete("all")
        offset_x = self.pointer_x * 14
        offset_y = self.pointer_y * 10
        polygons = [
            ((0, 0), (width * 0.34, 0), (width * 0.22, height * 0.42), (0, height * 0.28)),
            ((width * 0.35, 0), (width, 0), (width * 0.78, height * 0.34), (width * 0.26, height * 0.22)),
            ((0, height * 0.3), (width * 0.24, height * 0.44), (width * 0.17, height), (0, height)),
            ((width * 0.24, height * 0.44), (width, height * 0.33), (width, height), (width * 0.17, height)),
        ]
        for index, points in enumerate(polygons):
            shifted = [
                (x + offset_x * (index + 1) * 0.12, y + offset_y * (index + 1) * 0.12)
                for x, y in points
            ]
            self.canvas.create_polygon(shifted, fill=shard_colors[index % len(shard_colors)], outline="")

        lines = [
            (width * 0.34, 0, width * 0.24, height * 0.43),
            (width * 0.24, height * 0.43, width * 0.17, height),
            (width * 0.24, height * 0.43, width, height * 0.33),
            (width * 0.26, height * 0.22, width * 0.24, height * 0.43),
        ]
        for x1, y1, x2, y2 in lines:
            self.canvas.create_line(x1, y1, x2, y2, fill=crack, width=1)


def create_glass_backdrop(root):
    """Cria o plano de fundo e o devolve para sincronização com o tema."""
    return GlassBackdrop(root)


def bind_hover_lift(wrapper, button, shadow=None, shadow_color="#8fa8a5"):
    """Cria uma animação leve de elevação ao passar o mouse sobre um botão.

    A função ajusta a posição vertical do widget para dar sensação de profundidade
    sem alterar o comportamento principal do botão nem a lógica de negócio.
    """
    hover_anim_id = None

    def normal_y():
        """Calcula o centro vertical disponível no wrapper do botão."""
        button_height = button.winfo_reqheight()
        return max((wrapper.winfo_height() - button_height) / 2, 0)

    # Bloco de animação: controla o movimento suave até a posição alvo.
    def animate_to(target_y, current_y=0.0):
        nonlocal hover_anim_id

        delta = target_y - current_y
        next_y = current_y + (delta * 0.25)

        if abs(target_y - next_y) < 0.1:
            next_y = target_y

        button.place_configure(y=next_y)
        if shadow is not None:
            shadow.place_configure(y=next_y + 4)

        if next_y != target_y:
            hover_anim_id = button.after(22, animate_to, target_y, next_y)
        else:
            hover_anim_id = None

    # Altera a elevação quando o mouse entra na área do botão.
    def on_enter(event):
        nonlocal hover_anim_id
        if hover_anim_id is not None:
            button.after_cancel(hover_anim_id)
        wrapper.lift()
        button.lift()
        if shadow is not None:
            shadow.configure(fg_color=shadow_color)
        animate_to(normal_y() - 2.0, float(button.place_info().get('y', normal_y())))

    # Restaura a posição original quando o mouse sai do controle.
    def on_leave(event):
        nonlocal hover_anim_id
        if hover_anim_id is not None:
            button.after_cancel(hover_anim_id)
        animate_to(normal_y(), float(button.place_info().get('y', normal_y())))
        if shadow is not None:
            shadow.configure(fg_color="transparent")

    # O estado pressionado reduz a elevação para dar retorno tátil imediato.
    def on_press(event):
        if hover_anim_id is not None:
            button.after_cancel(hover_anim_id)
        button.place_configure(y=normal_y() + 3)
        if shadow is not None:
            shadow.place_configure(y=normal_y() + 7)

    def on_release(event):
        animate_to(-2.0 if button.winfo_containing(event.x_root, event.y_root) else 0.0, 1.0)

    button.bind("<Enter>", on_enter)
    button.bind("<Leave>", on_leave)
    button.bind("<ButtonPress-1>", on_press)
    button.bind("<ButtonRelease-1>", on_release)
    def center_button(event=None):
        current_y = normal_y()
        button.place_configure(y=current_y)
        if shadow is not None:
            shadow.place_configure(y=current_y + 4)

    wrapper.bind("<Configure>", center_button, add="+")


def build_button(parent, row, col, text, command, width, fg_color, hover_color, text_color, border_color, button_height=30, button_font=None, shadow_color="#8fa8a5"):
    """Constrói um botão visualmente uniforme para a toolbar da aplicação.

    O wrapper serve para controlar a área de layout e a animação de hover,
    enquanto o widget do botão recebe os estilos e a ação associada.
    """
    if button_font is None:
        button_font = ctk.CTkFont(size=11, weight="bold")

    # Container que mantém o botão alinhado dentro da grade da barra de ações.
    wrapper = ctk.CTkFrame(parent, fg_color="transparent", width=1, height=button_height + 16)
    wrapper.grid(row=row, column=col, padx=5, pady=8, sticky="nsew")
    wrapper.grid_propagate(False)
    button_height_ratio = button_height / (button_height + 16)

    shadow = ctk.CTkFrame(wrapper, fg_color="transparent", corner_radius=12, height=button_height)
    shadow.place(x=1, y=8, relwidth=1, relheight=button_height_ratio)

    button = ctk.CTkButton(
        wrapper,
        text=text,
        command=command,
        width=width,
        height=button_height,
        fg_color=fg_color,
        hover_color=hover_color,
        text_color=text_color,
        border_color=border_color,
        border_width=2,
        corner_radius=12,
        font=button_font,
    )
    button.place(x=0, y=0, relwidth=1, relheight=button_height_ratio)
    button.configure(cursor="hand2")
    bind_hover_lift(wrapper, button, shadow, shadow_color)
    return button
