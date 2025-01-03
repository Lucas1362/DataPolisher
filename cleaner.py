# cleaner.py
import pandas as pd
from estilo import aplicar_estilo_botao, aplicar_estilo_entry

<<<<<<< HEAD
def remove_duplicates(data):
    """Remove duplicatas do DataFrame."""
    return data.drop_duplicates()

def fill_na(data):
    """Preenche valores ausentes com 'Não disponível'."""
    return data.fillna('Não disponível')

def filter_column(data, column):
    """Filtra dados por uma coluna específica."""
    return data[[column]]
=======
class DataCleanerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Data Cleaner")
        self.data = None  # Inicializa o DataFrame como None
>>>>>>> parent of 4bf3b48 (criação de uma pasta apaneas para a interface com o intuito de diexar o codigo mais maleavel)

def filter_row(data, row_index):
    """Filtra dados por uma linha específica."""
    return data.iloc[[row_index]]  # Retorna uma DataFrame com a linha filtrada
