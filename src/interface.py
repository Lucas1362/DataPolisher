import flet as ft
import pandas as pd
import tkinter as tk
from tkinter import filedialog
import cleaner
import modals

class DataCleanerApp(ft.Column):
    def __init__(self, page: ft.Page):
        super().__init__(expand=True, spacing=0)
        self.app_page = page  # Alterado de self.page para self.app_page
        self.data = None
        self.data_history = []

        self.data_table = ft.DataTable(
            columns=[ft.DataColumn(ft.Text("Nenhum arquivo carregado"))],
            rows=[]
        )

        # Estrutura limpa dividida em blocos independentes
        self.controls = [
            self._build_header(),
            ft.Divider(height=15, color="transparent"),
            self._build_toolbar(),
            ft.Divider(height=15, color="transparent"),
            self._build_table() # A tabela fica isolada no seu próprio retângulo
        ]

    def _build_header(self):
        return ft.Container(
            content=ft.Row(
                controls=[
                    ft.Text("DataPolisher Studio", size=26, weight=ft.FontWeight.BOLD, color=ft.Colors.BLUE_900),
                    ft.Text("Higienização inteligente de dados", size=13, italic=True, color=ft.Colors.GREY_600),
                ],
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN
            ),
            padding=10 # Valor numérico direto, compatível com qualquer versão do Flet
        )

    def _build_toolbar(self):
        estilo_botao = ft.ButtonStyle(
            shape=ft.RoundedRectangleBorder(radius=3),
            elevation={
                "pressed": 2,
                "": 5,
                "hover": 8,
                
            },
            padding=12
        )

        # Todos os botões concentrados em uma única linha (Row) com espaçamento limpo
        return ft.Container(
            content=ft.Row(
                controls=[
                    ft.ElevatedButton("Carregar Arquivo", icon=ft.Icons.FILE_UPLOAD, on_click=self.pick_file, style=estilo_botao),
                    ft.ElevatedButton("Remover Duplicatas", icon=ft.Icons.DELETE, on_click=self.remove_duplicates, style=estilo_botao),
                    ft.ElevatedButton("Preencher Nulos", icon=ft.Icons.EDIT, on_click=lambda e: modals.open_fill_na_modal(self), style=estilo_botao),
                    ft.ElevatedButton("Padronizar", icon="text_format", on_click=lambda e: modals.open_standardize_modal(self), style=estilo_botao),
                    ft.ElevatedButton("Renomear Coluna", icon="edit_attributes", on_click=lambda e: modals.open_rename_modal(self), style=estilo_botao),
                    ft.ElevatedButton("Desfazer", icon="undo", on_click=self.undo_action, style=estilo_botao),
                    ft.ElevatedButton("Salvar", icon=ft.Icons.SAVE, bgcolor=ft.Colors.BLUE_900, color=ft.Colors.WHITE, on_click=self.save_file, style=estilo_botao),
                ],
                spacing=2,
                alignment=ft.MainAxisAlignment.START,
                
                wrap=True # Garante que se faltar espaço, eles quebram para a linha de baixo automaticamente em vez de dar erro
            ),
            padding=5
        )

    def _build_table(self):
        # Isola o scroll duplo estritamente dentro do retângulo da tabela
        tabela_com_scroll = ft.Row(
            controls=[
                ft.Column(
                    controls=[self.data_table],
                    scroll=ft.ScrollMode.ALWAYS,
                )
            ],
            scroll=ft.ScrollMode.ALWAYS,
            expand=True
        )

        return ft.Container(
            content=tabela_com_scroll,
            bgcolor=ft.Colors.WHITE,
            border_radius=15,
            padding=15,
            expand=True, # O retângulo expande apenas aqui, sem afetar o topo
            shadow=ft.BoxShadow(blur_radius=10, color=ft.Colors.BLACK12)
        )

    def pick_file(self, _):
        root = tk.Tk()
        root.withdraw()
        root.attributes('-topmost', True)
        
        file_path = filedialog.askopenfilename(
            title="Selecione o arquivo de dados",
            filetypes=[("Planilhas e Dados", "*.csv *.xlsx *.xls *.ods *.json")]
        )
        root.destroy()
        
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
            self.app_page.update()

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
        snack_bar = ft.SnackBar(ft.Text(text))
        self.app_page.overlay.append(snack_bar)
        snack_bar.open = True
        self.app_page.update()