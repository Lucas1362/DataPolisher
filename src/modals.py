"""Modais e diálogos de ação da interface do DataPolisher.

Este módulo guarda todas as janelas flutuantes que alteram o estado do DataFrame
ou exibem informações contextuais relacionadas ao processamento dos dados.
Cada função atua como um bloco de funcionalidade isolado, mantendo a lógica do
app separada da tela principal.
"""

import tkinter as tk
from tkinter import messagebox

import customtkinter as ctk
import pandas as pd

import cleaner


def standardize_data(app):
    """Abre um modal para padronizar textos, escolhendo coluna e caso desejado."""
    if app.data is None:
        messagebox.showwarning("Aviso", "Carregue um arquivo primeiro.")
        return

    # Bloco de criação da janela principal do modal.
    modal = ctk.CTkToplevel(app.root)
    modal.title("Padronizar Dados")
    modal.geometry("440x250")
    modal.transient(app.root)
    modal.grab_set()
    modal.configure(fg_color="#f3f7ff")

    # Card container que organiza todos os controles visuais da operação.
    card = ctk.CTkFrame(modal, fg_color="#ffffff", corner_radius=20, border_width=1, border_color="#dfeaff")
    card.pack(fill=tk.BOTH, expand=True, padx=18, pady=18)

    title = ctk.CTkLabel(card, text="Padronizar texto", font=ctk.CTkFont(size=20, weight="bold"), text_color="#1b263b")
    title.pack(anchor="w", padx=20, pady=(18, 4))

    subtitle = ctk.CTkLabel(card, text="Escolha a coluna e o estilo de texto desejado.", font=ctk.CTkFont(size=12), text_color="#53627a")
    subtitle.pack(anchor="w", padx=20, pady=(0, 12))

    columns = ["Todas as colunas"] + list(app.data.columns)
    column_var = tk.StringVar(value=columns[0])
    case_var = tk.StringVar(value="minúsculas")

    column_selector = ctk.CTkOptionMenu(card, values=columns, variable=column_var, width=260, fg_color="#edf4ff", button_color="#f4c27d", button_hover_color="#efb463")
    column_selector.pack(padx=20, pady=(0, 12), fill=tk.X)

    case_selector = ctk.CTkOptionMenu(card, values=["minúsculas", "maiúsculas", "título"], variable=case_var, width=260, fg_color="#edf4ff", button_color="#8ab6ff", button_hover_color="#72a5ff")
    case_selector.pack(padx=20, pady=(0, 16), fill=tk.X)

    # Bloco de ação do modal: aplica a padronização e atualiza a tabela.
    def apply_standardization():
        selected_column = column_var.get()
        case_map = {
            "minúsculas": "lower",
            "maiúsculas": "upper",
            "título": "title",
        }
        target_case = case_map.get(case_var.get(), "lower")

        try:
            if hasattr(app, 'data_history'):
                app.data_history.append(app.data.copy())

            if selected_column == "Todas as colunas":
                app.data = cleaner.standardize_dataframe(app.data, case=target_case)
                message = "Todos os textos foram padronizados."
            else:
                app.data = cleaner.standardize_dataframe(app.data, column=selected_column, case=target_case)
                message = f"Coluna '{selected_column}' padronizada."

            app.show_data()
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


def filter_column(app):
    """Mantém apenas uma coluna selecionada e reapresenta a tabela atualizada."""
    if app.data is None:
        messagebox.showwarning("Aviso", "Carregue um arquivo primeiro.")
        return

    if app.data.empty or app.data.columns.empty:
        messagebox.showwarning("Aviso", "Não há colunas disponíveis para filtrar.")
        return

    # Bloco de criação do modal de filtro por coluna.
    modal = ctk.CTkToplevel(app.root)
    modal.title("Filtrar por Coluna")
    modal.geometry("420x240")
    modal.minsize(420, 220)
    modal.transient(app.root)
    modal.grab_set()
    modal.configure(fg_color="#f3f7ff")

    card = ctk.CTkFrame(modal, fg_color="#ffffff", corner_radius=20, border_width=1, border_color="#dfeaff")
    card.pack(fill=tk.BOTH, expand=True, padx=18, pady=18)

    title = ctk.CTkLabel(card, text="Filtrar por coluna", font=ctk.CTkFont(size=20, weight="bold"), text_color="#1b263b")
    title.pack(anchor="w", padx=20, pady=(18, 6))

    subtitle = ctk.CTkLabel(card, text="Escolha a coluna que deseja manter na tabela.", font=ctk.CTkFont(size=12), text_color="#53627a")
    subtitle.pack(anchor="w", padx=20, pady=(0, 12))

    columns = list(app.data.columns)
    selected = tk.StringVar(value=columns[0])
    combo = ctk.CTkOptionMenu(card, values=columns, variable=selected, width=260, fg_color="#edf4ff", button_color="#8ab6ff", button_hover_color="#72a5ff")
    combo.pack(padx=20, pady=(0, 16), fill=tk.X)

    # Bloco de atualização: registra o estado anterior, aplica o filtro e refaz a tabela.
    def apply_filter():
        column_name = selected.get()
        if not column_name or column_name not in app.data.columns:
            messagebox.showwarning("Atenção", "Coluna inválida.")
            return

        if hasattr(app, 'data_history'):
            app.data_history.append(app.data.copy())

        app.data = app.data[[column_name]]
        app.show_data()
        app.show_popup(f"Filtro aplicado! Mostrando apenas a coluna: {column_name}")
        modal.destroy()

    action_bar = ctk.CTkFrame(card, fg_color="transparent")
    action_bar.pack(fill=tk.X, padx=20, pady=(0, 18))

    cancel = ctk.CTkButton(action_bar, text="Cancelar", width=110, fg_color="#e6ecff", hover_color="#dfeaff", text_color="#1b263b", command=modal.destroy)
    cancel.pack(side=tk.LEFT)

    apply_btn = ctk.CTkButton(action_bar, text="Aplicar", width=110, fg_color="#7bd6a1", hover_color="#63c78f", text_color="#103022", command=apply_filter)
    apply_btn.pack(side=tk.RIGHT)


