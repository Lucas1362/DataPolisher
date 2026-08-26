# interface.py
"""Camada visual do aplicativo DataPolisher.

Este arquivo concentra a janela principal, a tabela e a coordenação entre
os widgets visuais e os módulos de componentes e modais.
"""

import os
import sys
import tkinter as tk
from tkinter import filedialog, messagebox, simpledialog, Toplevel
from tkinter import ttk

import customtkinter as ctk
import pandas as pd

import cleaner
from components import build_button, bind_hover_lift, create_glass_backdrop
from estilo import aplicar_estilo
from modals import filter_column as filter_column_modal
from modals import filter_row as filter_row_modal
from modals import rename_column as rename_column_modal
from modals import standardize_data as standardize_data_modal

try:
    from tkinterdnd2 import DND_FILES
except ImportError:  # pragma: no cover
    DND_FILES = None


class DataCleanerApp:
    """Aplicativo principal de limpeza e padronização de dados.

    Esta classe representa a camada principal da interface. Ela organiza a
    janela, as ações do usuário, a tabela e as interações do app com os
    módulos de componentes e modais.
    """

    def __init__(self, root):
        # Bloco de inicialização do estado principal do app.
        self.root = root
        # O canvas fica atrás dos widgets e reage ao cursor como uma camada de vidro.
        self.glass_backdrop = create_glass_backdrop(root)
        self.root.title("DataPolisher - Limpeza de Dados")
        try:
            self.root.configure(fg_color="#dce9e7")
        except Exception:
            self.root.configure(bg="#dce9e7")
        self.root.minsize(980, 700)
        # A janela ganha presença quando está ativa e recua levemente quando perde foco.
        self._window_alpha_active = 0.97
        self._window_alpha_inactive = 0.91
        self.root.attributes("-alpha", self._window_alpha_active)
        self.root.bind("<FocusIn>", self._on_window_focus_in)
        self.root.bind("<FocusOut>", self._on_window_focus_out)
        self.data = None
        self.data_history = []
        self.is_dark_mode = False
        self.language = "pt"
        self.font_scale = 1.0
        self.table_divider_enabled = False
        self.center_numeric_values = True
        self.style = ttk.Style()

        # Bloco de ícone e identidade visual do programa.
        diretorio_atual = os.path.dirname(__file__)
        caminho_icone_ico = os.path.join(diretorio_atual, "..", "assets", "iconeData1.ico")
        caminho_icone = os.path.join(diretorio_atual, "..", "assets", "iconeData1.png")
        try:
            if os.name == "nt" and os.path.exists(caminho_icone_ico):
                self.root.iconbitmap(default=caminho_icone_ico)
            else:
                self._icon_image = tk.PhotoImage(file=caminho_icone)
                self.root.iconphoto(False, self._icon_image)
        except Exception as e:
            print(f"Aviso: Ícone não carregado. {e}")

        # Bloco do cabeçalho da aplicação: título, subtítulo e menu de configurações.
        self.header_frame = ctk.CTkFrame(self.root, fg_color="transparent")
        self.header_frame.pack(pady=(15, 5), padx=20, fill=tk.X)

        self.title_label = ctk.CTkLabel(self.header_frame, text="DataPolisher Studio", font=ctk.CTkFont(size=24, weight="bold"))
        self.title_label.pack(side=tk.LEFT, padx=10)

        self.subtitle_label = ctk.CTkLabel(self.header_frame, text="Higienização inteligente de dados", font=ctk.CTkFont(size=14, slant="italic"), text_color="gray")
        self.subtitle_label.pack(side=tk.LEFT, padx=5, pady=(8, 0))

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
            corner_radius=20,
            border_width=1,
            border_color="#dfeaff",
            fg_color="#f8fbff",
            width=320,
            height=0,
        )
        self.menu_panel.place_forget()
        self.menu_panel.pack_propagate(False)

        self.menu_content = ctk.CTkFrame(self.menu_panel, fg_color="transparent")
        self.menu_content.grid_columnconfigure(1, weight=1)
        self.menu_content.pack_propagate(False)
        self.menu_content.pack(padx=16, pady=14, fill=tk.X)

        self.menu_settings_label = ctk.CTkLabel(self.menu_content, text="Configurações", font=ctk.CTkFont(size=12, weight="bold"))
        self.menu_settings_label.grid(row=0, column=0, columnspan=2, sticky="w", pady=(0, 10))

        self.theme_switch = ctk.CTkSwitch(
            self.menu_content,
            text="Modo claro",
            command=self.toggle_mode,
            width=140,
            height=28,
            border_color="#9bb1d1",
            fg_color="#d6e4ff",
        )
        self.theme_switch.grid(row=1, column=0, columnspan=2, sticky="w", pady=(0, 12))

        self.language_var = tk.StringVar(value="Português")
        self.language_label = ctk.CTkLabel(self.menu_content, text="Idioma", font=ctk.CTkFont(size=12, weight="bold"))
        self.language_label.grid(row=2, column=0, sticky="w", padx=(0, 12), pady=(0, 8))
        self.language_selector = ctk.CTkOptionMenu(
            self.menu_content,
            values=["Português", "English"],
            variable=self.language_var,
            width=140,
            corner_radius=16,
            command=self.change_language,
        )
        self.language_selector.grid(row=2, column=1, sticky="ew", pady=(0, 8))

        self.font_label = ctk.CTkLabel(self.menu_content, text="Tamanho da fonte", font=ctk.CTkFont(size=12, weight="bold"))
        self.font_label.grid(row=3, column=0, sticky="w", padx=(0, 12), pady=(0, 8))
        self.font_slider = ctk.CTkSlider(
            self.menu_content,
            from_=0.9,
            to=1.2,
            number_of_steps=12,
            width=140,
            command=self.change_font_scale,
        )
        self.font_slider.set(self.font_scale)
        self.font_slider.grid(row=3, column=1, sticky="ew", pady=(0, 8))

        self.table_settings_label = ctk.CTkLabel(self.menu_content, text="Tabela", font=ctk.CTkFont(size=12, weight="bold"))
        self.table_settings_label.grid(row=4, column=0, columnspan=2, sticky="w", pady=(8, 4))

        self.menu_visible = False
        self._menu_animation_id = None
        self.style.theme_use("default")
        self._apply_theme_colors()

        # Bloco da barra de ferramentas: reúne os botões de ação principais do app.
        self.toolbar_frame = ctk.CTkFrame(self.root, fg_color="transparent", height=124)
        self.toolbar_frame.pack(fill=tk.X, padx=20, pady=(0, 12))
        self.toolbar_frame.pack_propagate(False)

        # O quadro dos botões é irmão da toolbar e apenas usa sua posição como referência.
        # Assim, a elevação dos botões não fica limitada pela ordem do container.
        self.button_frame = ctk.CTkFrame(self.root, fg_color="transparent", height=124)
        self.button_frame.place(in_=self.toolbar_frame, relx=0, rely=0, relwidth=1, relheight=1)

        # Bloco da área central da janela: tabela e área de drag-and-drop.
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
        self.tree.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)

        self.scrollbar_y = ctk.CTkScrollbar(self.frame, orientation="vertical", command=self.tree.yview)
        self.scrollbar_y.grid(row=0, column=1, sticky="ns", pady=10)

        self.frame.grid_columnconfigure(0, weight=1)
        self.frame.grid_rowconfigure(0, weight=1)
        self.tree.configure(yscrollcommand=self.scrollbar_y.set)
        self._apply_theme_colors()

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

        # Bloco de botões de ação: cada controle dispara uma operação de limpeza ou visualização.
        button_font = ctk.CTkFont(size=11, weight="bold")
        button_width = 110
        button_height = 30
        primary_fg = "#C9A227" if self.is_dark_mode else "#A77B16"
        primary_text = "#0B0B0B" if self.is_dark_mode else "#FFFFFF"
        primary_hover = "#E0B83A" if self.is_dark_mode else "#8F6812"
        secondary_fg = "#1A1A1A" if self.is_dark_mode else "#FFFFFF"
        secondary_text = "#E5C45A" if self.is_dark_mode else "#80600F"
        secondary_border = "#5C4815" if self.is_dark_mode else "#C9B477"
        secondary_hover = "#242424" if self.is_dark_mode else "#F5F0E2"
        destructive_fg = "#B42318"
        destructive_hover = "#D92D20"

        self.load_button = build_button(self.button_frame, 0, 0, "Carregar Arquivo", self.load_file, button_width, secondary_fg, secondary_hover, secondary_text, secondary_border, button_height, button_font)
        self.remove_duplicates_button = build_button(self.button_frame, 0, 1, "Remover Duplicatas", self.remove_duplicates, button_width, secondary_fg, secondary_hover, secondary_text, secondary_border, button_height, button_font)
        self.fill_na_button = build_button(self.button_frame, 0, 2, "Preencher Nulos", self.fill_na, button_width, secondary_fg, secondary_hover, secondary_text, secondary_border, button_height, button_font)
        self.standardize_button = build_button(self.button_frame, 0, 3, "Padronizar Dados", self.standardize_data, button_width, secondary_fg, secondary_hover, secondary_text, secondary_border, button_height, button_font)
        self.rename_column_button = build_button(self.button_frame, 0, 4, "Renomear Coluna", self.rename_column, button_width, secondary_fg, secondary_hover, secondary_text, secondary_border, button_height, button_font)
        self.filter_column_button = build_button(self.button_frame, 1, 0, "Filtrar Coluna", self.filter_column, button_width, secondary_fg, secondary_hover, secondary_text, secondary_border, button_height, button_font)
        self.filter_row_button = build_button(self.button_frame, 1, 1, "Filtrar Linha", self.filter_row, button_width, secondary_fg, secondary_hover, secondary_text, secondary_border, button_height, button_font)
        self.undo_button = build_button(self.button_frame, 1, 2, "Desfazer", self.undo_action, button_width, secondary_fg, secondary_hover, secondary_text, secondary_border, button_height, button_font)
        self.save_button = build_button(self.button_frame, 1, 3, "Salvar", self.save_file, button_width, primary_fg, primary_hover, primary_text, primary_fg, button_height, button_font)
        self.delete_column_button = build_button(self.button_frame, 1, 4, "Excluir Coluna", self.delete_column, button_width, destructive_fg, destructive_hover, "#FFFFFF", destructive_fg, button_height, button_font)

        # Mantém a toolbar acima da borda da área de dados durante a elevação dos botões.
        self.toolbar_frame.lift()
        self.button_frame.lift()

        self.frame.grid_columnconfigure(0, weight=1)
        self.frame.grid_rowconfigure(0, weight=1)
        for i in range(5):
            self.button_frame.grid_columnconfigure(i, weight=1)

        self._apply_ui_texts()
        self._apply_font_scale()
        self.root.bind("<F5>", self._recarregar_app)

    def _bind_hover_lift(self, wrapper, button):
        bind_hover_lift(wrapper, button)

    def _translate(self, key):
        # Bloco de internacionalização: traduz textos visuais para português e inglês.
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
        if self.is_dark_mode:
            return {
                "bg": "#101c28",
                "panel": "#182a38",
                "surface": "#223b4a",
                "surface_alt": "#2d4b5a",
                "table_bg": "#162734",
                "heading": "#214052",
                "heading_active": "#2d5667",
                "text": "#edf7f6",
                "secondary_text": "#a9c3c5",
                "selected": "#277f86",
                "accent": "#5ed0c5",
                "accent_soft": "#8be1d5",
                "accent_deep": "#287f83",
                "border": "#416575",
                "shadow": "#0a141e",
            }
        return {
            "bg": "#dce9e7",
            "panel": "#f5fbfa",
            "surface": "#eef7f5",
            "surface_alt": "#d5e9e5",
            "table_bg": "#f8fcfb",
            "heading": "#d9ece9",
            "heading_active": "#bfe0da",
            "text": "#17313b",
            "secondary_text": "#55717a",
            "selected": "#65c7bd",
            "accent": "#087f8c",
            "accent_soft": "#46b9b0",
            "accent_deep": "#075c6a",
            "border": "#b5d5d1",
            "shadow": "#a9c9c5",
        }

    def _on_window_focus_in(self, event=None):
        """Retoma a transparência principal quando a janela fica ativa."""
        self.root.attributes("-alpha", self._window_alpha_active)

    def _on_window_focus_out(self, event=None):
        """Reduz discretamente a opacidade para reforçar a sensação de camada de vidro."""
        self.root.attributes("-alpha", self._window_alpha_inactive)

    def _apply_theme_colors(self):
        # Bloco de temas visuais: aplica as cores do modo claro/escuro para toda a UI.
        colors = self._get_theme_colors()
        if hasattr(self, "glass_backdrop"):
            self.glass_backdrop.set_theme(self.is_dark_mode)
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
            self.menu_panel.configure(fg_color=colors["surface"], border_color=colors["border"], corner_radius=18)
        if hasattr(self, "menu_button"):
            self.menu_button.configure(fg_color=colors["accent"], text_color="#F5F3EE" if self.is_dark_mode else "#FFF9F0", hover_color=colors["accent"], border_width=0, text="▾" if not self.menu_visible else "▴")
        if hasattr(self, "theme_switch"):
            self.theme_switch.configure(text="Modo escuro" if self.is_dark_mode else "Modo claro")
            self.theme_switch.configure(fg_color=colors["surface"], border_color=colors["accent"])
        if hasattr(self, "rename_column_button"):
            self.rename_column_button.configure(fg_color=colors["surface"], hover_color=colors["surface_alt"], text_color=colors["accent"], border_color=colors["border"])

        if hasattr(self, "frame"):
            self.frame.configure(fg_color=colors["panel"], border_color=colors["border"], corner_radius=22, border_width=1)

        primary_fg = colors["accent"]
        primary_text = "#0B0B0B" if self.is_dark_mode else "#FFF9F0"
        primary_hover = colors["accent_soft"]
        secondary_fg = colors["surface"]
        secondary_text = colors["accent"]
        secondary_hover = colors["surface_alt"]
        secondary_border = colors["border"]
        destructive_fg = "#c45558"
        destructive_hover = "#dc7772"

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
            if hasattr(self, button_name):
                btn = getattr(self, button_name)
                if variant == "primary":
                    btn.configure(fg_color=primary_fg, hover_color=primary_hover, text_color=primary_text, border_color=colors["accent_deep"], border_width=1)
                elif variant == "secondary":
                    btn.configure(fg_color=secondary_fg, hover_color=secondary_hover, text_color=secondary_text, border_color=secondary_border, border_width=1)
                else:
                    btn.configure(fg_color=destructive_fg, hover_color=destructive_hover, text_color="#FFFFFF", border_color=destructive_fg, border_width=1)

        self._apply_drop_zone_visual()
        if hasattr(self, "tree"):
            self.style.configure("Treeview", background=colors["table_bg"], foreground=colors["text"], rowheight=30, fieldbackground=colors["table_bg"], bordercolor=colors["border"], borderwidth=0, relief="flat")
            self.style.map("Treeview", background=[("selected", colors["selected"])])
            self.style.configure("Treeview.Heading", background=colors["heading"], foreground=colors["text"], font=("Arial", 10, "bold"), relief="flat", padding=5, borderwidth=0)
            self.style.map("Treeview.Heading", background=[("active", colors["heading_active"])])

    def _on_mouse_wheel(self, event):
        # Bloco de navegação da tabela por rolagem do mouse.
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
        blocked_keywords = ("cpf", "cnpj", "rg", "ie", "identidade", "telefone", "celular", "cep", "documento", "matricula", "nfe", "inscricao")
        if any(keyword in normalized for keyword in blocked_keywords):
            return False
        numeric_keywords = ("valor", "preco", "price", "total", "subtotal", "montante", "pedido", "order", "numero_pedido", "n_pedido", "quantidade")
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
            tree_x = self.tree.winfo_x(); tree_y = self.tree.winfo_y(); tree_width = self.tree.winfo_width(); tree_height = self.tree.winfo_height(); self.root.update_idletasks()
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
        for column_width in column_widths[:-1]:
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
        panel_width = max(self.menu_panel.winfo_reqwidth(), 320)
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
            remaining = target_height - current_height
            next_height = min(current_height + max(10, int(remaining * 0.42)), target_height)
            self.menu_panel.configure(height=next_height)
            if next_height < target_height:
                self._menu_animation_id = self.root.after(12, self._animate_menu, True)
                return
            self._menu_animation_id = None
            self._position_menu_panel()
            return
        current_height = self.menu_panel.winfo_height()
        next_height = max(current_height - max(10, int(current_height * 0.42)), 0)
        self.menu_panel.configure(height=next_height)
        if next_height > 0:
            self._menu_animation_id = self.root.after(12, self._animate_menu, False)
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
        aplicar_estilo(self.root, self.is_dark_mode)

    def _setup_drag_and_drop(self):
        # Bloco de drag-and-drop: permite importar arquivos arrastando para a área da tabela.
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
            self.drop_hint.configure(fg_color=colors["surface_alt"], border_color=colors["accent"], text_color=colors["accent"])
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
                self.drop_hint.configure(fg_color=colors["surface_alt"], border_color=colors["accent"], text_color=colors["accent"])
                self.drop_hint.configure(text="Arraste um arquivo aqui")
                self.drop_hint.place(relx=0.5, rely=0.5, anchor="center")
                self.drop_hint.lift()
            else:
                self.hide_drop_hint()
            if hasattr(self, "frame"):
                self.frame.configure(border_color=colors["border"], border_width=1)

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

    def load_file_from_path(self, file_path):
        # Bloco de carregamento do arquivo: lê CSV, Excel, ODS e JSON com validação do formato.
        if not file_path:
            return False
        self._drop_zone_active = False
        self.hide_drop_hint(); self._apply_drop_zone_visual()
        file_path = str(file_path).strip().strip('"')
        file_path = os.path.abspath(os.path.expanduser(file_path))
        if not os.path.exists(file_path):
            messagebox.showerror("Erro", f"Arquivo não encontrado: {file_path}")
            return False
        try:
            extension = os.path.splitext(file_path)[1].lower()
            if extension == '.csv':
                self.data = pd.read_csv(file_path)
            elif extension in ('.xlsx', '.xls'):
                self.data = pd.read_excel(file_path)
            elif extension == '.ods':
                self.data = pd.read_excel(file_path, engine="odf")
            elif extension == '.json':
                self.data = pd.read_json(file_path)
            elif extension == '.pdf':
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

    def load_file(self):
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
        # Bloco de renderização da tabela: atualiza os cabeçalhos e registros visíveis.
        for i in self.tree.get_children():
            self.tree.delete(i)
        if self.data is not None and not self.data.empty:
            self.tree["columns"] = list(self.data.columns)
            self.tree["show"] = "headings"
            for column in self.tree["columns"]:
                self.tree.heading(column, text=column)
                self.tree.column(column, width=120, minwidth=120, stretch=False)
            for _, row in self.data.iterrows():
                self.tree.insert("", "end", values=list(row))
            self.root.after_idle(self._refresh_table_columns)
            self.show_drop_hint_if_needed()
        else:
            self.show_drop_hint_if_needed()
            messagebox.showwarning("Aviso", "Não há dados para mostrar.")

    def fill_na(self):
        # Bloco de preenchimento de nulos: preenche valores ausentes pela coluna ou pelo DataFrame inteiro.
        if self.data is not None:
            if self.data.isnull().values.any():
                coluna = simpledialog.askstring("Preencher Nulos", "Qual coluna deseja preencher? (Deixe em branco para preencher TODAS)")
                if coluna is not None:
                    valor = simpledialog.askstring("Preencher Nulos", "Digite o valor para preencher os espaços vazios:")
                    if valor is not None:
                        if hasattr(self, 'data_history'):
                            self.data_history.append(self.data.copy())
                        try:
                            if '.' in valor or ',' in valor:
                                valor = float(valor.replace(',', '.'))
                            else:
                                valor = int(valor)
                        except ValueError:
                            pass
                        if coluna.strip() == "":
                            self.data = self.data.fillna(valor)
                            msg = f"Todos os nulos foram preenchidos com: {valor}"
                        elif coluna in self.data.columns:
                            self.data[coluna] = self.data[coluna].fillna(valor)
                            msg = f"Nulos da coluna '{coluna}' preenchidos com: {valor}"
                        else:
                            messagebox.showwarning("Aviso", "Nome da coluna não encontrado!")
                            self.data_history.pop()
                            return
                        self.show_data(); messagebox.showinfo("Sucesso", msg)
            else:
                messagebox.showinfo("Aviso", "Nenhum valor ausente encontrado no DataFrame.")
        else:
            messagebox.showwarning("Aviso", "Carregue um arquivo primeiro.")

    def remove_duplicates(self):
        # Bloco de remoção de duplicatas: mantém a base sem registros repetidos e guarda undo.
        if self.data is not None:
            self.data_history.append(self.data.copy())
            original_length = len(self.data)
            self.data = cleaner.remove_duplicates(self.data)
            new_length = len(self.data)
            if new_length < original_length:
                self.show_data(); messagebox.showinfo("Sucesso", f"Duplicatas removidas: {original_length - new_length} entradas.")
            else:
                self.data_history.pop(); messagebox.showinfo("Aviso", "Nenhuma duplicata encontrada.")
        else:
            messagebox.showwarning("Aviso", "Carregue um arquivo primeiro.")

    def standardize_data(self):
        standardize_data_modal(self)

    def filter_column(self):
        filter_column_modal(self)

    def filter_row(self):
        filter_row_modal(self)

    def delete_column(self):
        if self.data is not None:
            column_name = simpledialog.askstring("Excluir Coluna", "Digite o nome da coluna:")
            if column_name and column_name in self.data.columns:
                self.data_history.append(self.data.copy())
                self.data = cleaner.delete_column(self.data, column_name)
                self.show_data(); messagebox.showinfo("Sucesso", f"Coluna '{column_name}' excluída!")
            else:
                messagebox.showwarning("Aviso", "Coluna inválida ou não encontrada.")
        else:
            messagebox.showwarning("Aviso", "Carregue um arquivo primeiro.")

    def rename_column(self):
        rename_column_modal(self)

    def show_popup(self, message):
        popup = Toplevel(self.root)
        popup.title("Resultado")
        popup.geometry("400x300")
        popup.resizable(True, True)
        label = tk.Label(popup, text=message, wraplength=350)
        label.pack(pady=20)
        ok_button = tk.Button(popup, text="OK", command=popup.destroy)
        ok_button.pack(pady=10)

    def save_file(self):
        # Bloco de exportação do resultado final: salva em CSV, Excel ou JSON.
        if self.data is not None:
            file_path = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV files", "*.csv"), ("Excel files", "*.xlsx"), ("JSON files", "*.json"), ("PDF files", "*.pdf")])
            if file_path:
                self.save_data(file_path)
        else:
            messagebox.showwarning("Aviso", "Não há dados para salvar.")

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
            messagebox.showinfo("Atenção", "PDFs ainda não implementados.")
        else:
            messagebox.showerror("Erro", "Formato de arquivo não suportado.")

    def undo_action(self):
        # Bloco de desfazer: restaura o último estado do DataFrame antes da última ação.
        if self.data_history:
            self.data = self.data_history.pop()
            self.show_data()
            messagebox.showinfo("Desfazer", "Última ação desfeita com sucesso!")
        else:
            messagebox.showwarning("Aviso", "Não há nenhuma ação para desfazer.")

    def _recarregar_app(self, event=None):
        python = sys.executable
        os.execv(python, [python] + sys.argv)