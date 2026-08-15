# -*- coding: utf-8 -*-

"""
Testes unitários das funções de relatório do PluginRevit.

Esses testes não dependem do Revit e podem ser executados diretamente pelo
Python através do comando run_tests.bat.
"""

import sys
import unittest
from pathlib import Path


# ----------------------------------------------------------------------
# Adiciona a biblioteca compartilhada do plugin ao Python Path.
# ----------------------------------------------------------------------

REPO_ROOT = Path(__file__).resolve().parents[1]
LIB_PATH = REPO_ROOT / "PluginRevit.extension" / "lib"

if str(LIB_PATH) not in sys.path:
    sys.path.insert(0, str(LIB_PATH))


from pluginrevit.reporting import build_element_info_rows


class TestElementInfoReporting(unittest.TestCase):
    """Testes da preparação de informações de elementos para relatório."""

    def test_build_rows_with_complete_information(self):
        """Deve converter corretamente um elemento completo em linhas."""

        element_info = {
            "id": 12345,
            "unique_id": "abc-123",
            "category": "Tomadas elétricas",
            "family": "Tomada 2P+T",
            "type": "10 A",
            "api_class": "FamilyInstance",
        }

        rows = build_element_info_rows(element_info)

        self.assertEqual(rows[0], ["ID", "12345"])
        self.assertEqual(rows[2], ["Categoria", "Tomadas elétricas"])
        self.assertEqual(rows[3], ["Família", "Tomada 2P+T"])
        self.assertEqual(rows[4], ["Tipo", "10 A"])
        self.assertEqual(rows[5], ["Classe API", "FamilyInstance"])

    def test_missing_information_becomes_nd(self):
        """Campos ausentes devem ser apresentados como N/D."""

        element_info = {
            "id": 12345,
        }

        rows = build_element_info_rows(element_info)

        self.assertEqual(rows[0], ["ID", "12345"])
        self.assertEqual(rows[2], ["Categoria", "N/D"])
        self.assertEqual(rows[3], ["Família", "N/D"])
        self.assertEqual(rows[4], ["Tipo", "N/D"])

    def test_zero_is_not_considered_missing(self):
        """O valor numérico zero deve ser preservado e não virar N/D."""

        element_info = {
            "id": 0,
        }

        rows = build_element_info_rows(element_info)

        self.assertEqual(rows[0], ["ID", "0"])


if __name__ == "__main__":
    unittest.main()