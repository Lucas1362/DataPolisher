# interface.py
import tkinter as tk
from tkinter import filedialog, messagebox, simpledialog, Toplevel
from tkinter import ttk
import pandas as pd

class DataCleanerApp:
    def __init__(self, root):
        
        
        self.root = root
        self.root.title("Data Cleaner")
        self.data = None  # Inicializa o DataFrame como None

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

        # Configure a expansão da grid
        self.frame.grid_rowconfigure(0, weight=1)
        self.frame.grid_columnconfigure(0, weight=1)

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

        self.save_excel_button = tk.Button(root, text="Exportar para Excel", command=self.export_to_excel)
        self.save_excel_button.pack(pady=10)

        # Configura a coluna e linha para expandir
        self.frame.grid_columnconfigure(0, weight=1)
        self.frame.grid_rowconfigure(0, weight=1)

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

    def load_csv(self, file_path):
        self.data = pd.read_csv(file_path)
        self.data.fillna("Não disponível", inplace=True)  # Preenche NaN ao carregar


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
                for column in self.data.columns:
                    if self.data[column].dtype in [int, float]:  # Preencher apenas colunas numéricas
                        self.data[column].fillna(self.data[column].mean(), inplace=True)
                        
                self.show_data()
                self.show_popup("Valores ausentes foram preenchidos com a média das colunas numéricas.")
            else:
                self.show_popup("Nenhum valor ausente encontrado no DataFrame.")
        else:
            messagebox.showwarning("Aviso", "Carregue um arquivo primeiro.")

    # Método para filtrar dados por coluna
    # Método para filtrar dados por coluna
    def filter_column(self):
        column_name = simpledialog.askstring("Filtrar por Coluna", "Digite o nome da coluna:")
        
        # Verifica se a coluna existe
        if column_name is not None and column_name in self.data.columns:
            column_data = self.data[column_name]  # Pega os dados da coluna
            
            # Cria uma nova janela para exibir os dados
            result_window = tk.Toplevel(self.root)
            result_window.title("Resultado do Filtro por Coluna")
            
            # Adiciona um frame para melhor organização
            frame = tk.Frame(result_window)
            frame.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

            # Cria um rótulo com o nome da coluna
            label = tk.Label(frame, text=f"Coluna: {column_name}", font=("Arial", 14, "bold"))
            label.pack(anchor="w")

            # Cria um PanedWindow para permitir o redimensionamento
            paned_window = tk.PanedWindow(frame, orient=tk.VERTICAL)
            paned_window.pack(fill=tk.BOTH, expand=True)

            # Cria a Text box
            text_box = tk.Text(paned_window, wrap=tk.WORD)
            paned_window.add(text_box)

            # Adiciona os dados formatados ao Text, substituindo "nan" por "Dados não disponíveis"
            for index, value in enumerate(column_data):
                if pd.isna(value):  # Verifica se o valor é NaN
                    value = "Dados não disponíveis"  # Mensagem personalizada
                text_box.insert(tk.END, f"Linha {index + 1}: {value}\n")

            # Desabilita a edição do Text
            text_box.config(state=tk.DISABLED)

            # Botão para fechar a janela
            close_button = tk.Button(frame, text="Fechar", command=result_window.destroy)
            close_button.pack(pady=5)
        else:
            messagebox.showwarning("Atenção", "Nome da coluna inválido!")

    # Método para filtrar dados por linha
    def filter_row(self):
        row_number = simpledialog.askinteger("Filtrar por linha", "Digite o número da linha:")
        
        # Verifica se a linha existe
        if row_number is not None and 1 <= row_number <= len(self.data):
            row_data = self.data.iloc[row_number - 1]  # Pega a linha desejada
            
            # Cria uma nova janela para exibir os dados
            result_window = tk.Toplevel(self.root)
            result_window.title("Resultado do Filtro por Linha")
            
            # Adiciona um frame para melhor organização
            frame = tk.Frame(result_window)
            frame.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)
            
            # Cria um rótulo com o número da linha
            label = tk.Label(frame, text=f"Linha {row_number}:", font=("Arial", 14, "bold"))
            label.pack(anchor="w")

            # Cria um PanedWindow para permitir o redimensionamento
            paned_window = tk.PanedWindow(frame, orient=tk.VERTICAL)
            paned_window.pack(fill=tk.BOTH, expand=True)

            # Cria a Text box
            text_box = tk.Text(paned_window, wrap=tk.WORD)
            paned_window.add(text_box)

            # Adiciona os dados formatados ao Text, substituindo "nan" por "Dados não disponíveis"
            for column, value in row_data.items():
                if pd.isna(value):  # Verifica se o valor é NaN
                    value = "Dados não disponíveis"  # Mensagem personalizada
                text_box.insert(tk.END, f"{column}: {value}\n")

            # Desabilita a edição do Text
            text_box.config(state=tk.DISABLED)

            # Botão para fechar a janela
            close_button = tk.Button(frame, text="Fechar", command=result_window.destroy)
            close_button.pack(pady=5)
        else:
            messagebox.showwarning("Atenção", "Número da linha inválido!")




    # Método para mostrar os dados na janela pop-up
    def show_popup(self, message):
        popup = Toplevel(self.root)
        popup.title("Resultado")
        popup.geometry("400x300")
        popup.resizable(True, True)  # Permite redimensionar a janela
        label = tk.Label(popup, text=message, wraplength=350)
        label.pack(pady=20)
        ok_button = tk.Button(popup, text="OK", command=popup.destroy)
        ok_button.pack(pady=10)

    # Método para salvar o DataFrame como CSV
    def save_file(self):
        if self.data is not None:
            file_path = filedialog.asksaveasfilename(defaultextension=".csv",
                                                      filetypes=[("CSV files", "*.csv")])
            if file_path:
                self.data.to_csv(file_path, index=False)
                messagebox.showinfo("Sucesso", "Arquivo salvo com sucesso!")
        else:
            messagebox.showwarning("Aviso", "Não há dados para salvar.")

    # Método para exportar o DataFrame para Excel
    def export_to_excel(self):
        if self.data is not None:
            file_path = filedialog.asksaveasfilename(defaultextension=".xlsx",
                                                      filetypes=[("Excel files", "*.xlsx")])
            if file_path:
                self.data.to_excel(file_path, index=False)
                messagebox.showinfo("Sucesso", "Arquivo exportado para Excel com sucesso!")
        else:
            messagebox.showwarning("Aviso", "Não há dados para exportar.")

# Rodar a aplicação
if __name__ == "__main__":
    root = tk.Tk()
    app = DataCleanerApp(root)
    root.mainloop()
