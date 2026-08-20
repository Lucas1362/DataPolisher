# interface.py
import os
import tkinter as tk
from tkinter import filedialog, messagebox, simpledialog, Toplevel
from tkinter import ttk
import pandas as pd
import customtkinter as ctk

class DataCleanerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("DataPolisher - Limpeza de Dados")
        self.data = None
        self.data_history = []
        
        # --- ÍCONE ---
        diretorio_atual = os.path.dirname(__file__) 
        caminho_icone = os.path.join(diretorio_atual, "..", "assets", "iconeData1.png")
        try:
            icone = tk.PhotoImage(file=caminho_icone)
            self.root.iconphoto(False, icone)
        except Exception as e:
            print(f"Aviso: Ícone não encontrado. {e}")

        # --- FRAME DA TABELA ---
        self.frame = ctk.CTkFrame(self.root, corner_radius=10)
        self.frame.pack(pady=20, padx=20, fill=tk.BOTH, expand=True)

        self.tree = ttk.Treeview(self.frame)
        self.tree.grid(row=0, column=0, sticky='nsew', padx=10, pady=10)

        self.scrollbar_y = ctk.CTkScrollbar(self.frame, orientation="vertical", command=self.tree.yview)
        self.scrollbar_y.grid(row=0, column=1, sticky='ns', pady=10)

        self.scrollbar_x = ctk.CTkScrollbar(self.root, orientation="horizontal", command=self.tree.xview)
        self.scrollbar_x.pack(side=tk.BOTTOM, fill=tk.X, padx=20, pady=(0, 20))
        self.tree.configure(yscrollcommand=self.scrollbar_y.set, xscrollcommand=self.scrollbar_x.set)

        # --- FRAME DOS BOTÕES ---
        self.button_frame = ctk.CTkFrame(self.root, fg_color="transparent")
        self.button_frame.pack(pady=10, padx=20, fill=tk.X)

        # --- BOTÕES MODERNOS ---
        self.load_button = ctk.CTkButton(self.button_frame, text="Carregar Arquivo", command=self.load_file, width=180)
        self.load_button.grid(row=0, column=0, padx=10, pady=10)

        self.remove_duplicates_button = ctk.CTkButton(self.button_frame, text="Remover Duplicatas", command=self.remove_duplicates, width=180)
        self.remove_duplicates_button.grid(row=0, column=1, padx=10, pady=10)

        self.fill_na_button = ctk.CTkButton(self.button_frame, text="Preencher Nulos", command=self.fill_na, width=180)
        self.fill_na_button.grid(row=0, column=2, padx=10, pady=10)

        self.filter_column_button = ctk.CTkButton(self.button_frame, text="Filtrar por Coluna", command=self.filter_column, width=180)
        self.filter_column_button.grid(row=1, column=0, padx=10, pady=10)

        self.undo_button = ctk.CTkButton(self.button_frame, text="Desfazer Ação", command=self.undo_action, width=180, fg_color="#d9534f", hover_color="#c9302c")
        self.undo_button.grid(row=1, column=1, padx=10, pady=10)

        self.save_button = ctk.CTkButton(self.button_frame, text="Salvar Arquivo", command=self.save_file, width=180, fg_color="#5cb85c", hover_color="#4cae4c")
        self.save_button.grid(row=1, column=2, padx=10, pady=10)

        self.theme_switch = ctk.CTkSwitch(self.button_frame, text="Modo Claro", command=self.toggle_mode)
        self.theme_switch.grid(row=0, column=3, rowspan=2, padx=20, pady=10)

        self.frame.grid_columnconfigure(0, weight=1)
        self.frame.grid_rowconfigure(0, weight=1)
        self.button_frame.grid_columnconfigure((0, 1, 2, 3), weight=1)

    def toggle_mode(self):
        if self.theme_switch.get() == 1:
            ctk.set_appearance_mode("light")
            self.theme_switch.configure(text="Modo Escuro")
        else:
            ctk.set_appearance_mode("dark")
            self.theme_switch.configure(text="Modo Claro")

    def aplicar_estilo(self):
        # Aplica o estilo completo
        aplicar_estilo(self.root, self.is_dark_mode)

    # Método para carregar o arquivo CSV
    # Método para carregar arquivos (Agora com múltiplos formatos)
    def load_file(self):
        # 1. Expandimos as opções de filtros na janela de abrir arquivo
        tipos_de_arquivos = [
            ("Planilhas e Dados", "*.csv *.xlsx *.xls *.ods *.json"),
            ("Arquivos CSV", "*.csv"),
            ("Excel", "*.xlsx *.xls"),
            ("LibreOffice Calc", "*.ods"),
            ("JSON", "*.json"),
            ("Todos os arquivos", "*.*")
        ]
        
        file_path = filedialog.askopenfilename(filetypes=tipos_de_arquivos)
        
        if file_path:
            try:
                # 2. Verifica a extensão para escolher o método certo do Pandas
                if file_path.endswith('.csv'):
                    self.data = pd.read_csv(file_path)
                elif file_path.endswith(('.xlsx', '.xls')):
                    self.data = pd.read_excel(file_path)
                elif file_path.endswith('.ods'):
                    self.data = pd.read_excel(file_path, engine="odf") # LibreOffice
                elif file_path.endswith('.json'):
                    self.data = pd.read_json(file_path)
                elif file_path.endswith('.pdf'):
                    messagebox.showwarning("Aviso", "Ainda não suportamos leitura de PDF. Escolha Excel ou CSV.")
                    return
                else:
                    messagebox.showerror("Erro", "Formato de arquivo não suportado.")
                    return

                # Limpa o histórico de ações ao carregar um arquivo novo (se você já adicionou o desfazer)
                if hasattr(self, 'data_history'):
                    self.data_history = [] 

                self.show_data()
                messagebox.showinfo("Sucesso", f"Arquivo carregado com sucesso!\n{self.data.shape[0]} linhas e {self.data.shape[1]} colunas.")
            except Exception as e:
                messagebox.showerror("Erro", f"Erro ao carregar o arquivo: {e}")
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
            self.data_history.append(self.data.copy())  # Salva o estado atual antes de modificar
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
            self.data_history.append(self.data.copy())  # Salva o estado atual antes de modificar
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
        if self.data is not None:
            column_name = simpledialog.askstring("Filtrar por Coluna", "Digite o nome da coluna:")
            
            if column_name and column_name in self.data.columns:
                # 1. Salva o estado atual na memória (para o botão Desfazer funcionar)
                if hasattr(self, 'data_history'):
                    self.data_history.append(self.data.copy())
                
                # 2. Substitui o DataFrame interno apenas pela coluna escolhida
                self.data = self.data[[column_name]]
                
                # 3. Atualiza a tabela na tela imediatamente
                self.show_data()
                self.show_popup(f"Filtro aplicado! Mostrando apenas a coluna: {column_name}")
            else:
                messagebox.showwarning("Atenção", "Nome da coluna inválido ou não preenchido!")
        else:
            messagebox.showwarning("Aviso", "Carregue um arquivo primeiro.")

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


    # Método para desfazer a última ação
    def undo_action(self):
        if self.data_history: # Verifica se existe algum histórico salvo
            # Pega o último estado salvo e remove da lista de histórico
            self.data = self.data_history.pop() 
            self.show_data() # Atualiza a tabela na tela
            messagebox.showinfo("Desfazer", "Última ação desfeita com sucesso!")
        else:
            messagebox.showwarning("Aviso", "Não há nenhuma ação para desfazer.")
# Executar a aplicação
if __name__ == "__main__":
    root = tk.Tk()
    app = DataCleanerApp(root)
    root.mainloop()