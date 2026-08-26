import flet as ft
import pandas as pd
import tkinter as tk
from tkinter import filedialog
import cleaner
import modals

class DataCleanerApp(ft.Column):
    def __init__(self, page: ft.Page):
        super().__init__(expand=True, spacing=15)
        self._page = page
        self.data = None
        self.data_history = []

        # Tabela inicia com a mensagem de aguardando
        self.data_table = ft.DataTable(
            columns=[ft.DataColumn(ft.Text("Nenhum arquivo carregado"))],
            rows=[],
            expand=True,
        )
        self.controls = [self._build_header(), self._build_toolbar(), self._build_table()]

    def _build_header(self):
        return ft.Row(
            controls=[
                ft.Text("DataPolisher Studio", size=28, weight=ft.FontWeight.BOLD, color=ft.Colors.BLUE_900),
                ft.Text("Higienização inteligente de dados", size=14, italic=True, color=ft.Colors.GREY_600),
            ],
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN
        )

    def _build_toolbar(self):
        linha_1 = ft.Row(
            controls=[
                ft.ElevatedButton("Carregar Arquivo", icon="file_upload", on_click=self.pick_file),
                ft.ElevatedButton("Remover Duplicatas", icon="delete", on_click=self.remove_duplicates),
                ft.ElevatedButton("Preencher Nulos", icon="edit", on_click=lambda e: modals.open_fill_na_modal(self)),
                ft.ElevatedButton("Padronizar", icon="text_format", on_click=lambda e: modals.open_standardize_modal(self)),
            ],
            spacing=10
        )
        linha_2 = ft.Row(
            controls=[
                ft.ElevatedButton("Renomear Coluna", icon="edit_attributes", on_click=lambda e: modals.open_rename_modal(self)),
                ft.ElevatedButton("Desfazer", icon="undo", on_click=self.undo_action),
                ft.ElevatedButton("Salvar", icon="save", bgcolor=ft.Colors.BLUE_900, color=ft.Colors.WHITE, on_click=self.save_file),
            ],
            spacing=10
        )
        return ft.Column([linha_1, linha_2], spacing=10)

    def _build_table(self):
        return ft.Container(
            # O segredo do scroll duplo no Flet:
            # Uma Row (scroll horizontal) dentro de uma Column (scroll vertical)
            content=ft.Column(
                controls=[
                    ft.Row(
                        controls=[self.data_table], 
                        scroll=ft.ScrollMode.ALWAYS,
                        expand=True
                    )
                ], 
                scroll=ft.ScrollMode.ALWAYS,
                expand=True
            ),
            bgcolor=ft.Colors.WHITE,
            border_radius=15,
            padding=10,
            expand=True,
            shadow=ft.BoxShadow(blur_radius=30, color=ft.Colors.BLACK12)
        )

    # --- COMUNICAÇÃO NATIVA COM O WINDOWS (Substitui o Flet FilePicker) ---
    def pick_file(self, _):
        root = tk.Tk()
        root.withdraw() # Esconde a janelinha base do Tkinter
        root.attributes('-topmost', True) # Força a janela a abrir na frente do app
        
        file_path = filedialog.askopenfilename(
            title="Selecione o arquivo de dados",
            filetypes=[("Planilhas e Dados", "*.csv *.xlsx *.xls *.ods *.json")]
        )
        root.destroy() # Encerra o processo do Tkinter imediatamente
        
        if file_path:
            self.load_file_path(file_path)

    def save_file(self, _):
        if self.data is None:
            self.show_snack_bar("Carregue um arquivo primeiro.")
            return
            
        root = tk.Tk()
        root.withdraw()
        root.attributes('-topmost', True)
        
        file_path = filedialog.asksaveasfilename(
            defaultextension=".csv",
            title="Salvar dados limpos",
            initialfile="dados_limpos.csv",
            filetypes=[("CSV", "*.csv"), ("Excel", "*.xlsx")]
        )
        root.destroy()
        
        if file_path:
            try:
                if file_path.lower().endswith((".xlsx", ".xls")):
                    self.data.to_excel(file_path, index=False)
                else:
                    self.data.to_csv(file_path, index=False)
                self.show_snack_bar("Arquivo salvo com sucesso!")
            except Exception as exc:
                self.show_snack_bar(f"Erro ao salvar arquivo: {exc}")

    # --- LÓGICA CONECTADA AO SEU CLEANER.PY ---
    def load_file_path(self, file_path):
        try:
            extension = file_path.lower().rsplit(".", 1)[-1]
            if extension == "csv":
                self.data = pd.read_csv(file_path)
            elif extension in ("xlsx", "xls"):
                self.data = pd.read_excel(file_path)
            elif extension == "ods":
                self.data = pd.read_excel(file_path, engine="odf")
            elif extension == "json":
                self.data = pd.read_json(file_path)
            else:
                raise ValueError("Formato de arquivo não suportado")

            self.data_history = []
            self.update_table_view()
            self.show_snack_bar("Arquivo carregado com sucesso!")
        except Exception as exc:
            self.show_snack_bar(f"Erro ao ler arquivo: {exc}")

    def update_table_view(self):
        if self.data is not None:
            preview_data = self.data.head(100)
            columns = [
                ft.DataColumn(ft.Text(str(col), weight=ft.FontWeight.BOLD))
                for col in preview_data.columns
            ]
            self.data_table.columns = columns or [ft.DataColumn(ft.Text("Nenhum dado"))]
            self.data_table.rows = [
                ft.DataRow(cells=[ft.DataCell(ft.Text(str(val))) for val in row])
                for row in preview_data.values
            ]
            self._page.update()

    def remove_duplicates(self, e):
        if self.data is not None:
            self.data_history.append(self.data.copy())
            original_len = len(self.data)
            self.data = cleaner.remove_duplicates(self.data)
            new_len = len(self.data)
            self.update_table_view()
            self.show_snack_bar(f"{original_len - new_len} duplicatas removidas!")

    def undo_action(self, e):
        if self.data_history:
            self.data = self.data_history.pop()
            self.update_table_view()
            self.show_snack_bar("Última ação desfeita.")

    def show_snack_bar(self, text):
        self._page.snack_bar = ft.SnackBar(ft.Text(text))
        self._page.snack_bar.open = True
        self._page.update()