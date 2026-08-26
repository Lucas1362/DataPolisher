import flet as ft
import cleaner

def open_standardize_modal(app):
    if app.data is None:
        app.show_snack_bar("Carregue um arquivo primeiro.")
        return

    columns = ["Todas as colunas"] + list(app.data.columns)
    col_dropdown = ft.Dropdown(options=[ft.dropdown.Option(c) for c in columns], value=columns[0], label="Coluna")
    case_dropdown = ft.Dropdown(
        options=[ft.dropdown.Option("minúsculas"), ft.dropdown.Option("maiúsculas"), ft.dropdown.Option("título")], 
        value="minúsculas", label="Formato"
    )

    def apply(e):
        val_col = col_dropdown.value
        val_case = case_dropdown.value
        case_map = {"minúsculas": "lower", "maiúsculas": "upper", "título": "title"}
        target_case = case_map.get(val_case, "lower")

        app.data_history.append(app.data.copy())
        if val_col == "Todas as colunas":
            app.data = cleaner.standardize_dataframe(app.data, case=target_case)
        else:
            app.data = cleaner.standardize_dataframe(app.data, column=val_col, case=target_case)

        app.update_table_view()
        app.show_snack_bar("Dados padronizados com sucesso!")
        close_dialog(e)

    def close_dialog(e):
        app.app_page.pop_dialog()

    dialog = ft.AlertDialog(
        title=ft.Text("Padronizar Dados", weight=ft.FontWeight.BOLD),
        content=ft.Column([ft.Text("Escolha a coluna e o estilo de texto desejado:"), col_dropdown, case_dropdown], tight=True),
        actions=[
            ft.TextButton("Cancelar", on_click=close_dialog),
            ft.ElevatedButton("Aplicar", on_click=apply, bgcolor=ft.Colors.GREEN_600, color=ft.Colors.WHITE)
        ],
    )
    app.app_page.show_dialog(dialog)

def open_rename_modal(app):
    if app.data is None:
        app.show_snack_bar("Carregue um arquivo primeiro.")
        return

    columns = list(app.data.columns)
    col_dropdown = ft.Dropdown(options=[ft.dropdown.Option(c) for c in columns], value=columns[0], label="Coluna Atual")
    new_name_field = ft.TextField(label="Novo nome da coluna")

    def apply(e):
        old_name = col_dropdown.value
        new_name = new_name_field.value.strip()
        
        if not new_name or new_name in app.data.columns:
            app.show_snack_bar("Nome inválido ou já existe.")
            return

        app.data_history.append(app.data.copy())
        app.data = app.data.rename(columns={old_name: new_name})
        app.update_table_view()
        app.show_snack_bar(f"Coluna renomeada para '{new_name}'.")
        close_dialog(e)

    def close_dialog(e):
        app.app_page.pop_dialog()

    dialog = ft.AlertDialog(
        title=ft.Text("Renomear Coluna", weight=ft.FontWeight.BOLD),
        content=ft.Column([col_dropdown, new_name_field], tight=True),
        actions=[
            ft.TextButton("Cancelar", on_click=close_dialog),
            ft.ElevatedButton("Salvar", on_click=apply, bgcolor=ft.Colors.BLUE_900, color=ft.Colors.WHITE)
        ],
    )
    app.app_page.show_dialog(dialog)

def open_fill_na_modal(app):
    if app.data is None:
        app.show_snack_bar("Carregue um arquivo primeiro.")
        return

    columns = ["Todas as colunas"] + list(app.data.columns)
    col_dropdown = ft.Dropdown(options=[ft.dropdown.Option(c) for c in columns], value="Todas as colunas", label="Coluna Alvo")
    value_field = ft.TextField(label="Valor para preencher (ex: 0, Não Informado)")

    def apply(e):
        val_col = col_dropdown.value
        val = value_field.value.strip()
        if not val:
            return
            
        try: val = float(val) if '.' in val else int(val)
        except ValueError: pass

        app.data_history.append(app.data.copy())
        target_col = None if val_col == "Todas as colunas" else val_col
        app.data = cleaner.fill_na_intelligent(app.data, val, target_col)
        
        app.update_table_view()
        app.show_snack_bar("Valores nulos preenchidos!")
        close_dialog(e)

    def close_dialog(e):
        app.app_page.pop_dialog()

    dialog = ft.AlertDialog(
        title=ft.Text("Preencher Nulos", weight=ft.FontWeight.BOLD),
        content=ft.Column([col_dropdown, value_field], tight=True),
        actions=[
            ft.TextButton("Cancelar", on_click=close_dialog),
            ft.ElevatedButton("Aplicar", on_click=apply, bgcolor=ft.Colors.GREEN_600, color=ft.Colors.WHITE)
        ],
    )
    app.app_page.show_dialog(dialog)