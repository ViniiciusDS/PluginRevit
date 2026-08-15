# -*- coding: utf-8 -*-

import sys
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
LIB_PATH = REPO_ROOT / "PluginRevit.extension" / "lib"

if str(LIB_PATH) not in sys.path:
    sys.path.insert(0, str(LIB_PATH))

from pluginrevit.core import build_hello_message, get_project_info


class TestCore(unittest.TestCase):

    def test_project_info(self):
        info = get_project_info()

        self.assertEqual(info["name"], "PluginRevit")
        self.assertTrue(info["version"])

    def test_build_hello_message_with_document(self):
        message = build_hello_message("Projeto Teste", "2026")

        self.assertIn("PluginRevit carregado com sucesso!", message)
        self.assertIn("Projeto: Projeto Teste", message)
        self.assertIn("Revit: 2026", message)

    def test_build_hello_message_without_document(self):
        message = build_hello_message(None, "2026")

        self.assertIn("Nenhum documento aberto", message)


if __name__ == "__main__":
    unittest.main()
