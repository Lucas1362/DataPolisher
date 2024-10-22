# cleaner.py
import pandas as pd
import tkinter as tk
from tkinter import filedialog, messagebox, simpledialog
from tkinter import ttk

class DataCleanerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Data Cleaner")
        self.data = None  # Inicializa o DataFrame como None

        # Frame para a tabela e barra de rolagem
        self.frame = tk.Frame(root)
        self.frame.pack(pady=10)

        # Configuração da tabela de visualização
        self.tree = ttk.Treeview(self.frame)
        self.tree.pack(side=tk.LEFT)

        # Barra de rolagem vertical
        self.scrollbar = ttk.Scrollbar(self.frame, orient="vertical", command=self.tree.yview)
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Configura a tabela para usar a barra de rolagem
        self.tree.configure(yscrollcommand=self.scrollbar.set)

        # Botões da interface
        self.load_button = tk.Button(root, text="Carregar Arquivo CSV", command=self.load_file)
        self.load_button.pack(pady=10)

        self.remove_duplicates_button = tk.Button(root, text="Remover Duplicatas", command=self.remove_duplicates)
        self.remove_duplicates_button.pack(pady=10)

        self.fill_na_button = tk.Button(root, text="Preencher Valores Ausentes", command=self.fill_na)
        self.fill_na_button.pack(pady=10)

        self.filter_button = tk.Button(root, text="Filtrar Dados por Coluna", command=self.filter_data)
        self.filter_button.pack(pady=10)

        self.save_csv_button = tk.Button(root, text="Salvar Arquivo Limpo como CSV", command=self.save_file)
        self.save_csv_button.pack(pady=10)

        self.save_excel_button = tk.Button(root, text="Salvar Arquivo Limpo como Excel", command=self.save_excel)
        self.save_excel_button.pack(pady=10)

    def load_file(self):
        file_path = filedialog.askopenfilename(filetypes=[("CSV Files", "*.csv")])
        if file_path:
            try:
                self.data = pd.read_csv(file_path)
                messagebox.showinfo("Sucesso", "Arquivo carregado com sucesso!")
                self.display_data()  # Exibir os dados carregados
            except Exception as e:
                messagebox.showerror("Erro", f"Erro ao carregar o arquivo: {e}")

    def display_data(self):
        # Limpa a tabela antes de exibir novos dados
        for i in self.tree.get_children():
            self.tree.delete(i)

        # Configura as colunas da tabela
        self.tree["columns"] = list(self.data.columns)
        self.tree["show"] = "headings"

        for col in self.tree["columns"]:
            self.tree.heading(col, text=col)  # Define o cabeçalho

        # Adiciona os dados à tabela
        for _, row in self.data.iterrows():
            self.tree.insert("", "end", values=list(row))

    def remove_duplicates(self):
        if self.data is not None:
            before_count = len(self.data)
            self.data = self.data.drop_duplicates()
            after_count = len(self.data)
            messagebox.showinfo("Sucesso", f"Duplicatas removidas! {before_count - after_count} duplicatas encontradas.")
            self.display_data()  # Atualiza a tabela
        else:
            messagebox.showwarning("Aviso", "Nenhum arquivo carregado.")

    def fill_na(self):
        if self.data is not None:
            self.data.fillna('Não disponível', inplace=True)
            messagebox.showinfo("Sucesso", "Valores ausentes preenchidos!")
            self.display_data()  # Atualiza a tabela
        else:
            messagebox.showwarning("Aviso", "Nenhum arquivo carregado.")

    def filter_data(self):
        if self.data is not None:
            column = simpledialog.askstring("Filtrar", "Digite o nome da coluna:")
            if column in self.data.columns:
                value = simpledialog.askstring("Filtrar", "Digite o valor para filtrar:")
                filtered_data = self.data[self.data[column] == value]
                self.data = filtered_data
                messagebox.showinfo("Sucesso", f"Filtrados {len(filtered_data)} registros.")
                self.display_data()  # Atualiza a tabela
            else:
                messagebox.showerror("Erro", "Coluna não encontrada.")
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
