import pandas as pd
import tkinter as tk
from tkinter import filedialog, messagebox, Toplevel, ttk

class DataCleanerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Data Cleaner")
        self.data = None  # Inicializa o DataFrame como None
        self.original_data = None  # Armazena a tabela original

        # Botão para carregar o arquivo
        self.load_button = tk.Button(root, text="Carregar Arquivo CSV", command=self.load_file)
        self.load_button.pack(pady=10)

        # Botão para visualizar a tabela original
        self.view_original_button = tk.Button(root, text="Visualizar Tabela Original", command=self.view_original_data)
        self.view_original_button.pack(pady=10)

        # Botão para remover duplicatas
        self.remove_duplicates_button = tk.Button(root, text="Remover Duplicatas", command=self.remove_duplicates)
        self.remove_duplicates_button.pack(pady=10)

        # Botão para preencher valores ausentes
        self.fill_na_button = tk.Button(root, text="Preencher Valores Ausentes", command=self.fill_na)
        self.fill_na_button.pack(pady=10)

        # Botão para visualizar a tabela limpa
        self.view_clean_button = tk.Button(root, text="Visualizar Tabela Limpa", command=self.view_clean_data)
        self.view_clean_button.pack(pady=10)

        # Campos de entrada para filtragem
        self.filter_column_entry = tk.Entry(root, width=30)
        self.filter_column_entry.pack(pady=5)
        self.filter_column_entry.insert(0, "Nome da Coluna para Filtrar")

        # Botão para filtrar os dados por coluna
        self.filter_button = tk.Button(root, text="Visualizar Todos os Dados da Coluna", command=self.filter_data)
        self.filter_button.pack(pady=10)

        # Botão para salvar o arquivo CSV
        self.save_csv_button = tk.Button(root, text="Salvar Arquivo Limpo como CSV", command=self.save_file)
        self.save_csv_button.pack(pady=10)

        # Botão para salvar o arquivo Excel
        self.save_excel_button = tk.Button(root, text="Salvar Arquivo Limpo como Excel", command=self.save_excel)
        self.save_excel_button.pack(pady=10)

    def load_file(self):
        file_path = filedialog.askopenfilename(filetypes=[("CSV Files", "*.csv")])
        if file_path:
            try:
                self.original_data = pd.read_csv(file_path)
                self.data = self.original_data.copy()  # Copia os dados para data
                messagebox.showinfo("Sucesso", "Arquivo carregado com sucesso!")
                print(self.data.head())
            except Exception as e:
                messagebox.showerror("Erro", f"Erro ao carregar o arquivo: {e}")

    def view_original_data(self):
        if self.original_data is not None:
            self.show_data(self.original_data, title="Tabela Original")
        else:
            messagebox.showwarning("Aviso", "Nenhum arquivo carregado.")

    def view_clean_data(self):
        if self.data is not None:
            self.show_data(self.data, title="Tabela Limpa")
        else:
            messagebox.showwarning("Aviso", "Nenhum arquivo carregado.")

    def show_data(self, data, title):
        window = Toplevel(self.root)
        window.title(title)
        tree = ttk.Treeview(window)
        
        # Adiciona colunas ao Treeview
        tree["columns"] = list(data.columns)
        tree["show"] = "headings"
        
        for column in data.columns:
            tree.heading(column, text=column)
            tree.column(column, width=100)  # Define largura das colunas
        
        # Adiciona os dados ao Treeview
        for index, row in data.iterrows():
            tree.insert("", "end", values=list(row))
        
        tree.pack(expand=True, fill='both')
        window.geometry("600x400")  # Define tamanho da janela

    def remove_duplicates(self):
        if self.data is not None:
            before_count = len(self.data)
            self.data = self.data.drop_duplicates()
            after_count = len(self.data)
            messagebox.showinfo("Sucesso", f"Duplicatas removidas! {before_count - after_count} duplicatas encontradas.")
        else:
            messagebox.showwarning("Aviso", "Nenhum arquivo carregado.")

    def fill_na(self):
        if self.data is not None:
            self.data.fillna('Não disponível', inplace=True)
            messagebox.showinfo("Sucesso", "Valores ausentes preenchidos!")
        else:
            messagebox.showwarning("Aviso", "Nenhum arquivo carregado.")

    def filter_data(self):
        if self.data is not None:
            column_name = self.filter_column_entry.get().strip()

            if column_name in self.data.columns:
                # Filtra os dados para mostrar apenas a coluna desejada
                filtered_data = self.data[[column_name]]
                self.show_data(filtered_data, title=f"Dados da Coluna: {column_name}")
            else:
                messagebox.showwarning("Aviso", f"A coluna '{column_name}' não existe.")
        else:
            messagebox.showwarning("Aviso", "Nenhum arquivo carregado.")

    def save_file(self):
        if self.data is not None:
            file_path = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV Files", "*.csv")])
            if file_path:
                self.data.to_csv(file_path, index=False)
                messagebox.showinfo("Sucesso", "Arquivo salvo como CSV com sucesso!")
        else:
            messagebox.showwarning("Aviso", "Nenhum arquivo carregado.")

    def save_excel(self):
        if self.data is not None:
            file_path = filedialog.asksaveasfilename(defaultextension=".xlsx", filetypes=[("Excel Files", "*.xlsx")])
            if file_path:
                self.data.to_excel(file_path, index=False)  # Salva o DataFrame em um arquivo Excel
                messagebox.showinfo("Sucesso", "Arquivo salvo como Excel com sucesso!")
        else:
            messagebox.showwarning("Aviso", "Nenhum arquivo carregado.")

if __name__ == "__main__":
    root = tk.Tk()
    app = DataCleanerApp(root)
    root.mainloop()