def filter_row(app):
    """Abre uma janela detalhada para visualizar uma linha específica da tabela."""
    if app.data is None:
        messagebox.showwarning("Aviso", "Carregue um arquivo primeiro.")
        return

    if app.data.empty:
        messagebox.showwarning("Aviso", "Não há linhas para filtrar.")
        return

    # Bloco de entrada para a linha alvo e criação da janela do modal.
    modal = ctk.CTkToplevel(app.root)
    modal.title("Filtrar por Linha")
    modal.geometry("420x260")
    modal.minsize(420, 230)
    modal.transient(app.root)
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

    # Bloco de apresentação da linha selecionada em uma janela secundária.
    def apply_filter():
        try:
            row_number = int(row_var.get())
        except ValueError:
            messagebox.showwarning("Atenção", "Digite um número válido para a linha.")
            return

        if not 1 <= row_number <= len(app.data):
            messagebox.showwarning("Atenção", "Número da linha inválido!")
            return

        row_data = app.data.iloc[row_number - 1]
        result_window = ctk.CTkToplevel(app.root)
        result_window.title(f"Linha {row_number}")
        result_window.geometry("500x340")
        result_window.resizable(True, True)
        result_window.transient(app.root)
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


def rename_column(app):
    """Modal para trocar o nome de uma coluna mantendo consistência no DataFrame."""
    if app.data is None:
        messagebox.showwarning("Aviso", "Carregue um arquivo primeiro.")
        return

    if app.data.empty or app.data.columns.empty:
        messagebox.showwarning("Aviso", "Não há colunas disponíveis para renomear.")
        return

    # Bloco de construção do modal de renomeação.
    modal = ctk.CTkToplevel(app.root)
    modal.title("Renomear Coluna")
    modal.geometry("440x270")
    modal.transient(app.root)
    modal.grab_set()
    modal.configure(fg_color="#f3f7ff")

    card = ctk.CTkFrame(modal, fg_color="#ffffff", corner_radius=20, border_width=1, border_color="#dfeaff")
    card.pack(fill=tk.BOTH, expand=True, padx=18, pady=18)

    title = ctk.CTkLabel(card, text="Renomear coluna", font=ctk.CTkFont(size=20, weight="bold"), text_color="#1b263b")
    title.pack(anchor="w", padx=20, pady=(18, 6))

    subtitle = ctk.CTkLabel(card, text="Escolha a coluna atual e informe o novo nome.", font=ctk.CTkFont(size=12), text_color="#53627a")
    subtitle.pack(anchor="w", padx=20, pady=(0, 12))

    columns = list(app.data.columns)
    selected_column = tk.StringVar(value=columns[0])
    new_name_var = tk.StringVar(value="")

    column_selector = ctk.CTkOptionMenu(card, values=columns, variable=selected_column, width=260, fg_color="#edf4ff", button_color="#8ab6ff", button_hover_color="#72a5ff")
    column_selector.pack(padx=20, pady=(0, 12), fill=tk.X)

    new_name_entry = ctk.CTkEntry(card, textvariable=new_name_var, width=260, placeholder_text="Novo nome da coluna")
    new_name_entry.pack(padx=20, pady=(0, 16), fill=tk.X)

    # Bloco de confirmação: valida nome, aplica a renomeação e atualiza a tabela.
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

        if new_name in app.data.columns and new_name != old_name:
            messagebox.showwarning("Atenção", f"O nome '{new_name}' já existe na tabela.")
            return

        if hasattr(app, 'data_history'):
            app.data_history.append(app.data.copy())

        app.data = app.data.rename(columns={old_name: new_name})
        app.show_data()
        messagebox.showinfo("Sucesso", f"Coluna '{old_name}' renomeada para '{new_name}'.")
        modal.destroy()

    action_bar = ctk.CTkFrame(card, fg_color="transparent")
    action_bar.pack(fill=tk.X, padx=20, pady=(0, 18))

    cancel = ctk.CTkButton(action_bar, text="Cancelar", width=110, fg_color="#e6ecff", hover_color="#dfeaff", text_color="#1b263b", command=modal.destroy)
    cancel.pack(side=tk.LEFT)

    apply_btn = ctk.CTkButton(action_bar, text="Salvar", width=110, fg_color="#7bd6a1", hover_color="#63c78f", text_color="#103022", command=apply_rename)
    apply_btn.pack(side=tk.RIGHT)
