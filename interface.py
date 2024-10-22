from tkinter import ttk, tk
from cleaner import DataCleanerApp  # Importa as funcionalidades de limpeza de dados

class DataCleanerInterface:
    def __init__(self, root, cleaner):
        self.root = root
        self.cleaner = cleaner  # Instancia o DataCleanerApp (funcionalidades)
        self.root.title("Data Cleaner")
        self.root.geometry("800x600")

        # Frame principal para segurar a tabela e os botões
        self.frame = tk.Frame(root, bg="#f0f0f0")
        self.frame.pack(fill=tk.BOTH, expand=True)

        # Criação da tabela Treeview
        self.tree = ttk.Treeview(self.frame)
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Barras de rolagem
        self.scrollbar_y = ttk.Scrollbar(self.frame, orient="vertical", command=self.tree.yview)
        self.scrollbar_y.pack(side=tk.RIGHT, fill=tk.Y)

        self.scrollbar_x = ttk.Scrollbar(self.frame, orient="horizontal", command=self.tree.xview)
        self.scrollbar_x.pack(side=tk.BOTTOM, fill=tk.X)

        # Vincula as barras de rolagem à tabela
        self.tree.configure(yscrollcommand=self.scrollbar_y.set, xscrollcommand=self.scrollbar_x.set)

        # Criação dos botões
        self.button_frame = tk.Frame(root, bg="#d3d3d3")
        self.button_frame.pack(fill=tk.X, padx=10, pady=10)

        self.load_button = tk.Button(self.button_frame, text="Carregar CSV", command=self.cleaner.load_file, bg="#87CEEB")
        self.load_button.pack(side=tk.LEFT, padx=5)

        self.remove_duplicates_button = tk.Button(self.button_frame, text="Remover Duplicatas", command=self.cleaner.remove_duplicates, bg="#FF6347")
        self.remove_duplicates_button.pack(side=tk.LEFT, padx=5)

        self.fill_na_button = tk.Button(self.button_frame, text="Preencher NA", command=self.cleaner.fill_na, bg="#FFD700")
        self.fill_na_button.pack(side=tk.LEFT, padx=5)

        self.filter_column_button = tk.Button(self.button_frame, text="Filtrar por Coluna", command=self.cleaner.filter_column, bg="#20B2AA")
        self.filter_column_button.pack(side=tk.LEFT, padx=5)

        self.filter_row_button = tk.Button(self.button_frame, text="Filtrar por Linha", command=self.cleaner.filter_row, bg="#BA55D3")
        self.filter_row_button.pack(side=tk.LEFT, padx=5)

        self.save_csv_button = tk.Button(self.button_frame, text="Salvar CSV", command=self.cleaner.save_file, bg="#32CD32")
        self.save_csv_button.pack(side=tk.LEFT, padx=5)

        self.save_excel_button = tk.Button(self.button_frame, text="Salvar Excel", command=self.cleaner.save_excel, bg="#32CD32")
        self.save_excel_button.pack(side=tk.LEFT, padx=5)
