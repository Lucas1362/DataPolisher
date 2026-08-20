import pandas as pd

def remove_duplicates(data):
    """Remove linhas duplicadas do DataFrame."""
    return data.drop_duplicates()

def fill_na_intelligent(data, valor, coluna=None):
    """Preenche valores ausentes em uma coluna específica ou no DataFrame todo."""
    # Criamos uma cópia para não alterar o dado original diretamente (boa prática)
    data_limpo = data.copy()
    
    if coluna and coluna.strip() != "" and coluna in data_limpo.columns:
        data_limpo[coluna] = data_limpo[coluna].fillna(valor)
    else:
        data_limpo = data_limpo.fillna(valor)
        
    return data_limpo

def filter_column(data, column_name):
    """Filtra o DataFrame para manter apenas uma coluna específica."""
    return data[[column_name]]

def delete_column(data, column_name):
    """Remove uma coluna específica do DataFrame."""
    return data.drop(columns=[column_name])