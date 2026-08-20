# interface.py
import os
import cleaner
import tkinter as tk
from tkinter import filedialog, messagebox, simpledialog, Toplevel
from tkinter import ttk
import pandas as pd
import customtkinter as ctk

class DataCleanerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("DataPolisher - Limpeza de Dados")
        self.root.configure(fg_color="#edf4ff")
        self.root.minsize(980, 700)
        self.data = None
        self.data_history = []
        self.is_dark_mode = False
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
        self.header_frame = ctk.CTkFrame(self.root, fg_color="transparent")
        self.header_frame.pack(pady=(15, 5), padx=20, fill=tk.X)
        
        self.title_label = ctk.CTkLabel(self.header_frame, text="DataPolisher Studio", font=ctk.CTkFont(size=24, weight="bold"))
        self.title_label.pack(side=tk.LEFT, padx=10)
        
        self.subtitle_label = ctk.CTkLabel(self.header_frame, text="Higienização inteligente de dados", font=ctk.CTkFont(size=14, slant="italic"), text_color="gray")
        self.subtitle_label.pack(side=tk.LEFT, padx=5, pady=(8,0))

        # --- ESTILO DA TABELA (modo claro/escuro dinâmico) ---
        self.style.theme_use("default")
        self._apply_theme_colors()
        # ----------------------------------------------------

        # --- FRAME DA TABELA ---
        self.frame = ctk.CTkFrame(self.root, corner_radius=18, fg_color="#f9fbff", border_color="#dfeaff", border_width=1)
        self.frame.pack(pady=10, padx=20, fill=tk.BOTH, expand=True)

        self.tree = ttk.Treeview(self.frame)
        self.tree.grid(row=0, column=0, sticky='nsew', padx=10, pady=10)

        self.scrollbar_y = ctk.CTkScrollbar(self.frame, orientation="vertical", command=self.tree.yview)
        self.scrollbar_y.grid(row=0, column=1, sticky='ns', pady=10)

        self.tree.configure(yscrollcommand=self.scrollbar_y.set)
        self._apply_theme_colors()

        # Arraste horizontal da tabela (simula swipe de touch em desktop)
        self._horizontal_drag_active = False
        self._horizontal_drag_start_x = 0
        self._horizontal_drag_start_scroll = 0.0
        self._horizontal_drag_velocity = 0.0
        self._horizontal_drag_last_x = 0
        self._horizontal_drag_inertia_id = None
        self.tree.bind("<Shift-ButtonPress-1>", self._start_horizontal_drag)
        self.tree.bind("<Shift-B1-Motion>", self._move_horizontal_drag)
        self.tree.bind("<Shift-ButtonRelease-1>", self._stop_horizontal_drag)
        self.tree.bind("<ButtonPress-2>", self._start_horizontal_drag)
        self.tree.bind("<B2-Motion>", self._move_horizontal_drag)
        self.tree.bind("<ButtonRelease-2>", self._stop_horizontal_drag)
        self.tree.bind("<ButtonPress-3>", self._start_horizontal_drag)
        self.tree.bind("<B3-Motion>", self._move_horizontal_drag)
        self.tree.bind("<ButtonRelease-3>", self._stop_horizontal_drag)
        self.tree.bind("<MouseWheel>", self._on_mouse_wheel_horizontal)
        self.tree.bind("<Shift-MouseWheel>", self._on_mouse_wheel_horizontal)

        # --- FRAME DOS BOTÕES ---
        self.button_frame = ctk.CTkFrame(self.root, fg_color="transparent")
        self.button_frame.pack(pady=10, padx=20, fill=tk.X)

        # --- BOTÕES MODERNOS ---
        button_font = ctk.CTkFont(size=12, weight="bold")
        common_button_opts = {
            "corner_radius": 10,
            "height": 38,
            "font": button_font,
            "border_width": 0,
        }

        # LINHA 0 (4 botões)
        self.load_button = ctk.CTkButton(self.button_frame, text="Carregar Arquivo", command=self.load_file, width=160, fg_color="#7aa7ff", hover_color="#5c8ef5", text_color="#0d1b2a", **common_button_opts)
        self.load_button.grid(row=0, column=0, padx=8, pady=10)

        self.remove_duplicates_button = ctk.CTkButton(self.button_frame, text="Remover Duplicatas", command=self.remove_duplicates, width=160, fg_color="#b99cff", hover_color="#a889ff", text_color="#1f1638", **common_button_opts)
        self.remove_duplicates_button.grid(row=0, column=1, padx=8, pady=10)

        self.fill_na_button = ctk.CTkButton(self.button_frame, text="Preencher Nulos", command=self.fill_na, width=160, fg_color="#7ad7d0", hover_color="#62c8c0", text_color="#0d2c2c", **common_button_opts)
        self.fill_na_button.grid(row=0, column=2, padx=8, pady=10)

        self.standardize_button = ctk.CTkButton(self.button_frame, text="Padronizar Dados", command=self.standardize_data, width=180, fg_color="#f4c27d", hover_color="#efb463", text_color="#382612", **common_button_opts)
        self.standardize_button.grid(row=0, column=3, padx=8, pady=10)

        self.theme_switch = ctk.CTkSwitch(self.button_frame, text="Modo Claro", command=self.toggle_mode, width=120, height=28, border_color="#9bb1d1", fg_color="#d6e4ff")
        self.theme_switch.grid(row=0, column=4, padx=15, pady=10)

        # LINHA 1 (5 botões)
        self.filter_column_button = ctk.CTkButton(self.button_frame, text="Filtrar Coluna", command=self.filter_column, width=140, fg_color="#8ab6ff", hover_color="#72a5ff", text_color="#0d1b2a", **common_button_opts)
        self.filter_column_button.grid(row=1, column=0, padx=6, pady=10)

        self.filter_row_button = ctk.CTkButton(self.button_frame, text="Filtrar Linha", command=self.filter_row, width=140, fg_color="#8ab6ff", hover_color="#72a5ff", text_color="#0d1b2a", **common_button_opts)
        self.filter_row_button.grid(row=1, column=1, padx=6, pady=10)

        self.undo_button = ctk.CTkButton(self.button_frame, text="Desfazer", command=self.undo_action, width=140, fg_color="#8ab6ff", hover_color="#72a5ff", text_color="#0d1b2a", **common_button_opts)
        self.undo_button.grid(row=1, column=2, padx=6, pady=10)

        self.save_button = ctk.CTkButton(self.button_frame, text="Salvar", command=self.save_file, width=140, fg_color="#7bd6a1", hover_color="#63c78f", text_color="#103022", **common_button_opts)
        self.save_button.grid(row=1, column=3, padx=6, pady=10)

        self.delete_column_button = ctk.CTkButton(self.button_frame, text="Excluir Coluna", command=self.delete_column, width=140, fg_color="#f3a6a6", hover_color="#ee8f8f", text_color="#3c1d1d", **common_button_opts)
        self.delete_column_button.grid(row=1, column=4, padx=6, pady=10)

        # Ajuste de expansão
        self.frame.grid_columnconfigure(0, weight=1)
        self.frame.grid_rowconfigure(0, weight=1)
        self.button_frame.grid_columnconfigure((0, 1, 2, 3, 4), weight=1)
    def _get_theme_colors(self):
        if self.is_dark_mode:
            return {
                "bg": "#111827",
                "panel": "#1d2433",
                "table_bg": "#202a3a",
                "heading": "#2c374d",
                "heading_active": "#3a4968",
                "text": "#edf2ff",
                "selected": "#7aa7ff",
                "border": "#394c72",
            }
        return {
            "bg": "#edf4ff",
            "panel": "#f8fbff",
            "table_bg": "#ffffff",
            "heading": "#e2ebff",
            "heading_active": "#d4e1ff",
            "text": "#1b263b",
            "selected": "#b8d1ff",
            "border": "#dfeaff",
        }

    def _apply_theme_colors(self):
        colors = self._get_theme_colors()
        self.root.configure(fg_color=colors["bg"])
        if hasattr(self, "frame"):
            self.frame.configure(fg_color=colors["panel"])
        if hasattr(self, "tree"):
            self.style.configure("Treeview",
                                background=colors["table_bg"],
                                foreground=colors["text"],
                                rowheight=30,
                                fieldbackground=colors["table_bg"],
                                bordercolor=colors["border"],
                                borderwidth=0)
            self.style.map("Treeview", background=[("selected", colors["selected"])])
            self.style.configure("Treeview.Heading",
                                background=colors["heading"],
                                foreground=colors["text"],
                                font=("Arial", 10, "bold"),
                                relief="flat",
                                padding=5)
            self.style.map("Treeview.Heading", background=[("active", colors["heading_active"])])

    def _start_horizontal_drag(self, event):
        self._horizontal_drag_active = True
        self._horizontal_drag_start_x = event.x
        self._horizontal_drag_start_scroll = float(self.tree.xview()[0])
        self._horizontal_drag_last_x = event.x
        self._horizontal_drag_velocity = 0.0
        if self._horizontal_drag_inertia_id is not None:
            self.root.after_cancel(self._horizontal_drag_inertia_id)
            self._horizontal_drag_inertia_id = None

    def _move_horizontal_drag(self, event):
        if not self._horizontal_drag_active:
            return

        delta_x = event.x - self._horizontal_drag_last_x
        self._horizontal_drag_last_x = event.x

        # Move com sensibilidade reduzida para parecer mais natural
        current_scroll = float(self.tree.xview()[0])
        target_scroll = current_scroll - (delta_x / max(self.tree.winfo_width(), 1)) * 1.4
        target_scroll = max(0.0, min(target_scroll, 1.0))
        self.tree.xview_moveto(target_scroll)

        # Inércia baseada no último deslocamento do drag
        self._horizontal_drag_velocity = (target_scroll - current_scroll) * 1.8

    def _stop_horizontal_drag(self, event):
        self._horizontal_drag_active = False
        self._horizontal_drag_velocity *= 0.7
        if abs(self._horizontal_drag_velocity) < 0.0005:
            self._horizontal_drag_velocity = 0.0
            return
        self._animate_horizontal_friction()

    def _animate_horizontal_friction(self):
        if abs(self._horizontal_drag_velocity) < 0.0005:
            self._horizontal_drag_velocity = 0.0
            self._horizontal_drag_inertia_id = None
            return

        current = float(self.tree.xview()[0])
        next_scroll = current + self._horizontal_drag_velocity
        next_scroll = max(0.0, min(next_scroll, 1.0))
        self.tree.xview_moveto(next_scroll)
        self._horizontal_drag_velocity *= 0.88
        self._horizontal_drag_inertia_id = self.root.after(16, self._animate_horizontal_friction)

    def _on_mouse_wheel_horizontal(self, event):
        try:
            delta = -event.delta / 120
        except AttributeError:
            delta = 0

        if delta == 0:
            return "break"

        current = float(self.tree.xview()[0])
        self.tree.xview_moveto(max(0.0, min(1.0, current + delta * 0.04)))
        return "break"

    def toggle_mode(self):
        if self.theme_switch.get() == 1:
            ctk.set_appearance_mode("light")
            self.is_dark_mode = False
            self.theme_switch.configure(text="Modo Escuro")
        else:
            ctk.set_appearance_mode("dark")
            self.is_dark_mode = True
            self.theme_switch.configure(text="Modo Claro")
        self._apply_theme_colors()

    def aplicar_estilo(self):
        # Aplica o estilo completo
        aplicar_estilo(self.root, self.is_dark_mode)

    # Método para carregar o arquivo CSV
    # Método para carregar arquivos (Agora com múltiplos formatos)
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
            try:
                # 2. Verifica a extensão para escolher o método certo do Pandas
                if file_path.endswith('.csv'):
                    self.data = pd.read_csv(file_path)
                elif file_path.endswith(('.xlsx', '.xls')):
                    self.data = pd.read_excel(file_path)
                elif file_path.endswith('.ods'):
                    self.data = pd.read_excel(file_path, engine="odf") # LibreOffice
                elif file_path.endswith('.json'):
                    self.data = pd.read_json(file_path)
                elif file_path.endswith('.pdf'):
                    messagebox.showwarning("Aviso", "Ainda não suportamos leitura de PDF. Escolha Excel ou CSV.")
                    return
                else:
                    messagebox.showerror("Erro", "Formato de arquivo não suportado.")
                    return

                # Limpa o histórico de ações ao carregar um arquivo novo (se você já adicionou o desfazer)
                if hasattr(self, 'data_history'):
                    self.data_history = [] 

                self.show_data()
                messagebox.showinfo("Sucesso", f"Arquivo carregado com sucesso!\n{self.data.shape[0]} linhas e {self.data.shape[1]} colunas.")
            except Exception as e:
                messagebox.showerror("Erro", f"Erro ao carregar o arquivo: {e}")
    def show_data(self):
        for i in self.tree.get_children():
            self.tree.delete(i)

        if self.data is not None and not self.data.empty:
            self.tree["columns"] = list(self.data.columns)
            self.tree["show"] = "headings"

            for column in self.tree["columns"]:
                self.tree.heading(column, text=column)

            for index, row in self.data.iterrows():
                self.tree.insert("", "end", values=list(row))
        else:
            messagebox.showwarning("Aviso", "Não há dados para mostrar.")

    # Método para preencher valores ausentes 
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

    # Método para remover duplicata
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

    # Método para filtrar dados por linha
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



    # Método para excluir uma coluna indesejada
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

    # Método para mostrar os dados na janela pop-up
    def show_popup(self, message):
        popup = Toplevel(self.root)
        popup.title("Resultado")
        popup.geometry("400x300")
        popup.resizable(True, True)
        label = tk.Label(popup, text=message, wraplength=350)
        label.pack(pady=20)
        ok_button = tk.Button(popup, text="OK", command=popup.destroy)
        ok_button.pack(pady=10)

    # Método para salvar o DataFrame em diferentes formatos
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

    # Método que centraliza a lógica de salvamento
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


    # Método para desfazer a última ação
    def undo_action(self):
        if self.data_history: # Verifica se existe algum histórico salvo
            # Pega o último estado salvo e remove da lista de histórico
            self.data = self.data_history.pop() 
            self.show_data() # Atualiza a tabela na tela
            messagebox.showinfo("Desfazer", "Última ação desfeita com sucesso!")
        else:
            messagebox.showwarning("Aviso", "Não há nenhuma ação para desfazer.")
