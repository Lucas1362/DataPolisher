import pandas as pd
import tkinter as tk
from tkinter import filedialog, messagebox
from scipy import stats  # Para a detecção de outliers

class DataCleanerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Data Cleaner")
        self.data = None  # Inicializa o DataFrame como None

        # Botão para carregar o arquivo
        self.load_button = tk.Button(root, text="Carregar Arquivo CSV", command=self.load_file)
        self.load_button.pack(pady=10)

        # Botão para remover duplicatas
        self.remove_duplicates_button = tk.Button(root, text="Remover Duplicatas", command=self.remove_duplicates)
        self.remove_duplicates_button.pack(pady=10)

        # Botão para preencher valores ausentes
        self.fill_na_button = tk.Button(root, text="Preencher Valores Ausentes", command=self.fill_na)
        self.fill_na_button.pack(pady=10)

        # Botão para remover outliers
        self.remove_outliers_button = tk.Button(root, text="Remover Outliers", command=self.remove_outliers)
        self.remove_outliers_button.pack(pady=10)

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
                self.data = pd.read_csv(file_path)
                messagebox.showinfo("Sucesso", "Arquivo carregado com sucesso!")
                print(self.data.head())
            except Exception as e:
                messagebox.showerror("Erro", f"Erro ao carregar o arquivo: {e}")

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

    # Nova função para remover outliers usando Z-Score
    def remove_outliers(self):
        if self.data is not None:
            try:
                numeric_columns = self.data.select_dtypes(include='number').columns  # Seleciona apenas colunas numéricas
                before_count = len(self.data)

                # Remove outliers de todas as colunas numéricas com base no Z-Score
                for column in numeric_columns:
                    z_scores = stats.zscore(self.data[column])
                    self.data = self.data[(abs(z_scores) < 3)]  # Limite de 3 desvios-padrão

                after_count = len(self.data)
                messagebox.showinfo("Sucesso", f"Outliers removidos! {before_count - after_count} linhas removidas.")
            except Exception as e:
                messagebox.showerror("Erro", f"Erro ao remover outliers: {e}")
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
