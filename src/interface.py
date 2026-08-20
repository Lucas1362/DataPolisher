# interface.py
import tkinter as tk
from tkinter import filedialog, messagebox, simpledialog, Toplevel
from estilo import aplicar_estilo
from tkinter import ttk
import pandas as pd
import matplotlib.pyplot as plt

class DataCleanerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Data Cleaner")  # Define o título da janela
        self.root.iconbitmap("D:\\vscode\\DataPolisher\\i.asidj\\iconeData1.ico")  # Adiciona o ícone à janela
        self.data = None
        self.is_dark_mode = False  # Inicializa o modo escuro como False

        # Frame para a tabela
        self.frame = tk.Frame(root)
        self.frame.pack(pady=10, fill=tk.BOTH, expand=True)

        # Configuração da tabela de visualização
        self.tree = ttk.Treeview(self.frame)
        self.tree.grid(row=0, column=0, sticky='nsew')

        # Barras de rolagem
        self.scrollbar_y = ttk.Scrollbar(self.frame, orient="vertical", command=self.tree.yview)
        self.scrollbar_y.grid(row=0, column=1, sticky='ns')

        self.scrollbar_x = ttk.Scrollbar(root, orient="horizontal", command=self.tree.xview)
        self.scrollbar_x.pack(side=tk.BOTTOM, fill=tk.X)

        # Configura a tabela para usar as barras de rolagem
        self.tree.configure(yscrollcommand=self.scrollbar_y.set, xscrollcommand=self.scrollbar_x.set)

        # Frame para os botões
        self.button_frame = tk.Frame(root)
        self.button_frame.pack(pady=10, fill=tk.X)

        # Botões da interface
        self.load_button = tk.Button(self.button_frame, text="Carregar Arquivo CSV", command=self.load_file)
        self.load_button.grid(row=0, column=0, padx=5, pady=5, sticky='ew')

        self.remove_duplicates_button = tk.Button(self.button_frame, text="Remover Duplicatas", command=self.remove_duplicates)
        self.remove_duplicates_button.grid(row=1, column=0, padx=5, pady=5, sticky='ew')

        self.fill_na_button = tk.Button(self.button_frame, text="Preencher Valores Ausentes", command=self.fill_na)
        self.fill_na_button.grid(row=2, column=0, padx=5, pady=5, sticky='ew')

        self.filter_column_button = tk.Button(self.button_frame, text="Filtrar Dados por Coluna", command=self.filter_column)
        self.filter_column_button.grid(row=3, column=0, padx=5, pady=5, sticky='ew')

        self.filter_row_button = tk.Button(self.button_frame, text="Filtrar Dados por Linha", command=self.filter_row)
        self.filter_row_button.grid(row=4, column=0, padx=5, pady=5, sticky='ew')

        self.save_button = tk.Button(self.button_frame, text="Salvar Arquivo Limpo", command=self.save_file)
        self.save_button.grid(row=5, column=0, padx=5, pady=5, sticky='ew')

        # Botão para alternar entre modos
        self.toggle_mode_button = tk.Button(self.button_frame, text="Alternar Modo", command=self.toggle_mode)
        self.toggle_mode_button.grid(row=6, column=0, padx=5, pady=5, sticky='ew')

        # Configura a coluna e linha para expandir
        self.frame.grid_columnconfigure(0, weight=1)
        self.frame.grid_rowconfigure(0, weight=1)
        self.button_frame.grid_columnconfigure(0, weight=1)  # Para os botões

        self.aplicar_estilo()  # Aplica o estilo inicial

    # Método para alternar entre modos
    def toggle_mode(self):
        self.is_dark_mode = not self.is_dark_mode  # Alterna o modo
        self.aplicar_estilo()  # Aplica o novo estilo

    def aplicar_estilo(self):
        # Aplica o estilo completo
        aplicar_estilo(self.root, self.is_dark_mode)

    # Método para carregar o arquivo CSV
    def load_file(self):
        file_path = filedialog.askopenfilename(filetypes=[("CSV files", "*.csv")])
        if file_path:
            try:
                self.data = pd.read_csv(file_path)
                self.show_data()
                messagebox.showinfo("Sucesso", "Arquivo carregado com sucesso!")
            except Exception as e:
                messagebox.showerror("Erro", f"Erro ao carregar o arquivo: {e}")

    # Método para mostrar os dados na Treeview
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

    # Método para remover duplicatas
    def remove_duplicates(self):
        if self.data is not None:
            original_length = len(self.data)
            self.data.drop_duplicates(inplace=True)
            new_length = len(self.data)
            if new_length < original_length:
                self.show_data()
                self.show_popup(f"Duplicatas removidas: {original_length - new_length} entradas.")
            else:
                self.show_popup("Nenhuma duplicata encontrada.")
        else:
            messagebox.showwarning("Aviso", "Carregue um arquivo primeiro.")

    # Método para preencher valores ausentes
    def fill_na(self):
        if self.data is not None:
            if self.data.isnull().values.any():
                # Pergunta ao usuário qual texto usar para os valores ausentes
                replacement_text = simpledialog.askstring("Substituir valores ausentes", 
                                                        "Digite o texto para substituir todos os valores ausentes:")

                # Preencher todos os valores ausentes em todo o DataFrame
                self.data.fillna(replacement_text, inplace=True)

                self.show_data()
                self.show_popup("Todos os valores ausentes foram preenchidos.")
            else:
                self.show_popup("Nenhum valor ausente encontrado no DataFrame.")
        else:
            messagebox.showwarning("Aviso", "Carregue um arquivo primeiro.")

    # Método para filtrar dados por coluna
    def filter_column(self):
        column_name = simpledialog.askstring("Filtrar por Coluna", "Digite o nome da coluna:")
        
        if column_name is not None and column_name in self.data.columns:
            column_data = self.data[column_name]
            result_window = tk.Toplevel(self.root)
            result_window.title("Resultado do Filtro por Coluna")
            frame = tk.Frame(result_window)
            frame.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

            label = tk.Label(frame, text=f"Coluna: {column_name}", font=("Arial", 14, "bold"))
            label.pack(anchor="w")

            text_box = tk.Text(frame, wrap=tk.WORD)
            text_box.pack(fill=tk.BOTH, expand=True)

            for index, value in enumerate(column_data):
                if pd.isna(value):
                    value = "Dados não disponíveis"
                text_box.insert(tk.END, f"Linha {index + 1}: {value}\n")

            text_box.config(state=tk.DISABLED)

            close_button = tk.Button(frame, text="Fechar", command=result_window.destroy)
            close_button.pack(pady=5)
        else:
            messagebox.showwarning("Atenção", "Nome da coluna inválido!")

    # Método para filtrar dados por linha
    def filter_row(self):
        row_number = simpledialog.askinteger("Filtrar por linha", "Digite o número da linha:")
        
        if row_number is not None and 1 <= row_number <= len(self.data):
            row_data = self.data.iloc[row_number - 1]
            result_window = tk.Toplevel(self.root)
            result_window.title("Resultado do Filtro por Linha")
            frame = tk.Frame(result_window)
            frame.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

            label = tk.Label(frame, text=f"Linha {row_number}:", font=("Arial", 14, "bold"))
            label.pack(anchor="w")

            text_box = tk.Text(frame, wrap=tk.WORD)
            text_box.pack(fill=tk.BOTH, expand=True)

            for column, value in row_data.items():
                if pd.isna(value):
                    value = "Dados não disponíveis"
                text_box.insert(tk.END, f"{column}: {value}\n")

            text_box.config(state=tk.DISABLED)

            close_button = tk.Button(frame, text="Fechar", command=result_window.destroy)
            close_button.pack(pady=5)
        else:
            messagebox.showwarning("Atenção", "Número da linha inválido!")

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

# Executar a aplicação
if __name__ == "__main__":
    root = tk.Tk()
    app = DataCleanerApp(root)
    root.mainloop()