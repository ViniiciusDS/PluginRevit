# -*- coding: utf-8 -*-

"""
Testes estruturais do comando Inspecionar Conectores.

O script depende diretamente do ambiente pyRevit/Revit e, portanto,
não pode ser executado pelo unittest externo.

Estes testes verificam o contrato estrutural mínimo:

    - arquivo existe;
    - sintaxe Python válida;
    - funções fundamentais estão importadas;
    - funções fundamentais realmente participam do fluxo.

Os testes funcionais continuam sendo realizados dentro do Revit.
"""

import ast
import unittest
from pathlib import Path


# ======================================================================
# Caminho do comando
# ======================================================================

REPO_ROOT = Path(__file__).resolve().parents[1]

COMMAND_PATH = (
    REPO_ROOT
    / "PluginRevit.extension"
    / "PluginRevit.tab"
    / "Desenvolvimento.panel"
    / "Inspecionar Conectores.pushbutton"
    / "script.py"
)


class TestConnectorCommandContract(unittest.TestCase):
    """
    Testes estruturais do botão Inspecionar Conectores.
    """

    def _read_source_code(self):
        """
        Lê o código-fonte completo do comando.

        Returns:
            str:
                Conteúdo de script.py.
        """

        return COMMAND_PATH.read_text(
            encoding="utf-8"
        )

    def _parse_source_code(self):
        """
        Converte o código-fonte em uma árvore sintática Python.

        Returns:
            ast.Module:
                Árvore produzida por ast.parse().
        """

        return ast.parse(
            self._read_source_code()
        )

    def test_connector_command_file_exists(self):
        """
        O comando Inspecionar Conectores deve existir no caminho esperado.
        """

        self.assertTrue(
            COMMAND_PATH.exists(),
            "O comando Inspecionar Conectores não foi encontrado.",
        )

    def test_connector_command_has_valid_python_syntax(self):
        """
        O script deve possuir sintaxe Python válida.
        """

        syntax_tree = self._parse_source_code()

        self.assertIsNotNone(
            syntax_tree
        )

    def test_connector_command_references_required_functions(self):
        """
        O comando deve importar todas as funções fundamentais
        necessárias para o fluxo da Etapa 2B.
        """

        syntax_tree = self._parse_source_code()

        imported_names = set()

        for node in ast.walk(syntax_tree):

            if isinstance(node, ast.ImportFrom):

                for alias in node.names:

                    imported_names.add(
                        alias.name
                    )

        expected_names = {
            "read_basic_element_info",
            "read_mep_connection_summary",
            "read_element_connectors",
            "build_element_info_rows",
            "build_mep_summary_rows",
            "build_connector_rows",
        }

        missing_names = (
            expected_names
            - imported_names
        )

        self.assertFalse(
            missing_names,
            "Imports essenciais ausentes: {0}".format(
                sorted(missing_names)
            ),
        )

    def test_connector_command_calls_required_functions(self):
        """
        O comando deve realmente executar as funções fundamentais.

        Isso evita regressões em que um import permanece no arquivo,
        mas a função deixa de participar do fluxo.
        """

        syntax_tree = self._parse_source_code()

        called_functions = set()

        for node in ast.walk(syntax_tree):

            if isinstance(node, ast.Call):

                if isinstance(node.func, ast.Name):

                    called_functions.add(
                        node.func.id
                    )

        expected_calls = {
            "read_basic_element_info",
            "read_mep_connection_summary",
            "read_element_connectors",
            "build_element_info_rows",
            "build_mep_summary_rows",
            "build_connector_rows",
        }

        missing_calls = (
            expected_calls
            - called_functions
        )

        self.assertFalse(
            missing_calls,
            "Chamadas essenciais ausentes: {0}".format(
                sorted(missing_calls)
            ),
        )


if __name__ == "__main__":
    unittest.main()