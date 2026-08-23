# interface.py
"""Camada visual do aplicativo DataPolisher.

Este arquivo centraliza a interface gráfica, os fluxos de interação e
as ações que operam sobre o DataFrame carregado. Em termos práticos,
esta classe funciona como o cérebro do app: carrega arquivos, expõe os
botões de funcionalidade, aplica limpezas e atualiza a tabela visível.
"""

import os
import sys
import cleaner
import tkinter as tk
from tkinter import filedialog, messagebox, simpledialog, Toplevel
from tkinter import ttk
import pandas as pd
import customtkinter as ctk

try:
    from tkinterdnd2 import DND_FILES
except ImportError:  # pragma: no cover
    DND_FILES = None

class DataCleanerApp:

    """Aplicativo principal de limpeza e padronização de dados.

    Esta classe concentra a lógica de interface, os fluxos de interação e as
    ações sobre o DataFrame carregado. Em termos de uso, ela funciona como o
    centro operacional do app: carrega arquivos, exibe dados, aplica
    transformações e exporta o resultado final.
    """

    def __init__(self, root):

        # Bloco principal da interface: inicialização do app e do estado geral.
        # Aqui ficam os dados ativos, o histórico do undo e as configurações
        # visuais que afetam toda a aplicação.
       
        self.root = root
        self.root.title("DataPolisher - Limpeza de Dados")
        try:
            self.root.configure(fg_color="#edf4ff")
        except Exception:
            self.root.configure(bg="#edf4ff")
        self.root.minsize(980, 700)
        self.data = None
        self.data_history = []
        self.is_dark_mode = False
        self.language = "pt"
        self.font_scale = 1.0
        self.table_divider_enabled = False
        self.center_numeric_values = True
        self.style = ttk.Style()
        
        # --- ÍCONE ---
        diretorio_atual = os.path.dirname(__file__) 
        caminho_icone = os.path.join(diretorio_atual, "..", "assets", "iconeData1.png")
        try:
            icone = tk.PhotoImage(file=caminho_icone)
            self.root.iconphoto(False, icone)
        except Exception as e:
            print(f"Aviso: Ícone não encontrado. {e}")

        # --- CABEÇALHO DO APP ---
        # Área visual destinada à identidade do produto e ao contexto geral da
        # ferramenta. Mantém o app com uma linguagem mais profissional e clara.
        self.header_frame = ctk.CTkFrame(self.root, fg_color="transparent")
        self.header_frame.pack(pady=(15, 5), padx=20, fill=tk.X)
        
        self.title_label = ctk.CTkLabel(self.header_frame, text="DataPolisher Studio", font=ctk.CTkFont(size=24, weight="bold"))
        self.title_label.pack(side=tk.LEFT, padx=10)
        
        self.subtitle_label = ctk.CTkLabel(self.header_frame, text="Higienização inteligente de dados", font=ctk.CTkFont(size=14, slant="italic"), text_color="gray")
        self.subtitle_label.pack(side=tk.LEFT, padx=5, pady=(8,0))

        self.menu_group = ctk.CTkFrame(self.header_frame, fg_color="transparent")
        self.menu_group.pack(side=tk.RIGHT, padx=10)

        self.menu_label = ctk.CTkLabel(self.menu_group, text="Menu", font=ctk.CTkFont(size=12, weight="bold"))
        self.menu_label.pack(side=tk.LEFT, padx=(0, 6))

        self.menu_button = ctk.CTkButton(
            self.menu_group,
            text="▾",
            command=self.toggle_settings_menu,
            width=36,
            height=28,
            corner_radius=8,
            fg_color="#dfeaff",
            hover_color="#cfe0ff",
            text_color="#1b263b",
        )
        self.menu_button.pack(side=tk.LEFT)

        self.menu_panel = ctk.CTkFrame(
            self.root,
            corner_radius=12,
            border_width=1,
            border_color="#dfeaff",
            fg_color="#f8fbff",
            width=220,
            height=0,
        )
        self.menu_panel.place_forget()
        self.menu_panel.pack_propagate(False)

        self.menu_content = ctk.CTkFrame(self.menu_panel, fg_color="transparent")
        self.menu_content.pack_propagate(False)
        self.menu_content.pack(padx=14, pady=12, fill=tk.X)

        self.menu_settings_label = ctk.CTkLabel(self.menu_content, text="Configurações", font=ctk.CTkFont(size=12, weight="bold"))
        self.menu_settings_label.pack(anchor="w", pady=(0, 8))

        self.theme_switch = ctk.CTkSwitch(
            self.menu_content,
            text="Modo claro",
            command=self.toggle_mode,
            width=140,
            height=28,
            border_color="#9bb1d1",
            fg_color="#d6e4ff",
        )
        self.theme_switch.pack(anchor="w", pady=(0, 8))

        self.language_var = tk.StringVar(value="Português")
        self.language_label = ctk.CTkLabel(self.menu_content, text="Idioma", font=ctk.CTkFont(size=12, weight="bold"))
        self.language_label.pack(anchor="w", pady=(0, 4))
        self.language_selector = ctk.CTkOptionMenu(
            self.menu_content,
            values=["Português", "English"],
            variable=self.language_var,
            width=140,
            command=self.change_language,
        )
        self.language_selector.pack(anchor="w", pady=(0, 8))

        self.font_label = ctk.CTkLabel(self.menu_content, text="Tamanho da fonte", font=ctk.CTkFont(size=12, weight="bold"))
        self.font_label.pack(anchor="w", pady=(0, 4))
        self.font_slider = ctk.CTkSlider(
            self.menu_content,
            from_=0.9,
            to=1.2,
            number_of_steps=12,
            width=140,
            command=self.change_font_scale,
        )
        self.font_slider.set(self.font_scale)
        self.font_slider.pack(anchor="w")

        self.table_settings_label = ctk.CTkLabel(self.menu_content, text="Tabela", font=ctk.CTkFont(size=12, weight="bold"))
        self.table_settings_label.pack(anchor="w", pady=(10, 4))

        self.menu_visible = False
        self._menu_animation_id = None

        # --- ESTILO DA TABELA (modo claro/escuro dinâmico) ---
        self.style.theme_use("default")
        self._apply_theme_colors()

        # ----------------------------------------------------

        # --- BARRA DE FERRAMENTAS ---
        # Mantém os controles em uma faixa compacta acima da tabela, com
        # visual mais parecido com editores de texto e planilhas profissionais.
        self.toolbar_frame = ctk.CTkFrame(self.root, fg_color="transparent")
        self.toolbar_frame.pack(fill=tk.X, padx=20, pady=(0, 8))

        self.button_frame = ctk.CTkFrame(self.toolbar_frame, fg_color="transparent")
        self.button_frame.pack(fill=tk.X)

        self.frame = ctk.CTkFrame(self.root, corner_radius=18, fg_color="#f9fbff", border_color="#dfeaff", border_width=1)
        self.frame.pack(pady=(0, 10), padx=20, fill=tk.BOTH, expand=True)

        self._drop_zone_active = False
        self.drop_hint = ctk.CTkLabel(
            self.frame,
            text="Arraste um arquivo aqui",
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color="#5b7bd6",
            fg_color="#edf4ff",
            corner_radius=12,
            border_width=1,
            border_color="#c6d7ff",
            width=220,
            height=30,
        )
        self.show_drop_hint_if_needed()

        self.toast = ctk.CTkLabel(
            self.root,
            text="",
            font=ctk.CTkFont(size=12, weight="bold"),
            fg_color="#1f9d61",
            text_color="white",
            corner_radius=12,
            border_width=0,
            width=260,
            height=36,
        )
        self.toast.place_forget()
        self.toast_timer = None

        self.tree = ttk.Treeview(self.frame)
        self.tree.grid(row=0, column=0, sticky='nsew', padx=10, pady=10)

        self.scrollbar_y = ctk.CTkScrollbar(self.frame, orientation="vertical", command=self.tree.yview)
        self.scrollbar_y.grid(row=0, column=1, sticky='ns', pady=10)

        self.frame.grid_columnconfigure(0, weight=1)
        self.frame.grid_rowconfigure(0, weight=1)
        self.tree.configure(yscrollcommand=self.scrollbar_y.set)
        self._apply_theme_colors()

        # Arraste horizontal da tabela (simula swipe de touch em desktop)
        self._horizontal_drag_active = False
        self._horizontal_drag_start_x = 0
        self._horizontal_drag_start_scroll = 0.0
        self._horizontal_drag_velocity = 0.0
        self._vertical_drag_velocity = 0.0
        self._horizontal_drag_last_x = 0
        self._horizontal_drag_last_y = 0
        self._horizontal_drag_inertia_id = None
        self._drag_sensitivity = 1.0
        self._drag_vertical_sensitivity = 0.6
        self._drag_friction = 0.98
        self.tree.bind("<Shift-ButtonPress-1>", self._start_horizontal_drag)
        self.tree.bind("<Shift-B1-Motion>", self._move_horizontal_drag)
        self.tree.bind("<Shift-ButtonRelease-1>", self._stop_horizontal_drag)
        self.tree.bind("<ButtonPress-2>", self._start_horizontal_drag)
        self.tree.bind("<B2-Motion>", self._move_horizontal_drag)
        self.tree.bind("<ButtonRelease-2>", self._stop_horizontal_drag)
        self.tree.bind("<ButtonPress-3>", self._start_horizontal_drag)
        self.tree.bind("<B3-Motion>", self._move_horizontal_drag)
        self.tree.bind("<ButtonRelease-3>", self._stop_horizontal_drag)
        self.tree.bind("<MouseWheel>", self._on_mouse_wheel)
        self.tree.bind("<Button-4>", self._on_mouse_wheel)
        self.tree.bind("<Button-5>", self._on_mouse_wheel)
        self.root.bind("<MouseWheel>", self._on_mouse_wheel)
        self.root.bind("<Button-4>", self._on_mouse_wheel)
        self.root.bind("<Button-5>", self._on_mouse_wheel)
        self.frame.bind("<Configure>", self._refresh_table_columns)

        self._setup_drag_and_drop()

        # --- BOTÕES MODERNOS ---
        # Cada botão representa uma funcionalidade específica do fluxo de
        # tratamento de dados. A ideia é deixar a navegação clara e intuitiva.
        button_font = ctk.CTkFont(size=11, weight="bold")
        button_width = 110
        button_height = 30
        common_button_opts = {
            "corner_radius": 0,
            "height": button_height,
            "font": button_font,
            "border_width": 0,
        }

        primary_fg = "#C9A227" if self.is_dark_mode else "#A77B16"
        primary_text = "#0B0B0B" if self.is_dark_mode else "#FFFFFF"
        primary_hover = "#E0B83A" if self.is_dark_mode else "#8F6812"
        primary_press = "#A9841F" if self.is_dark_mode else "#76550E"
        secondary_fg = "#1A1A1A" if self.is_dark_mode else "#FFFFFF"
        secondary_text = "#E5C45A" if self.is_dark_mode else "#80600F"
        secondary_border = "#5C4815" if self.is_dark_mode else "#C9B477"
        secondary_hover = "#242424" if self.is_dark_mode else "#F5F0E2"
        destructive_fg = "#B42318"
        destructive_hover = "#D92D20"

        def build_button(row, col, text, command, width, fg_color, hover_color, text_color, border_color):
            wrapper = ctk.CTkFrame(self.button_frame, fg_color="transparent", width=width + 10, height=button_height + 8)
            wrapper.grid(row=row, column=col, padx=3, pady=6, sticky="nsew")
            wrapper.grid_propagate(False)

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
                border_width=1,
                corner_radius=8,
                font=button_font,
            )
            button.place(x=0, y=0, relwidth=1, relheight=1)
            button.configure(cursor="hand2")
            self._bind_hover_lift(wrapper, button)
            return button

        # Linha única para manter a barra enxuta e mais parecida com ferramentas de edição.
        self.load_button = build_button(0, 0, "Carregar Arquivo", self.load_file, button_width, secondary_fg, secondary_hover, secondary_text, secondary_border)
        self.remove_duplicates_button = build_button(0, 1, "Remover Duplicatas", self.remove_duplicates, button_width, secondary_fg, secondary_hover, secondary_text, secondary_border)
        self.fill_na_button = build_button(0, 2, "Preencher Nulos", self.fill_na, button_width, secondary_fg, secondary_hover, secondary_text, secondary_border)
        self.standardize_button = build_button(0, 3, "Padronizar Dados", self.standardize_data, button_width, secondary_fg, secondary_hover, secondary_text, secondary_border)
        self.rename_column_button = build_button(0, 4, "Renomear Coluna", self.rename_column, button_width, secondary_fg, secondary_hover, secondary_text, secondary_border)
        self.filter_column_button = build_button(0, 5, "Filtrar Coluna", self.filter_column, button_width, secondary_fg, secondary_hover, secondary_text, secondary_border)
        self.filter_row_button = build_button(0, 6, "Filtrar Linha", self.filter_row, button_width, secondary_fg, secondary_hover, secondary_text, secondary_border)
        self.undo_button = build_button(0, 7, "Desfazer", self.undo_action, button_width, secondary_fg, secondary_hover, secondary_text, secondary_border)
        self.save_button = build_button(0, 8, "Salvar", self.save_file, button_width, primary_fg, primary_hover, primary_text, primary_fg)
        self.delete_column_button = build_button(0, 9, "Excluir Coluna", self.delete_column, button_width, destructive_fg, destructive_hover, "#FFFFFF", destructive_fg)

        # Ajuste de expansão
        self.frame.grid_columnconfigure(0, weight=1)
        self.frame.grid_rowconfigure(0, weight=1)
        for i in range(0, 10):
            self.button_frame.grid_columnconfigure(i, weight=1)

        self._apply_ui_texts()
        self._apply_font_scale()
        
        self.root.bind("<F5>", self._recarregar_app)

    def _bind_hover_lift(self, wrapper, button):
        hover_anim_id = None

        def animate_to(target_y, current_y=0.0):
            nonlocal hover_anim_id

            delta = target_y - current_y
            next_y = current_y + (delta * 0.25)

            if abs(target_y - next_y) < 0.1:
                next_y = target_y

            button.place_configure(y=next_y)

            if next_y != target_y:
                hover_anim_id = button.after(12, animate_to, target_y, next_y)
            else:
                hover_anim_id = None

        def on_enter(event):
            nonlocal hover_anim_id
            if hover_anim_id is not None:
                button.after_cancel(hover_anim_id)
            animate_to(-2.0, float(button.place_info().get('y', 0)))

        def on_leave(event):
            nonlocal hover_anim_id
            if hover_anim_id is not None:
                button.after_cancel(hover_anim_id)
            animate_to(0.0, float(button.place_info().get('y', 0)))

        button.bind("<Enter>", on_enter)
        button.bind("<Leave>", on_leave)

    def _translate(self, key):
        translations = {
            "pt": {
                "title": "DataPolisher Studio",
                "subtitle": "Higienização inteligente de dados",
                "menu": "Menu",
                "settings": "Configurações",
                "theme_light": "Modo claro",
                "theme_dark": "Modo escuro",
                "language": "Idioma",
                "font_size": "Tamanho da fonte",
                "load_file": "Carregar Arquivo",
                "remove_duplicates": "Remover Duplicatas",
                "fill_na": "Preencher Nulos",
                "standardize": "Padronizar Dados",
                "filter_column": "Filtrar Coluna",
                "filter_row": "Filtrar Linha",
                "undo": "Desfazer",
                "save": "Salvar",
                "delete_column": "Excluir Coluna",
                "rename_column": "Renomear Coluna",
                "cancel": "Cancelar",
                "apply": "Aplicar",
                "visualize": "Visualizar",
                "close": "Fechar",
            },
            "en": {
                "title": "DataPolisher Studio",
                "subtitle": "Smart data cleaning",
                "menu": "Menu",
                "settings": "Settings",
                "theme_light": "Light mode",
                "theme_dark": "Dark mode",
                "language": "Language",
                "font_size": "Font size",
                "load_file": "Load File",
                "remove_duplicates": "Remove Duplicates",
                "fill_na": "Fill Missing",
                "standardize": "Standardize Data",
                "filter_column": "Filter Column",
                "filter_row": "Filter Row",
                "undo": "Undo",
                "save": "Save",
                "delete_column": "Delete Column",
                "rename_column": "Rename Column",
                "cancel": "Cancel",
                "apply": "Apply",
                "visualize": "View",
                "close": "Close",
            },
        }
        return translations.get(self.language, translations["pt"]).get(key, key)

    def _font_size(self, base_size):
        return max(10, round(base_size * self.font_scale, 1))

    def _apply_ui_texts(self):
        if hasattr(self, "title_label"):
            self.title_label.configure(text=self._translate("title"))
        if hasattr(self, "subtitle_label"):
            self.subtitle_label.configure(text=self._translate("subtitle"))
        if hasattr(self, "menu_label"):
            self.menu_label.configure(text=self._translate("menu"))
        if hasattr(self, "menu_settings_label"):
            self.menu_settings_label.configure(text=self._translate("settings"))
        if hasattr(self, "language_label"):
            self.language_label.configure(text=self._translate("language"))
        if hasattr(self, "font_label"):
            self.font_label.configure(text=self._translate("font_size"))
        if hasattr(self, "theme_switch"):
            self.theme_switch.configure(text=self._translate("theme_dark" if self.is_dark_mode else "theme_light"))

        if hasattr(self, "load_button"):
            self.load_button.configure(text=self._translate("load_file"))
        if hasattr(self, "remove_duplicates_button"):
            self.remove_duplicates_button.configure(text=self._translate("remove_duplicates"))
        if hasattr(self, "fill_na_button"):
            self.fill_na_button.configure(text=self._translate("fill_na"))
        if hasattr(self, "standardize_button"):
            self.standardize_button.configure(text=self._translate("standardize"))
        if hasattr(self, "filter_column_button"):
            self.filter_column_button.configure(text=self._translate("filter_column"))
        if hasattr(self, "filter_row_button"):
            self.filter_row_button.configure(text=self._translate("filter_row"))
        if hasattr(self, "undo_button"):
            self.undo_button.configure(text=self._translate("undo"))
        if hasattr(self, "save_button"):
            self.save_button.configure(text=self._translate("save"))
        if hasattr(self, "delete_column_button"):
            self.delete_column_button.configure(text=self._translate("delete_column"))
        if hasattr(self, "rename_column_button"):
            self.rename_column_button.configure(text=self._translate("rename_column"))

        if hasattr(self, "language_var"):
            self.language_var.set("Português" if self.language == "pt" else "English")

    def _apply_font_scale(self):
        if hasattr(self, "title_label"):
            self.title_label.configure(font=ctk.CTkFont(size=int(round(self._font_size(24))), weight="bold"))
        if hasattr(self, "subtitle_label"):
            self.subtitle_label.configure(font=ctk.CTkFont(size=int(round(self._font_size(14))), slant="italic"))
        if hasattr(self, "menu_label"):
            self.menu_label.configure(font=ctk.CTkFont(size=int(round(self._font_size(12))), weight="bold"))
        if hasattr(self, "menu_settings_label"):
            self.menu_settings_label.configure(font=ctk.CTkFont(size=int(round(self._font_size(12))), weight="bold"))
        if hasattr(self, "language_label"):
            self.language_label.configure(font=ctk.CTkFont(size=int(round(self._font_size(12))), weight="bold"))
        if hasattr(self, "font_label"):
            self.font_label.configure(font=ctk.CTkFont(size=int(round(self._font_size(12))), weight="bold"))
        if hasattr(self, "theme_switch"):
            self.theme_switch.configure(font=ctk.CTkFont(size=int(round(self._font_size(12)))))
        if hasattr(self, "language_selector"):
            self.language_selector.configure(font=ctk.CTkFont(size=int(round(self._font_size(11)))))

        button_font_size = max(10, int(round(self._font_size(11))))
        button_height = max(26, int(round(30 * self.font_scale)))
        button_width = max(92, int(round(110 * self.font_scale)))

        for button_name in [
            "load_button", "remove_duplicates_button", "fill_na_button", "standardize_button",
            "filter_column_button", "filter_row_button", "undo_button", "save_button", "delete_column_button"
        ]:
            if hasattr(self, button_name):
                button = getattr(self, button_name)
                button.configure(
                    font=ctk.CTkFont(size=button_font_size, weight="bold"),
                    width=button_width,
                    height=button_height,
                )

        if hasattr(self, "tree"):
            self._refresh_table_columns()

    def change_language(self, value):
        if value == "English":
            self.language = "en"
        else:
            self.language = "pt"
        self._apply_ui_texts()
        self._apply_font_scale()

    def change_font_scale(self, value):
        self.font_scale = float(value)
        self._apply_font_scale()

    def _get_theme_colors(self):
        # Esquema premium com dourado, preto e tons quentes de joalheria.
        if self.is_dark_mode:
            return {
                "bg": "#161616",
                "panel": "#1C1C1C",
                "surface": "#2B2B2B",
                "surface_alt": "#333333",
                "table_bg": "#1C1C1C",
                "heading": "#252525",
                "heading_active": "#343434",
                "text": "#F5F3EE",
                "secondary_text": "#D5D0C7",
                "selected": "#C9A227",
                "accent": "#C9A227",
                "accent_soft": "#E5C45A",
                "accent_deep": "#8F6C17",
                "border": "#4A4A4A",
                "shadow": "#101010",
            }
        return {
            "bg": "#F5F3EE",
            "panel": "#FFFDFB",
            "surface": "#F9F5F0",
            "surface_alt": "#F0E9DF",
            "table_bg": "#FFFFFF",
            "heading": "#F0E7D5",
            "heading_active": "#E2D4B1",
            "text": "#171717",
            "secondary_text": "#5F5A52",
            "selected": "#C49A32",
            "accent": "#A77B16",
            "accent_soft": "#D8B45B",
            "accent_deep": "#77570F",
            "border": "#D9C89A",
            "shadow": "#D9C7A3",
        }

    def _apply_theme_colors(self):
        colors = self._get_theme_colors()
        try:
            self.root.configure(fg_color=colors["bg"])
        except Exception:
            self.root.configure(bg=colors["bg"])

        if hasattr(self, "header_frame"):
            self.header_frame.configure(fg_color="transparent")
        if hasattr(self, "title_label"):
            self.title_label.configure(text_color=colors["text"])
        if hasattr(self, "subtitle_label"):
            self.subtitle_label.configure(text_color=colors["secondary_text"])
        if hasattr(self, "menu_label"):
            self.menu_label.configure(text_color=colors["text"])
        if hasattr(self, "menu_settings_label"):
            self.menu_settings_label.configure(text_color=colors["text"])
        if hasattr(self, "menu_panel"):
            self.menu_panel.configure(
                fg_color=colors["panel"],
                border_color=colors["accent"],
                corner_radius=16,
            )
        if hasattr(self, "menu_button"):
            self.menu_button.configure(
                fg_color=colors["accent"],
                text_color="#F5F3EE" if self.is_dark_mode else "#FFF9F0",
                hover_color=colors["accent_soft"],
                text="▾" if not self.menu_visible else "▴"
            )
        if hasattr(self, "theme_switch"):
            self.theme_switch.configure(text="Modo escuro" if self.is_dark_mode else "Modo claro")
            self.theme_switch.configure(fg_color=colors["surface"], border_color=colors["accent"])
        if hasattr(self, "rename_column_button"):
            self.rename_column_button.configure(
                fg_color=colors["surface"],
                hover_color=colors["surface_alt"],
                text_color=colors["accent"],
                border_color=colors["border"],
            )

        if hasattr(self, "frame"):
            self.frame.configure(
                fg_color=colors["panel"],
                border_color=colors["border"],
                corner_radius=18,
                border_width=2,
            )

        # Estilo premium para os botões da interface.
        primary_fg = colors["accent"]
        primary_text = "#0B0B0B" if self.is_dark_mode else "#FFF9F0"
        primary_hover = colors["accent_soft"]
        secondary_fg = colors["surface"]
        secondary_text = colors["accent"]
        secondary_hover = colors["surface_alt"]
        secondary_border = colors["border"]
        destructive_fg = "#B42318"
        destructive_hover = "#D92D20"

        for button_name, variant in {
            "load_button": "secondary",
            "remove_duplicates_button": "secondary",
            "fill_na_button": "secondary",
            "standardize_button": "secondary",
            "filter_column_button": "secondary",
            "filter_row_button": "secondary",
            "undo_button": "secondary",
            "save_button": "primary",
            "delete_column_button": "danger",
        }.items():
            if not hasattr(self, button_name):
                continue
            btn = getattr(self, button_name)
            if variant == "primary":
                btn.configure(
                    fg_color=primary_fg,
                    hover_color=primary_hover,
                    text_color=primary_text,
                    border_color=colors["accent_deep"],
                    border_width=1,
                )
            elif variant == "secondary":
                btn.configure(
                    fg_color=secondary_fg,
                    hover_color=secondary_hover,
                    text_color=secondary_text,
                    border_color=secondary_border,
                    border_width=1,
                )
            else:
                btn.configure(
                    fg_color=destructive_fg,
                    hover_color=destructive_hover,
                    text_color="#FFFFFF",
                    border_color=destructive_fg,
                    border_width=1,
                )

        self._apply_drop_zone_visual()
        if hasattr(self, "tree"):
            self.style.configure("Treeview",
                                background=colors["table_bg"],
                                foreground=colors["text"],
                                rowheight=30,
                                fieldbackground=colors["table_bg"],
                                bordercolor=colors["border"],
                                borderwidth=0,
                                relief="flat")
            self.style.map("Treeview", background=[("selected", colors["selected"])])
            self.style.configure("Treeview.Heading",
                                background=colors["heading"],
                                foreground=colors["text"],
                                font=("Arial", 10, "bold"),
                                relief="flat",
                                padding=5,
                                borderwidth=0)
            self.style.map("Treeview.Heading", background=[("active", colors["heading_active"])])

    def _on_mouse_wheel(self, event):
        """Mantém o scroll do mouse em movimento vertical na tabela."""
        if hasattr(event, "delta") and event.delta:
            steps = int(-event.delta / 120)
            if steps:
                self.tree.yview_scroll(steps, "units")
                return "break"

        if getattr(event, "num", None) == 4:
            self.tree.yview_scroll(-1, "units")
            return "break"

        if getattr(event, "num", None) == 5:
            self.tree.yview_scroll(1, "units")
            return "break"

        return "break"

    def _start_horizontal_drag(self, event):
        # Navegação horizontal e vertical da tabela em desktop, simulando swipe.
        # Isso melhora a experiência quando a tabela tem muitas colunas e linhas.
        self._horizontal_drag_active = True
        self._horizontal_drag_start_x = event.x
        self._horizontal_drag_start_scroll = float(self.tree.xview()[0])
        self._horizontal_drag_last_x = event.x
        self._horizontal_drag_last_y = event.y
        self._horizontal_drag_velocity = 0.0
        self._vertical_drag_velocity = 0.0
        if self._horizontal_drag_inertia_id is not None:
            self.root.after_cancel(self._horizontal_drag_inertia_id)
            self._horizontal_drag_inertia_id = None

    def _move_horizontal_drag(self, event):
        if not self._horizontal_drag_active:
            return

        delta_x = event.x - self._horizontal_drag_last_x
        delta_y = event.y - self._horizontal_drag_last_y
        self._horizontal_drag_last_x = event.x
        self._horizontal_drag_last_y = event.y

        current_scroll_x = float(self.tree.xview()[0])
        current_scroll_y = float(self.tree.yview()[0])

        # Mantém a mesma lógica da navegação horizontal, mas deixa o eixo
        # vertical mais suave para movimento de cima/baixo.
        target_scroll_x = current_scroll_x - (delta_x / max(self.tree.winfo_width(), 1)) * self._drag_sensitivity
        target_scroll_y = current_scroll_y - (delta_y / max(self.tree.winfo_height(), 1)) * self._drag_vertical_sensitivity

        target_scroll_x = max(0.0, min(target_scroll_x, 1.0))
        target_scroll_y = max(0.0, min(target_scroll_y, 1.0))

        self.tree.xview_moveto(target_scroll_x)
        self.tree.yview_moveto(target_scroll_y)

        self._horizontal_drag_velocity = (target_scroll_x - current_scroll_x) * 0.5
        self._vertical_drag_velocity = (target_scroll_y - current_scroll_y) * 0.5

    def _stop_horizontal_drag(self, event):
        self._horizontal_drag_active = False
        self._horizontal_drag_velocity *= 0.50
        self._vertical_drag_velocity *= 0.50
        if abs(self._horizontal_drag_velocity) < 0.0005 and abs(self._vertical_drag_velocity) < 0.0005:
            self._horizontal_drag_velocity = 0.0
            self._vertical_drag_velocity = 0.0
            return
        self._animate_horizontal_friction()

    def _animate_horizontal_friction(self):
        if abs(self._horizontal_drag_velocity) < 0.0005 and abs(self._vertical_drag_velocity) < 0.0005:
            self._horizontal_drag_velocity = 0.0
            self._vertical_drag_velocity = 0.0
            self._horizontal_drag_inertia_id = None
            return

        current_x = float(self.tree.xview()[0])
        current_y = float(self.tree.yview()[0])

        next_scroll_x = current_x + self._horizontal_drag_velocity
        next_scroll_y = current_y + self._vertical_drag_velocity

        next_scroll_x = max(0.0, min(next_scroll_x, 1.0))
        next_scroll_y = max(0.0, min(next_scroll_y, 1.0))

        self.tree.xview_moveto(next_scroll_x)
        self.tree.yview_moveto(next_scroll_y)

        self._horizontal_drag_velocity *= self._drag_friction
        self._vertical_drag_velocity *= self._drag_friction
        self._horizontal_drag_inertia_id = self.root.after(7, self._animate_horizontal_friction)

    def _should_center_numeric_column(self, column_name):
        if not self.center_numeric_values:
            return False

        normalized = str(column_name).lower()
        blocked_keywords = (
            "cpf", "cnpj", "rg", "ie", "identidade", "telefone", "celular",
            "cep", "documento", "matricula", "nfe", "inscricao"
        )
        if any(keyword in normalized for keyword in blocked_keywords):
            return False

        numeric_keywords = (
            "valor", "preco", "price", "total", "subtotal", "montante",
            "pedido", "order", "numero_pedido", "n_pedido", "quantidade"
        )
        return any(keyword in normalized for keyword in numeric_keywords)

    def _refresh_table_dividers(self):
        if not hasattr(self, "frame") or not hasattr(self, "tree"):
            return

        for divider in getattr(self, "_table_divider_lines", []):
            divider.destroy()
        self._table_divider_lines = []

        if not self.table_divider_enabled:
            return

        try:
            tree_x = self.tree.winfo_x()
            tree_y = self.tree.winfo_y()
            tree_width = self.tree.winfo_width()
            tree_height = self.tree.winfo_height()
            self.root.update_idletasks()
        except Exception:
            return

        if not tree_width or not tree_height:
            return

        columns = self.tree["columns"]
        if not columns:
            return

        column_widths = [max(self.tree.column(column, "width"), 80) for column in columns]
        total_width = sum(column_widths)
        if total_width <= 0:
            return

        scroll_fraction = float(self.tree.xview()[0]) if hasattr(self.tree, "xview") else 0.0
        visible_width = max(tree_width - 20, 0)
        scroll_offset = scroll_fraction * max(total_width - visible_width, 0)
        divider_color = "#7A7A7A" if self.is_dark_mode else "#9A9A9A"

        x_cursor = 9
        for column_index, column_width in enumerate(column_widths[:-1]):
            x_cursor += column_width
            divider_x = tree_x + x_cursor - scroll_offset
            divider = tk.Frame(self.frame, width=2, height=max(tree_height - 10, 20), bg=divider_color, bd=0, highlightthickness=0)
            divider.place(x=divider_x, y=tree_y + 4)
            self._table_divider_lines.append(divider)

    def _refresh_table_columns(self, event=None):
        if not hasattr(self, "tree"):
            return

        columns = self.tree["columns"]
        if not columns:
            return

        total_columns = len(columns)
        available_width = max(self.frame.winfo_width() - 36, 260)
        base_width = max(120, int(available_width / total_columns))

        for column in columns:
            should_center = self._should_center_numeric_column(column)
            self.tree.column(column, width=base_width, minwidth=120, stretch=False, anchor="center" if should_center else "w")
            self.tree.heading(column, anchor="center" if should_center else "w")

        self._refresh_table_dividers()

    def toggle_table_dividers(self, force_state=None):
        self.table_divider_enabled = False
        if hasattr(self, "tree"):
            self._refresh_table_dividers()
        self._apply_theme_colors()

    def _position_menu_panel(self):
        if not hasattr(self, "menu_group") or not self.menu_group.winfo_ismapped():
            return

        self.root.update_idletasks()
        panel_width = max(self.menu_panel.winfo_reqwidth(), 220)
        root_width = self.root.winfo_width()
        root_height = self.root.winfo_height()

        base_x = self.menu_group.winfo_rootx() - self.root.winfo_rootx() - 8
        base_y = self.menu_group.winfo_rooty() - self.root.winfo_rooty() + self.menu_group.winfo_height() + 10

        max_x = max(12, root_width - panel_width - 12)
        x = min(max(base_x, 12), max_x)
        y = min(max(base_y, 12), max(12, root_height - 150))

        self.menu_panel.place(x=x, y=y)
        self.menu_panel.lift()

    def _menu_target_height(self):
        self.root.update_idletasks()
        content_height = self.menu_content.winfo_reqheight() if hasattr(self, "menu_content") else 0
        target_height = max(240, content_height + 40)
        max_height = max(240, self.root.winfo_height() - 100)
        return min(target_height, max_height)

    def _animate_menu(self, opening):
        target_height = self._menu_target_height()

        if opening:
            current_height = self.menu_panel.winfo_height()
            next_height = min(current_height + 18, target_height)
            self.menu_panel.configure(height=next_height)
            if next_height < target_height:
                self._menu_animation_id = self.root.after(16, self._animate_menu, True)
                return
            self._menu_animation_id = None
            self._position_menu_panel()
            return

        current_height = self.menu_panel.winfo_height()
        next_height = max(current_height - 18, 0)
        self.menu_panel.configure(height=next_height)
        if next_height > 0:
            self._menu_animation_id = self.root.after(16, self._animate_menu, False)
            return

        self.menu_panel.configure(height=0)
        self.menu_panel.place_forget()
        self._menu_animation_id = None

    def toggle_settings_menu(self):
        self.menu_visible = not self.menu_visible
        if self.menu_visible:
            self.root.update_idletasks()
            self._position_menu_panel()
            self.menu_panel.configure(height=0)
            self.menu_panel.lift()
            self._animate_menu(True)
        else:
            if self._menu_animation_id is not None:
                self.root.after_cancel(self._menu_animation_id)
                self._menu_animation_id = None
            self._animate_menu(False)
        self._apply_theme_colors()

    def toggle_mode(self):
        # Alterna o tema visual do app sem mexer na lógica dos dados.
        switch_state = bool(self.theme_switch.get())

        if switch_state == self.is_dark_mode:
            self.is_dark_mode = not self.is_dark_mode
            if self.is_dark_mode:
                self.theme_switch.select()
            else:
                self.theme_switch.deselect()
        else:
            self.is_dark_mode = switch_state

        ctk.set_appearance_mode("dark" if self.is_dark_mode else "light")
        self.theme_switch.configure(text="Modo escuro" if self.is_dark_mode else "Modo claro")
        self._apply_theme_colors()

    def aplicar_estilo(self):
        # Aplica o estilo completo
        aplicar_estilo(self.root, self.is_dark_mode)

    def _setup_drag_and_drop(self):
        target_widget = getattr(self, "frame", None)
        if DND_FILES is None or target_widget is None or not hasattr(target_widget, "drop_target_register"):
            return

        try:
            target_widget.drop_target_register(DND_FILES)
            target_widget.dnd_bind("<<DropEnter>>", self.on_drag_enter)
            target_widget.dnd_bind("<<DropLeave>>", self.on_drag_leave)
            target_widget.dnd_bind("<<Drop>>", self.on_drop_files)
        except Exception:
            pass

    def on_drag_enter(self, event):
        self._drop_zone_active = True
        self._apply_drop_zone_visual()

    def on_drag_leave(self, event):
        self._drop_zone_active = False
        self._apply_drop_zone_visual()

    def hide_drop_hint(self):
        if hasattr(self, "drop_hint"):
            self.drop_hint.place_forget()

    def show_drop_hint_if_needed(self):
        if self.data is None and hasattr(self, "drop_hint"):
            colors = self._get_theme_colors()
            self.drop_hint.configure(
                fg_color=colors["surface_alt"],
                border_color=colors["accent"],
                text_color=colors["accent"],
            )
            self.drop_hint.configure(text="Arraste um arquivo aqui")
            self.drop_hint.place(relx=0.5, rely=0.5, anchor="center")
            self.drop_hint.lift()
        else:
            self.hide_drop_hint()

    def _apply_drop_zone_visual(self):
        if not hasattr(self, "drop_hint"):
            return

        colors = self._get_theme_colors()

        if self._drop_zone_active:
            self.hide_drop_hint()
            if hasattr(self, "frame"):
                self.frame.configure(border_color=colors["accent_soft"], border_width=3)
        else:
            if self.data is None:
                self.drop_hint.configure(
                    fg_color=colors["surface_alt"],
                    border_color=colors["accent"],
                    text_color=colors["accent"],
                )
                self.drop_hint.configure(text="Arraste um arquivo aqui")
                self.drop_hint.place(relx=0.5, rely=0.5, anchor="center")
                self.drop_hint.lift()
            else:
                self.hide_drop_hint()
            if hasattr(self, "frame"):
                self.frame.configure(border_color=colors["border"], border_width=2)

    def parse_dropped_files(self, data):
        if not data:
            return []

        if isinstance(data, (list, tuple)):
            return [str(item).strip() for item in data if str(item).strip()]

        file_text = str(data).strip()
        if not file_text:
            return []

        if file_text.startswith("{") and file_text.endswith("}"):
            file_text = file_text[1:-1]

        if hasattr(self.root, "tk") and hasattr(self.root.tk, "splitlist"):
            parsed = self.root.tk.splitlist(file_text)
            return [str(item).strip() for item in parsed if str(item).strip()]

        return [part.strip() for part in file_text.split() if part.strip()]

    def on_drop_files(self, event):
        self._drop_zone_active = False
        self.hide_drop_hint()
        self._apply_drop_zone_visual()

        files = self.parse_dropped_files(event.data)
        if not files:
            return

        for file_path in files:
            if self.load_file_from_path(file_path):
                break

    def hide_drop_hint(self):
        if hasattr(self, "drop_hint"):
            self.drop_hint.place_forget()

    def load_file_from_path(self, file_path):
        if not file_path:
            return False

        self._drop_zone_active = False
        self.hide_drop_hint()
        self._apply_drop_zone_visual()

        file_path = os.path.abspath(os.path.expanduser(file_path))

        if not os.path.exists(file_path):
            messagebox.showerror("Erro", f"Arquivo não encontrado: {file_path}")
            return False

        try:
            if file_path.endswith('.csv'):
                self.data = pd.read_csv(file_path)
            elif file_path.endswith(('.xlsx', '.xls')):
                self.data = pd.read_excel(file_path)
            elif file_path.endswith('.ods'):
                self.data = pd.read_excel(file_path, engine="odf")
            elif file_path.endswith('.json'):
                self.data = pd.read_json(file_path)
            elif file_path.endswith('.pdf'):
                messagebox.showwarning("Aviso", "Ainda não suportamos leitura de PDF. Escolha Excel ou CSV.")
                return False
            else:
                messagebox.showerror("Erro", "Formato de arquivo não suportado.")
                return False

            if hasattr(self, 'data_history'):
                self.data_history = []

            self.show_data()
            self.show_toast(f"Arquivo carregado: {self.data.shape[0]} linhas e {self.data.shape[1]} colunas.")
            return True
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao carregar o arquivo: {e}")
            return False

    # Funcionalidade de carregamento de dados.
    # Aceita CSV, Excel, ODS e JSON, e depois prepara o DataFrame para
    # as ações de limpeza e visualização na tabela.
    def load_file(self):
        # 1. Expandimos as opções de filtros na janela de abrir arquivo
        tipos_de_arquivos = [
            ("Planilhas e Dados", "*.csv *.xlsx *.xls *.ods *.json"),
            ("Arquivos CSV", "*.csv"),
            ("Excel", "*.xlsx *.xls"),
            ("LibreOffice Calc", "*.ods"),
            ("JSON", "*.json"),
            ("Todos os arquivos", "*.*")
        ]

        file_path = filedialog.askopenfilename(filetypes=tipos_de_arquivos)
        if file_path:
            self.load_file_from_path(file_path)

    def show_toast(self, message, color=None, duration=1800):
        if not hasattr(self, "toast"):
            return

        if color is None:
            color = self._get_theme_colors()["accent"]

        self.toast.configure(text=message, fg_color=color)
        self.toast.place(relx=0.5, rely=0.94, anchor="center")
        self.toast.lift()

        if self.toast_timer is not None:
            self.root.after_cancel(self.toast_timer)

        self.toast_timer = self.root.after(duration, self.hide_toast)

    def hide_toast(self):
        if hasattr(self, "toast"):
            self.toast.place_forget()
        self.toast_timer = None

    def show_data(self):
        # Atualiza a interface com o estado atual do DataFrame.
        # Esse bloco é o ponto central de sincronização entre dados e tabela.
        for i in self.tree.get_children():
            self.tree.delete(i)

        if self.data is not None and not self.data.empty:
            self.tree["columns"] = list(self.data.columns)
            self.tree["show"] = "headings"

            for column in self.tree["columns"]:
                self.tree.heading(column, text=column)
                self.tree.column(column, width=120, minwidth=120, stretch=False)

            for index, row in self.data.iterrows():
                self.tree.insert("", "end", values=list(row))

            self.root.after_idle(self._refresh_table_columns)
            self.show_drop_hint_if_needed()
        else:
            self.show_drop_hint_if_needed()
            messagebox.showwarning("Aviso", "Não há dados para mostrar.")

    # Funcionalidade de preenchimento de nulos.
    # Permite preencher toda a base ou apenas uma coluna, com conversão
    # automática de valores numéricos para manter a consistência do tipo.
    def fill_na(self):
        if self.data is not None:
            if self.data.isnull().values.any():
                # 1. Pergunta qual coluna o usuário quer alterar
                coluna = simpledialog.askstring("Preencher Nulos", "Qual coluna deseja preencher? (Deixe em branco para preencher TODAS)")
                
                if coluna is not None: # Se o usuário não clicou em "Cancelar"
                    # 2. Pergunta o valor a ser inserido
                    valor = simpledialog.askstring("Preencher Nulos", "Digite o valor para preencher os espaços vazios:")
                    
                    if valor is not None:
                        # Salva o estado atual para o botão Desfazer
                        if hasattr(self, 'data_history'):
                            self.data_history.append(self.data.copy())
                        
                        # 3. MÁGICA: Tenta converter o que o usuário digitou para número. 
                        # Isso impede que colunas numéricas virem texto!
                        try:
                            if '.' in valor or ',' in valor:
                                valor = float(valor.replace(',', '.'))
                            else:
                                valor = int(valor)
                        except ValueError:
                            pass # Se não for número, mantém como texto normalmente

                        # 4. Aplica a mudança
                        if coluna.strip() == "":
                            # Se deixou em branco, preenche o DataFrame todo
                            self.data = self.data.fillna(valor)
                            msg = f"Todos os nulos foram preenchidos com: {valor}"
                        elif coluna in self.data.columns:
                            # Se digitou uma coluna válida, preenche só ela
                            self.data[coluna] = self.data[coluna].fillna(valor)
                            msg = f"Nulos da coluna '{coluna}' preenchidos com: {valor}"
                        else:
                            # Se digitou o nome da coluna errado
                            messagebox.showwarning("Aviso", "Nome da coluna não encontrado!")
                            self.data_history.pop() # Remove o histórico salvo pois a ação falhou
                            return

                        self.show_data()
                        messagebox.showinfo("Sucesso", msg)
            else:
                messagebox.showinfo("Aviso", "Nenhum valor ausente encontrado no DataFrame.")
        else:
            messagebox.showwarning("Aviso", "Carregue um arquivo primeiro.")

    # Funcionalidade para remover registros duplicados.
    # Útil quando a base de dados foi importada de mais de uma fonte e
    # existe repetição de linhas sem valor real.
    def remove_duplicates(self):
        if self.data is not None:
            self.data_history.append(self.data.copy())
            original_length = len(self.data)

            self.data = cleaner.remove_duplicates(self.data)

            new_length = len(self.data)
            if new_length < original_length:
                self.show_data()
                messagebox.showinfo("Sucesso", f"Duplicatas removidas: {original_length - new_length} entradas.")
            else:
                self.data_history.pop()
                messagebox.showinfo("Aviso", "Nenhuma duplicata encontrada.")
        else:
            messagebox.showwarning("Aviso", "Carregue um arquivo primeiro.")

    # Funcionalidade de padronização textual.
    # Centraliza a regra de normalização para colunas de texto, ajudando a
    # deixar nomes, cidades e campos livres com um padrão consistente.
    def standardize_data(self):
        if self.data is None:
            messagebox.showwarning("Aviso", "Carregue um arquivo primeiro.")
            return

        modal = ctk.CTkToplevel(self.root)
        modal.title("Padronizar Dados")
        modal.geometry("440x250")
        modal.transient(self.root)
        modal.grab_set()
        modal.configure(fg_color="#f3f7ff")

        card = ctk.CTkFrame(modal, fg_color="#ffffff", corner_radius=20, border_width=1, border_color="#dfeaff")
        card.pack(fill=tk.BOTH, expand=True, padx=18, pady=18)

        title = ctk.CTkLabel(card, text="Padronizar texto", font=ctk.CTkFont(size=20, weight="bold"), text_color="#1b263b")
        title.pack(anchor="w", padx=20, pady=(18, 4))

        subtitle = ctk.CTkLabel(card, text="Escolha a coluna e o estilo de texto desejado.", font=ctk.CTkFont(size=12), text_color="#53627a")
        subtitle.pack(anchor="w", padx=20, pady=(0, 12))

        columns = ["Todas as colunas"] + list(self.data.columns)
        column_var = tk.StringVar(value=columns[0])
        case_var = tk.StringVar(value="minúsculas")

        column_selector = ctk.CTkOptionMenu(card, values=columns, variable=column_var, width=260, fg_color="#edf4ff", button_color="#f4c27d", button_hover_color="#efb463")
        column_selector.pack(padx=20, pady=(0, 12), fill=tk.X)

        case_selector = ctk.CTkOptionMenu(card, values=["minúsculas", "maiúsculas", "título"], variable=case_var, width=260, fg_color="#edf4ff", button_color="#8ab6ff", button_hover_color="#72a5ff")
        case_selector.pack(padx=20, pady=(0, 16), fill=tk.X)

        def apply_standardization():
            selected_column = column_var.get()
            case_map = {
                "minúsculas": "lower",
                "maiúsculas": "upper",
                "título": "title",
            }
            target_case = case_map.get(case_var.get(), "lower")

            try:
                if hasattr(self, 'data_history'):
                    self.data_history.append(self.data.copy())

                if selected_column == "Todas as colunas":
                    self.data = cleaner.standardize_dataframe(self.data, case=target_case)
                    message = "Todos os textos foram padronizados."
                else:
                    self.data = cleaner.standardize_dataframe(self.data, column=selected_column, case=target_case)
                    message = f"Coluna '{selected_column}' padronizada."

                self.show_data()
                messagebox.showinfo("Sucesso", message)
                modal.destroy()
            except Exception as exc:
                messagebox.showerror("Erro", f"Não foi possível padronizar os dados: {exc}")

        action_bar = ctk.CTkFrame(card, fg_color="transparent")
        action_bar.pack(fill=tk.X, padx=20, pady=(0, 18))

        cancel = ctk.CTkButton(action_bar, text="Cancelar", width=110, fg_color="#e6ecff", hover_color="#dfeaff", text_color="#1b263b", command=modal.destroy)
        cancel.pack(side=tk.LEFT)

        apply_btn = ctk.CTkButton(action_bar, text="Aplicar", width=110, fg_color="#7bd6a1", hover_color="#63c78f", text_color="#103022", command=apply_standardization)
        apply_btn.pack(side=tk.RIGHT)

    # Funcionalidade de filtro por coluna.
    # Mantém apenas a coluna escolhida para análise focada ou revisão rápida.
    def filter_column(self):
        if self.data is None:
            messagebox.showwarning("Aviso", "Carregue um arquivo primeiro.")
            return

        if self.data.empty or self.data.columns.empty:
            messagebox.showwarning("Aviso", "Não há colunas disponíveis para filtrar.")
            return

        modal = ctk.CTkToplevel(self.root)
        modal.title("Filtrar por Coluna")
        modal.geometry("420x240")
        modal.minsize(420, 220)
        modal.transient(self.root)
        modal.grab_set()
        modal.configure(fg_color="#f3f7ff")

        card = ctk.CTkFrame(modal, fg_color="#ffffff", corner_radius=20, border_width=1, border_color="#dfeaff")
        card.pack(fill=tk.BOTH, expand=True, padx=18, pady=18)

        title = ctk.CTkLabel(card, text="Filtrar por coluna", font=ctk.CTkFont(size=20, weight="bold"), text_color="#1b263b")
        title.pack(anchor="w", padx=20, pady=(18, 6))

        subtitle = ctk.CTkLabel(card, text="Escolha a coluna que deseja manter na tabela.", font=ctk.CTkFont(size=12), text_color="#53627a")
        subtitle.pack(anchor="w", padx=20, pady=(0, 12))

        columns = list(self.data.columns)
        selected = tk.StringVar(value=columns[0])
        combo = ctk.CTkOptionMenu(card, values=columns, variable=selected, width=260, fg_color="#edf4ff", button_color="#8ab6ff", button_hover_color="#72a5ff")
        combo.pack(padx=20, pady=(0, 16), fill=tk.X)

        def apply_filter():
            column_name = selected.get()
            if not column_name or column_name not in self.data.columns:
                messagebox.showwarning("Atenção", "Coluna inválida.")
                return

            if hasattr(self, 'data_history'):
                self.data_history.append(self.data.copy())

            self.data = self.data[[column_name]]
            self.show_data()
            self.show_popup(f"Filtro aplicado! Mostrando apenas a coluna: {column_name}")
            modal.destroy()

        action_bar = ctk.CTkFrame(card, fg_color="transparent")
        action_bar.pack(fill=tk.X, padx=20, pady=(0, 18))

        cancel = ctk.CTkButton(action_bar, text="Cancelar", width=110, fg_color="#e6ecff", hover_color="#dfeaff", text_color="#1b263b", command=modal.destroy)
        cancel.pack(side=tk.LEFT)

        apply_btn = ctk.CTkButton(action_bar, text="Aplicar", width=110, fg_color="#7bd6a1", hover_color="#63c78f", text_color="#103022", command=apply_filter)
        apply_btn.pack(side=tk.RIGHT)

    # Funcionalidade de filtro por linha.
    # Abre uma visualização detalhada da linha selecionada para revisão manual.
    def filter_row(self):
        if self.data is None:
            messagebox.showwarning("Aviso", "Carregue um arquivo primeiro.")
            return

        if self.data.empty:
            messagebox.showwarning("Aviso", "Não há linhas para filtrar.")
            return

        modal = ctk.CTkToplevel(self.root)
        modal.title("Filtrar por Linha")
        modal.geometry("420x260")
        modal.minsize(420, 230)
        modal.transient(self.root)
        modal.grab_set()
        modal.configure(fg_color="#f3f7ff")

        card = ctk.CTkFrame(modal, fg_color="#ffffff", corner_radius=20, border_width=1, border_color="#dfeaff")
        card.pack(fill=tk.BOTH, expand=True, padx=18, pady=18)

        title = ctk.CTkLabel(card, text="Filtrar por linha", font=ctk.CTkFont(size=20, weight="bold"), text_color="#1b263b")
        title.pack(anchor="w", padx=20, pady=(18, 6))

        subtitle = ctk.CTkLabel(card, text="Informe o número da linha que você deseja visualizar.", font=ctk.CTkFont(size=12), text_color="#53627a")
        subtitle.pack(anchor="w", padx=20, pady=(0, 12))

        row_var = tk.StringVar(value="1")
        row_entry = ctk.CTkEntry(card, textvariable=row_var, width=260, placeholder_text="Ex: 12")
        row_entry.pack(padx=20, pady=(0, 16), fill=tk.X)

        def apply_filter():
            try:
                row_number = int(row_var.get())
            except ValueError:
                messagebox.showwarning("Atenção", "Digite um número válido para a linha.")
                return

            if not 1 <= row_number <= len(self.data):
                messagebox.showwarning("Atenção", "Número da linha inválido!")
                return

            row_data = self.data.iloc[row_number - 1]
            result_window = ctk.CTkToplevel(self.root)
            result_window.title(f"Linha {row_number}")
            result_window.geometry("500x340")
            result_window.resizable(True, True)
            result_window.transient(self.root)
            result_window.grab_set()
            result_window.configure(fg_color="#f3f7ff")

            result_card = ctk.CTkFrame(result_window, fg_color="#ffffff", corner_radius=20, border_width=1, border_color="#dfeaff")
            result_card.pack(fill=tk.BOTH, expand=True, padx=18, pady=18)

            label = ctk.CTkLabel(result_card, text=f"Linha {row_number}", font=ctk.CTkFont(size=18, weight="bold"), text_color="#1b263b")
            label.pack(anchor="w", padx=18, pady=(16, 10))

            text_box = tk.Text(result_card, wrap=tk.WORD, height=12, bg="#f9fbff", fg="#1b263b", font=("Segoe UI", 10), relief="flat")
            text_box.pack(fill=tk.BOTH, expand=True, padx=18, pady=(0, 12))

            for column, value in row_data.items():
                if pd.isna(value):
                    value = "Dados não disponíveis"
                text_box.insert(tk.END, f"{column}: {value}\n")

            text_box.config(state=tk.DISABLED)

            close_button = ctk.CTkButton(result_card, text="Fechar", width=120, command=result_window.destroy, fg_color="#e6ecff", hover_color="#dfeaff", text_color="#1b263b")
            close_button.pack(anchor="e", padx=18, pady=(0, 16))
            modal.destroy()

        action_bar = ctk.CTkFrame(card, fg_color="transparent")
        action_bar.pack(fill=tk.X, padx=20, pady=(0, 18))

        cancel = ctk.CTkButton(action_bar, text="Cancelar", width=110, fg_color="#e6ecff", hover_color="#dfeaff", text_color="#1b263b", command=modal.destroy)
        cancel.pack(side=tk.LEFT)

        apply_btn = ctk.CTkButton(action_bar, text="Visualizar", width=110, fg_color="#b99cff", hover_color="#a889ff", text_color="#1f1638", command=apply_filter)
        apply_btn.pack(side=tk.RIGHT)



    # Funcionalidade de exclusão de colunas.
    # Remove campos irrelevantes, descartáveis ou redundantes da base atual.
    def delete_column(self):
        if self.data is not None:
            column_name = simpledialog.askstring("Excluir Coluna", "Digite o nome da coluna:")
            if column_name and column_name in self.data.columns:
                # Salva no histórico
                self.data_history.append(self.data.copy())
                
                # Usa o nosso arquivo cleaner.py para fazer o trabalho pesado!
                self.data = cleaner.delete_column(self.data, column_name)
                
                self.show_data()
                messagebox.showinfo("Sucesso", f"Coluna '{column_name}' excluída!")
            else:
                messagebox.showwarning("Aviso", "Coluna inválida ou não encontrada.")
        else:
            messagebox.showwarning("Aviso", "Carregue um arquivo primeiro.")

    def rename_column(self):
        if self.data is None:
            messagebox.showwarning("Aviso", "Carregue um arquivo primeiro.")
            return

        if self.data.empty or self.data.columns.empty:
            messagebox.showwarning("Aviso", "Não há colunas disponíveis para renomear.")
            return

        modal = ctk.CTkToplevel(self.root)
        modal.title("Renomear Coluna")
        modal.geometry("440x270")
        modal.transient(self.root)
        modal.grab_set()
        modal.configure(fg_color="#f3f7ff")

        card = ctk.CTkFrame(modal, fg_color="#ffffff", corner_radius=20, border_width=1, border_color="#dfeaff")
        card.pack(fill=tk.BOTH, expand=True, padx=18, pady=18)

        title = ctk.CTkLabel(card, text="Renomear coluna", font=ctk.CTkFont(size=20, weight="bold"), text_color="#1b263b")
        title.pack(anchor="w", padx=20, pady=(18, 6))

        subtitle = ctk.CTkLabel(card, text="Escolha a coluna atual e informe o novo nome.", font=ctk.CTkFont(size=12), text_color="#53627a")
        subtitle.pack(anchor="w", padx=20, pady=(0, 12))

        columns = list(self.data.columns)
        selected_column = tk.StringVar(value=columns[0])
        new_name_var = tk.StringVar(value="")

        column_selector = ctk.CTkOptionMenu(card, values=columns, variable=selected_column, width=260, fg_color="#edf4ff", button_color="#8ab6ff", button_hover_color="#72a5ff")
        column_selector.pack(padx=20, pady=(0, 12), fill=tk.X)

        new_name_entry = ctk.CTkEntry(card, textvariable=new_name_var, width=260, placeholder_text="Novo nome da coluna")
        new_name_entry.pack(padx=20, pady=(0, 16), fill=tk.X)

        def apply_rename():
            old_name = selected_column.get()
            new_name = str(new_name_var.get()).strip()

            if not new_name:
                messagebox.showwarning("Atenção", "Digite um nome válido para a coluna.")
                return

            if new_name == old_name:
                messagebox.showinfo("Informação", "O novo nome é igual ao nome atual.")
                modal.destroy()
                return

            if new_name in self.data.columns and new_name != old_name:
                messagebox.showwarning("Atenção", f"O nome '{new_name}' já existe na tabela.")
                return

            if hasattr(self, 'data_history'):
                self.data_history.append(self.data.copy())

            self.data = self.data.rename(columns={old_name: new_name})
            self.show_data()
            messagebox.showinfo("Sucesso", f"Coluna '{old_name}' renomeada para '{new_name}'.")
            modal.destroy()

        action_bar = ctk.CTkFrame(card, fg_color="transparent")
        action_bar.pack(fill=tk.X, padx=20, pady=(0, 18))

        cancel = ctk.CTkButton(action_bar, text="Cancelar", width=110, fg_color="#e6ecff", hover_color="#dfeaff", text_color="#1b263b", command=modal.destroy)
        cancel.pack(side=tk.LEFT)

        apply_btn = ctk.CTkButton(action_bar, text="Salvar", width=110, fg_color="#7bd6a1", hover_color="#63c78f", text_color="#103022", command=apply_rename)
        apply_btn.pack(side=tk.RIGHT)

    # Janela de retorno visual para mensagens rápidas.
    # Usada para confirmar ações e avisar sobre estados importantes da base.
    def show_popup(self, message):
        popup = Toplevel(self.root)
        popup.title("Resultado")
        popup.geometry("400x300")
        popup.resizable(True, True)
        label = tk.Label(popup, text=message, wraplength=350)
        label.pack(pady=20)
        ok_button = tk.Button(popup, text="OK", command=popup.destroy)
        ok_button.pack(pady=10)

    # Funcionalidade de exportação.
    # Permite salvar os dados tratados em CSV, Excel ou JSON conforme a
    # necessidade do usuário ou do fluxo de trabalho.
    def save_file(self):
        if self.data is not None:
            file_path = filedialog.asksaveasfilename(defaultextension=".csv",
                                                    filetypes=[
                                                        ("CSV files", "*.csv"),
                                                        ("Excel files", "*.xlsx"),
                                                        ("JSON files", "*.json"),
                                                        ("PDF files", "*.pdf")
                                                    ])
            if file_path:
                self.save_data(file_path)
        else:
            messagebox.showwarning("Aviso", "Não há dados para salvar.")

    # Bloco central de exportação do DataFrame.
    # Recebe o caminho escolhido e aplica o formato correto sem espalhar a
    # lógica de salvamento pelo restante da interface.
    def save_data(self, file_path):
        if file_path.endswith('.csv'):
            self.data.to_csv(file_path, index=False)
            messagebox.showinfo("Sucesso", f"Arquivo CSV salvo com sucesso em:\n{file_path}")
        elif file_path.endswith('.xlsx'):
            self.data.to_excel(file_path, index=False)
            messagebox.showinfo("Sucesso", f"Arquivo Excel salvo com sucesso em:\n{file_path}")
        elif file_path.endswith('.json'):
            self.data.to_json(file_path, orient='records', lines=True)
            messagebox.showinfo("Sucesso", f"Arquivo JSON salvo com sucesso em:\n{file_path}")
        elif file_path.endswith('.pdf'):
            # Aqui você pode adicionar a lógica para salvar como PDF
            # Usando uma biblioteca como matplotlib ou reportlab
            messagebox.showinfo("Atenção", "PDFs ainda não implementados.")
        else:
            messagebox.showerror("Erro", "Formato de arquivo não suportado.")


    # Funcionalidade de desfazer.
    # Restaura o último estado do DataFrame antes da última operação,
    # funcionando como mecanismo de segurança para correções rápidas.
    def undo_action(self):
        if self.data_history: # Verifica se existe algum histórico salvo
            # Pega o último estado salvo e remove da lista de histórico
            self.data = self.data_history.pop() 
            self.show_data() # Atualiza a tabela na tela
            messagebox.showinfo("Desfazer", "Última ação desfeita com sucesso!")
        else:
            messagebox.showwarning("Aviso", "Não há nenhuma ação para desfazer.")
    def _recarregar_app(self, event=None):
  
        python = sys.executable
        os.execv(python, [python] + sys.argv)