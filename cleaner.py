# cleaner.py
import pandas as pd

def remove_duplicates(data):
    """Remove duplicatas do DataFrame."""
    return data.drop_duplicates()

def fill_na(data):
    """Preenche valores ausentes com 'Não disponível'."""
    return data.fillna('Não disponível')

def filter_column(data, column):
    """Filtra dados por uma coluna específica."""
    return data[[column]]

def filter_row(data, row_index):
    """Filtra dados por uma linha específica."""
    return data.iloc[[row_index]]  # Retorna uma DataFrame com a linha filtrada
