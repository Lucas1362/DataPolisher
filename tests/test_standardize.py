import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

import pandas as pd
import tkinter as tk
import customtkinter as ctk
from tkinterdnd2 import TkinterDnD

import cleaner
from interface import DataCleanerApp


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

    def test_theme_toggle_updates_switch_state(self):
        root = ctk.CTk()
        root.withdraw()
        app = DataCleanerApp(root)

        app.toggle_mode()

        self.assertTrue(app.is_dark_mode)
        self.assertEqual(app.theme_switch.get(), 1)
        self.assertEqual(app.theme_switch.cget("text"), "Modo escuro")

        root.destroy()

    def test_settings_menu_can_collapse(self):
        root = ctk.CTk()
        root.withdraw()
        app = DataCleanerApp(root)

        self.assertFalse(app.menu_panel.pack_propagate())

        root.destroy()

    def test_language_change_updates_ui_texts(self):
        root = ctk.CTk()
        root.withdraw()
        app = DataCleanerApp(root)

        app.change_language("English")

        self.assertEqual(app.language, "en")
        self.assertEqual(app.load_button.cget("text"), "Load File")
        self.assertEqual(app.theme_switch.cget("text"), "Light mode")

        root.destroy()

    def test_parse_dropped_files_handles_tkinterdnd_format(self):
        root = ctk.CTk()
        root.withdraw()
        app = DataCleanerApp(root)

        parsed = app.parse_dropped_files('{"/tmp/arquivo.csv" "C:/dados/arquivo.xlsx"}')

        self.assertEqual(parsed, ["/tmp/arquivo.csv", "C:/dados/arquivo.xlsx"])

        root.destroy()

    def test_app_initializes_with_tkinterdnd_root(self):
        root = TkinterDnD.Tk()
        root.withdraw()
        app = DataCleanerApp(root)

        self.assertTrue(hasattr(app, "frame"))

        root.destroy()

    def test_table_wheel_scroll_is_vertical_and_horizontal_drag_stays_right_button(self):
        root = ctk.CTk()
        root.withdraw()
        app = DataCleanerApp(root)

        self.assertNotEqual(app.tree.bind("<MouseWheel>"), "")
        self.assertNotEqual(app.tree.bind("<Button-4>"), "")
        self.assertNotEqual(app.tree.bind("<Button-5>"), "")
        self.assertNotEqual(app.root.bind("<MouseWheel>"), "")
        self.assertNotEqual(app.root.bind("<Button-4>"), "")
        self.assertNotEqual(app.root.bind("<Button-5>"), "")
        self.assertEqual(app.tree.bind("<Shift-MouseWheel>"), "")
        self.assertNotEqual(app.tree.bind("<ButtonPress-3>"), "")

        root.destroy()

    def test_right_drag_moves_table_on_both_axes(self):
        root = ctk.CTk()
        root.withdraw()
        app = DataCleanerApp(root)
        app.data = pd.DataFrame({
            **{f"col_{i}": [j + i for j in range(30)] for i in range(1, 9)},
        })
        app.show_data()
        app.root.update_idletasks()

        for column in app.tree["columns"]:
            app.tree.column(column, width=500, minwidth=120, stretch=False)

        app._horizontal_drag_active = True
        app._horizontal_drag_last_x = 100
        app._horizontal_drag_last_y = 80
        app.tree.xview_moveto(0.5)
        app.tree.yview_moveto(0.5)

        event = type("DummyEvent", (), {"x": 180, "y": 160})()
        app._move_horizontal_drag(event)

        self.assertGreater(float(app.tree.xview()[0]), 0.0)
        self.assertGreater(float(app.tree.yview()[0]), 0.0)

        root.destroy()

    def test_divider_toggle_and_numeric_centering_rules(self):
        root = ctk.CTk()
        root.withdraw()
        app = DataCleanerApp(root)

        app.toggle_table_dividers()
        self.assertFalse(app.table_divider_enabled)

        self.assertTrue(app._should_center_numeric_column("valor_total"))
        self.assertTrue(app._should_center_numeric_column("numero_pedido"))
        self.assertTrue(app._should_center_numeric_column("pedido"))
        self.assertFalse(app._should_center_numeric_column("cpf"))
        self.assertFalse(app._should_center_numeric_column("cnpj"))

        root.destroy()

    def test_dark_mode_uses_deep_gray_palette(self):
        root = ctk.CTk()
        root.withdraw()
        app = DataCleanerApp(root)

        app.toggle_mode()
        colors = app._get_theme_colors()

        self.assertEqual(colors["bg"], "#161616")
        self.assertEqual(colors["panel"], "#1C1C1C")
        self.assertEqual(colors["surface"], "#2B2B2B")
        self.assertEqual(colors["surface_alt"], "#333333")

        root.destroy()

    def test_toolbar_uses_single_row_and_resizes_with_font_scale(self):
        root = ctk.CTk()
        root.withdraw()
        app = DataCleanerApp(root)

        rows = [
            app.load_button.grid_info().get("row", 0),
            app.remove_duplicates_button.grid_info().get("row", 0),
            app.fill_na_button.grid_info().get("row", 0),
            app.standardize_button.grid_info().get("row", 0),
            app.filter_column_button.grid_info().get("row", 0),
            app.filter_row_button.grid_info().get("row", 0),
            app.undo_button.grid_info().get("row", 0),
            app.save_button.grid_info().get("row", 0),
            app.delete_column_button.grid_info().get("row", 0),
        ]

        self.assertTrue(all(row == 0 for row in rows))

        before_height = app.load_button.cget("height")
        app.font_scale = 1.2
        app._apply_font_scale()
        self.assertGreater(app.load_button.cget("height"), before_height)

        root.destroy()

    def test_dividers_follow_column_boundaries(self):
        root = ctk.CTk()
        root.withdraw()
        app = DataCleanerApp(root)
        app.data = pd.DataFrame({
            "col_a": [1, 2],
            "col_b": [3, 4],
            "col_c": [5, 6],
        })
        app.show_data()
        app.root.update_idletasks()

        self.assertEqual(len(app._table_divider_lines), 0)
        self.assertFalse(app.table_divider_enabled)

        root.destroy()
