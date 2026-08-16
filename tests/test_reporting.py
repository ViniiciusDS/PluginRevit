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


from pluginrevit.reporting import (
    build_element_info_rows,
    build_parameter_rows,
)


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

class TestParameterReporting(unittest.TestCase):
    """
    Testes da preparação dos parâmetros para apresentação em tabela.
    """

    def test_build_parameter_rows_with_complete_information(self):
        """
        Deve converter corretamente informações completas de parâmetros
        em linhas de tabela.
        """

        parameter_infos = [
            {
                "name": "Painel",
                "storage_type": "String",
                "raw_value": "QD-01",
                "display_value": "QD-01",
                "has_value": True,
                "is_read_only": True,
            },
            {
                "name": "Elevação",
                "storage_type": "Double",
                "raw_value": 0.9842519685,
                "display_value": "300 mm",
                "has_value": True,
                "is_read_only": False,
            },
        ]

        rows = build_parameter_rows(
            parameter_infos
        )

        self.assertEqual(
            rows[0],
            [
                "Painel",
                "QD-01",
                "QD-01",
                "String",
                "Sim",
                "Sim",
            ],
        )

        self.assertEqual(
            rows[1],
            [
                "Elevação",
                "300 mm",
                "0.9842519685",
                "Double",
                "Sim",
                "Não",
            ],
        )

    def test_missing_parameter_information_becomes_nd(self):
        """
        Informações ausentes devem ser exibidas como N/D.
        """

        parameter_infos = [
            {
                "name": "Comentários",
            }
        ]

        rows = build_parameter_rows(
            parameter_infos
        )

        self.assertEqual(
            rows[0],
            [
                "Comentários",
                "N/D",
                "N/D",
                "N/D",
                "N/D",
                "N/D",
            ],
        )

    def test_empty_parameter_list_returns_empty_rows(self):
        """
        Uma lista vazia de parâmetros deve gerar uma lista vazia
        de linhas sem provocar erro.
        """

        rows = build_parameter_rows([])

        self.assertEqual(
            rows,
            [],
        )

    def test_invalid_parameter_item_raises_type_error(self):
        """
        Um item que não seja dicionário deve gerar erro explícito.

        Isso ajuda a detectar problemas de contrato entre
        parameter_reader.py e reporting.py.
        """

        parameter_infos = [
            {
                "name": "Circuito",
                "display_value": "C1",
            },
            "isto não é um dicionário",
        ]

        with self.assertRaises(TypeError):
            build_parameter_rows(
                parameter_infos
            )

if __name__ == "__main__":
    unittest.main()