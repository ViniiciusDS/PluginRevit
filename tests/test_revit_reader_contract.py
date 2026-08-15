# -*- coding: utf-8 -*-

"""
Testes estruturais do módulo revit_reader.

O módulo revit_reader depende do pyRevit/Revit e, portanto, não pode ser
importado diretamente pelos testes Python externos nesta etapa.

Em vez disso, estes testes analisam o código-fonte utilizando o módulo ast
da biblioteca padrão do Python.

Objetivo:
    garantir que funções essenciais do módulo existam no nível principal
    do arquivo e evitar erros de importação causados por funções ausentes
    ou incorretamente indentadas.
"""

import ast
import unittest
from pathlib import Path


# ----------------------------------------------------------------------
# Localização do arquivo que será analisado.
# ----------------------------------------------------------------------

REPO_ROOT = Path(__file__).resolve().parents[1]

REVIT_READER_PATH = (
    REPO_ROOT
    / "PluginRevit.extension"
    / "lib"
    / "pluginrevit"
    / "revit_reader.py"
)


class TestRevitReaderContract(unittest.TestCase):
    """
    Testa o contrato estrutural mínimo esperado de revit_reader.py.
    """

    def _get_top_level_function_names(self):
        """
        Retorna todas as funções declaradas no nível principal do módulo.

        Returns:
            set:
                Nomes das funções encontradas diretamente no arquivo.

        Notes:
            Uma função acidentalmente declarada dentro de outra função
            não aparecerá neste conjunto. Isso permite detectar problemas
            de indentação que poderiam provocar ImportError.
        """

        source_code = REVIT_READER_PATH.read_text(
            encoding="utf-8"
        )

        syntax_tree = ast.parse(source_code)

        return {
            node.name
            for node in syntax_tree.body
            if isinstance(node, ast.FunctionDef)
        }

    def test_revit_reader_file_exists(self):
        """
        O arquivo revit_reader.py deve existir no local esperado.
        """

        self.assertTrue(
            REVIT_READER_PATH.exists(),
            "revit_reader.py não foi encontrado.",
        )

    def test_expected_functions_are_top_level(self):
        """
        Funções públicas e auxiliares esperadas devem existir
        no nível principal do módulo.
        """

        functions = self._get_top_level_function_names()

        expected_functions = {
            "_get_element_id_value",
            "_safe_get_name",
            "read_basic_element_info",
        }

        missing_functions = expected_functions - functions

        self.assertFalse(
            missing_functions,
            "Funções ausentes ou incorretamente indentadas: {0}".format(
                sorted(missing_functions)
            ),
        )


if __name__ == "__main__":
    unittest.main()