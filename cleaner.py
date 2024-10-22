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

        # Frame para a tabela
        self.frame = tk.Frame(root)
        self.frame.pack(pady=10)

        # Configuração da tabela de visualização
        self.tree = ttk.Treeview(self.frame)
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Barras de rolagem
        self.scrollbar_y = ttk.Scrollbar(self.frame, orient="vertical", command=self.tree.yview)
        self.scrollbar_y.pack(side=tk.RIGHT, fill=tk.Y)

        self.scrollbar_x = ttk.Scrollbar(root, orient="horizontal", command=self.tree.xview)
        self.scrollbar_x.pack(side=tk.BOTTOM, fill=tk.X)

        # Configura a tabela para usar as barras de rolagem
        self.tree.configure(yscrollcommand=self.scrollbar_y.set, xscrollcommand=self.scrollbar_x.set)

        # Botões da interface
        self.load_button = tk.Button(root, text="Carregar Arquivo CSV", command=self.load_file)
        self.load_button.pack(pady=10)

        self.remove_duplicates_button = tk.Button(root, text="Remover Duplicatas", command=self.remove_duplicates)
        self.remove_duplicates_button.pack(pady=10)

        self.fill_na_button = tk.Button(root, text="Preencher Valores Ausentes", command=self.fill_na)
        self.fill_na_button.pack(pady=10)

        self.filter_column_button = tk.Button(root, text="Filtrar Dados por Coluna", command=self.filter_column)
        self.filter_column_button.pack(pady=10)

        self.filter_row_button = tk.Button(root, text="Filtrar Dados por Linha", command=self.filter_row)
        self.filter_row_button.pack(pady=10)

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

    def filter_column(self):
        if self.data is not None:
            column = simpledialog.askstring("Filtrar Coluna", "Digite o nome da coluna:")
            if column in self.data.columns:
                unique_values = self.data[column].unique()  # Obtém valores únicos da coluna
                value = simpledialog.askstring("Filtrar Coluna", f"Escolha um valor para filtrar:\n{unique_values.tolist()}")
                if value in unique_values:
                    filtered_data = self.data[self.data[column] == value]
                    messagebox.showinfo("Sucesso", f"Filtrados {len(filtered_data)} registros.")
                    self.data = filtered_data[[column]]  # Mantém apenas a coluna filtrada
                    self.display_data()  # Atualiza a tabela para mostrar a coluna filtrada
                else:
                    messagebox.showerror("Erro", "Valor não encontrado na coluna.")
            else:
                messagebox.showerror("Erro", "Coluna não encontrada.")
        else:
            messagebox.showwarning("Aviso", "Nenhum arquivo carregado.")

    def filter_row(self):
        if self.data is not None:
            try:
                row_index = simpledialog.askinteger("Filtrar Linha", "Digite o índice da linha (começando de 0):")
                if row_index is not None and 0 <= row_index < len(self.data):
                    row_data = self.data.iloc[row_index]
                    self.data = pd.DataFrame([row_data])  # Cria um DataFrame a partir da linha filtrada
                    messagebox.showinfo("Sucesso", f"Exibindo dados da linha {row_index}.")
                    self.display_data()  # Atualiza a tabela
                else:
                    messagebox.showerror("Erro", "Índice inválido.")
            except ValueError:
                messagebox.showerror("Erro", "Por favor, insira um número válido.")
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
