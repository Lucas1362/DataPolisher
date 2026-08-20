import unicodedata

import pandas as pd


def standardize_text(value, case="lower"):
    """Padroniza um valor textual, removendo acentos e espaços extras."""
    if pd.isna(value):
        return value

    text = str(value).strip()
    text = unicodedata.normalize("NFKD", text)
    text = "".join(char for char in text if not unicodedata.combining(char))
    text = text.replace("\n", " ").replace("\r", " ")
    text = " ".join(text.split())

    if case == "upper":
        return text.upper()
    if case == "title":
        return text.title()
    return text.lower()


def standardize_dataframe(data, column=None, case="lower"):
    """Padroniza textos de uma coluna ou de todas as colunas textuais do DataFrame."""
    result = data.copy()

    if column is not None:
        if column not in result.columns:
            raise ValueError(f"Coluna '{column}' não encontrada.")

        result[column] = result[column].map(
            lambda value: standardize_text(value, case=case) if isinstance(value, str) else value
        )
        return result

    for col in result.columns:
        if pd.api.types.is_object_dtype(result[col]) or pd.api.types.is_string_dtype(result[col]):
            result[col] = result[col].map(
                lambda value: standardize_text(value, case=case) if isinstance(value, str) else value
            )

    return result


def remove_duplicates(data):
    """Remove linhas duplicadas do DataFrame."""
    return data.drop_duplicates()


def fill_na_intelligent(data, valor, coluna=None):
    """Preenche valores ausentes em uma coluna específica ou no DataFrame todo."""
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