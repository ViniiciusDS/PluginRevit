# -*- coding: utf-8 -*-

"""
Testes estruturais do comando Inspecionar Parametros.

O script do botão depende do ambiente pyRevit/Revit e, portanto, não pode
ser executado diretamente pelo unittest externo.

Estes testes verificam o contrato estrutural mínimo do comando:

    - arquivo existe;
    - código possui sintaxe Python válida;
    - funções essenciais da arquitetura continuam referenciadas.

Os testes de funcionamento real continuam sendo executados dentro do Revit.
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
    / "Inspecionar Parametros.pushbutton"
    / "script.py"
)


class TestParameterCommandContract(unittest.TestCase):
    """
    Testes do contrato estrutural do comando Inspecionar Parametros.
    """

    def _read_source_code(self):
        """
        Lê o código-fonte do comando.

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
                Árvore sintática produzida por ast.parse().
        """

        return ast.parse(
            self._read_source_code()
        )

    def test_parameter_command_file_exists(self):
        """
        O script do comando deve existir no caminho esperado.
        """

        self.assertTrue(
            COMMAND_PATH.exists(),
            "O comando Inspecionar Parametros não foi encontrado.",
        )

    def test_parameter_command_has_valid_python_syntax(self):
        """
        O script deve possuir sintaxe Python válida.

        Esse teste detecta problemas como:
            - parênteses ausentes;
            - indentação inválida;
            - strings não fechadas;
            - erros estruturais de sintaxe.
        """

        syntax_tree = self._parse_source_code()

        self.assertIsNotNone(
            syntax_tree
        )

    def test_parameter_command_references_required_functions(self):
        """
        O comando deve importar as funções fundamentais do fluxo:

            read_basic_element_info
            read_element_parameters
            build_element_info_rows
            build_parameter_rows
        """

        syntax_tree = self._parse_source_code()

        imported_names = set()

        # --------------------------------------------------------------
        # Percorremos toda a árvore porque alguns imports estão dentro
        # da função main().
        # --------------------------------------------------------------

        for node in ast.walk(syntax_tree):

            if isinstance(node, ast.ImportFrom):

                for alias in node.names:
                    imported_names.add(
                        alias.name
                    )

        expected_names = {
            "read_basic_element_info",
            "read_element_parameters",
            "build_element_info_rows",
            "build_parameter_rows",
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


if __name__ == "__main__":
    unittest.main()