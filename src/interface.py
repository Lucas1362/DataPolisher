import flet as ft
import pandas as pd
import cleaner
import modals

class DataCleanerApp(ft.Column):
    def __init__(self, page: ft.Page):
        super().__init__(expand=True, spacing=15)
        self._page = page
        self.data = None
        self.data_history = []

        self.file_picker = ft.FilePicker()
        self.save_picker = ft.FilePicker()
        self._page.overlay.append(self.file_picker)
        self._page.overlay.append(self.save_picker)

        self.data_table = ft.DataTable(columns=[], rows=[], expand=True)
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
                ft.ElevatedButton("Carregar Arquivo", icon=ft.icons.UPLOAD, on_click=self.pick_file),
                ft.ElevatedButton("Remover Duplicatas", icon=ft.icons.DELETE, on_click=self.remove_duplicates),
                ft.ElevatedButton("Preencher Nulos", icon=ft.icons.EDIT, on_click=lambda e: modals.open_fill_na_modal(self)),
                ft.ElevatedButton("Padronizar", icon=ft.icons.TEXT_FORMAT, on_click=lambda e: modals.open_standardize_modal(self)),
            ],
            spacing=10
        )
        linha_2 = ft.Row(
            controls=[
                ft.ElevatedButton("Renomear Coluna", icon=ft.icons.EDIT_ATTRIBUTES, on_click=lambda e: modals.open_rename_modal(self)),
                ft.ElevatedButton("Desfazer", icon=ft.icons.UNDO, on_click=self.undo_action),
                ft.ElevatedButton("Salvar", icon=ft.icons.SAVE, bgcolor=ft.colors.BLUE_900, color=ft.colors.WHITE, on_click=self.save_file),
            ],
            spacing=10
        )
        return ft.Column([linha_1, linha_2], spacing=10)
    def _build_table(self):
        return ft.Container(
            content=ft.Column([self.data_table], scroll=ft.ScrollMode.ALWAYS),
            bgcolor=ft.Colors.WHITE,
            border_radius=15,
            padding=10,
            expand=True, # Ocupa todo o espaço restante
            shadow=ft.BoxShadow(blur_radius=10, color=ft.Colors.BLACK12)
        )

    def pick_file(self, _):
        files = self.file_picker.pick_files(
            allowed_extensions=["csv", "xlsx", "xls", "ods", "json"],
            allow_multiple=False,
        )
        if files:
            self.load_file_path(files[0].path)

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

    def save_file(self, _):
        if self.data is None:
            self.show_snack_bar("Carregue um arquivo primeiro.")
            return
        path = self.save_picker.save_file(file_name="dados_limpos.csv")
        if not path:
            return
        try:
            if path.lower().endswith((".xlsx", ".xls")):
                self.data.to_excel(path, index=False)
            else:
                self.data.to_csv(path, index=False)
            self.show_snack_bar("Arquivo salvo com sucesso!")
        except Exception as exc:
            self.show_snack_bar(f"Erro ao salvar arquivo: {exc}")

    def update_table_view(self):
        """Atualiza a interface da tabela com os dados do Pandas."""
        if self.data is not None:
            # Pega as primeiras 100 linhas para não travar a UI (padrão de ferramentas de dados)
            preview_data = self.data.head(100)

            self.data_table.columns = [ft.DataColumn(ft.Text(str(col), weight=ft.FontWeight.BOLD)) for col in preview_data.columns]
            self.data_table.rows = [
                ft.DataRow(cells=[ft.DataCell(ft.Text(str(val))) for val in row])
                for row in preview_data.values
            ]
            self.data_table.update()

    def remove_duplicates(self, e):
        """Utiliza o seu módulo cleaner.py exatamente como era antes."""
        if self.data is not None:
            self.data_history.append(self.data.copy())
            original_len = len(self.data)

            # Chama a sua função original sem mexer nela!
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
        self.page.snack_bar = ft.SnackBar(ft.Text(text))
        self.page.snack_bar.open = True
        self.page.update()