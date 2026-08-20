import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

import pandas as pd

import cleaner


class StandardizeTestCase(unittest.TestCase):
    def test_standardize_text(self):
        value = cleaner.standardize_text("  São Paulo  ")
        self.assertEqual(value, "sao paulo")

    def test_standardize_dataframe_column(self):
        df = pd.DataFrame({
            "nome": ["  JoãO ", "MARIA", " Ana "],
            "cidade": ["São Paulo", "Rio de Janeiro", "  "]
        })

        result = cleaner.standardize_dataframe(df, column="nome", case="lower")

        self.assertEqual(list(result["nome"]), ["joao", "maria", "ana"])
