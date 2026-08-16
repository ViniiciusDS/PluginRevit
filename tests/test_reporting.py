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
    build_mep_summary_rows,
    build_parameter_identity_rows,
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

class TestParameterIdentityReporting(unittest.TestCase):
    """
    Testes da preparação dos metadados de identidade dos parâmetros.
    """

    def test_builtin_parameter_identity_row(self):
        """
        Deve preparar corretamente a linha de um parâmetro built-in.
        """

        parameter_infos = [
            {
                "name": "Painel",
                "parameter_id": -1140123,
                "identity_kind": "BuiltIn",
                "built_in_parameter": "RBS_ELEC_PANEL_NAME",
                "is_shared": False,
                "guid": None,
                "data_type_id": "autodesk.spec:string",
            }
        ]

        rows = build_parameter_identity_rows(
            parameter_infos
        )

        self.assertEqual(
            rows[0],
            [
                "Painel",
                "-1140123",
                "BuiltIn",
                "RBS_ELEC_PANEL_NAME",
                "Não",
                "N/D",
                "autodesk.spec:string",
            ],
        )

    def test_shared_parameter_identity_row(self):
        """
        Shared Parameter deve apresentar GUID e origem Shared.
        """

        guid = (
            "12345678-1234-1234-1234-123456789abc"
        )

        parameter_infos = [
            {
                "name": "ID do comando",
                "parameter_id": 250001,
                "identity_kind": "Shared",
                "built_in_parameter": None,
                "is_shared": True,
                "guid": guid,
                "data_type_id": "autodesk.spec:string",
            }
        ]

        rows = build_parameter_identity_rows(
            parameter_infos
        )

        self.assertEqual(
            rows[0],
            [
                "ID do comando",
                "250001",
                "Shared",
                "N/D",
                "Sim",
                guid,
                "autodesk.spec:string",
            ],
        )

    def test_custom_parameter_identity_row(self):
        """
        Parâmetro customizado deve manter sua classificação
        Custom/Other.
        """

        parameter_infos = [
            {
                "name": "RN1",
                "parameter_id": 250100,
                "identity_kind": "Custom/Other",
                "built_in_parameter": None,
                "is_shared": False,
                "guid": None,
                "data_type_id": "autodesk.spec:number",
            }
        ]

        rows = build_parameter_identity_rows(
            parameter_infos
        )

        self.assertEqual(
            rows[0],
            [
                "RN1",
                "250100",
                "Custom/Other",
                "N/D",
                "Não",
                "N/D",
                "autodesk.spec:number",
            ],
        )

    def test_missing_identity_information_becomes_nd(self):
        """
        Metadados ausentes devem ser apresentados como N/D.
        """

        parameter_infos = [
            {
                "name": "Parâmetro Teste",
            }
        ]

        rows = build_parameter_identity_rows(
            parameter_infos
        )

        self.assertEqual(
            rows[0],
            [
                "Parâmetro Teste",
                "N/D",
                "N/D",
                "N/D",
                "N/D",
                "N/D",
                "N/D",
            ],
        )

    def test_same_name_parameters_preserve_distinct_ids(self):
        """
        Dois parâmetros com o mesmo nome devem permanecer distinguíveis
        no relatório através de seus ParameterIds.

        Esse teste representa o cenário encontrado anteriormente com
        parâmetros como "Nível" e "Categoria".
        """

        parameter_infos = [
            {
                "name": "Nível",
                "parameter_id": -100001,
                "identity_kind": "BuiltIn",
                "built_in_parameter": "LEVEL_PARAM_A",
                "is_shared": False,
                "guid": None,
                "data_type_id": "autodesk.spec:reference",
            },
            {
                "name": "Nível",
                "parameter_id": -100002,
                "identity_kind": "BuiltIn",
                "built_in_parameter": "LEVEL_PARAM_B",
                "is_shared": False,
                "guid": None,
                "data_type_id": "autodesk.spec:reference",
            },
        ]

        rows = build_parameter_identity_rows(
            parameter_infos
        )

        self.assertEqual(
            rows[0][0],
            "Nível",
        )

        self.assertEqual(
            rows[1][0],
            "Nível",
        )

        self.assertEqual(
            rows[0][1],
            "-100001",
        )

        self.assertEqual(
            rows[1][1],
            "-100002",
        )

    def test_invalid_identity_item_raises_type_error(self):
        """
        Um item inválido deve gerar erro explícito em vez de produzir
        uma tabela parcialmente incorreta.
        """

        parameter_infos = [
            {
                "name": "Painel",
                "parameter_id": 123,
            },
            "item inválido",
        ]

        with self.assertRaises(TypeError):
            build_parameter_identity_rows(
                parameter_infos
            )

class TestMEPSummaryReporting(unittest.TestCase):
    """
    Testes da preparação do resumo de infraestrutura MEP.
    """

    def test_complete_mep_summary(self):
        """
        Deve preparar corretamente um elemento com infraestrutura
        MEP completa e dois conectores.
        """

        mep_summary = {
            "has_mep_model": True,
            "has_connector_manager": True,
            "has_connector_collection": True,
            "connector_count": 2,
        }

        rows = build_mep_summary_rows(
            mep_summary
        )

        self.assertEqual(
            rows,
            [
                [
                    "Possui MEPModel?",
                    "Sim",
                ],
                [
                    "Possui ConnectorManager?",
                    "Sim",
                ],
                [
                    "Possui coleção Connectors?",
                    "Sim",
                ],
                [
                    "Quantidade de conectores",
                    "2",
                ],
            ],
        )

    def test_element_without_mep_model(self):
        """
        Elemento sem MEPModel deve ser apresentado corretamente.
        """

        mep_summary = {
            "has_mep_model": False,
            "has_connector_manager": False,
            "has_connector_collection": False,
            "connector_count": 0,
        }

        rows = build_mep_summary_rows(
            mep_summary
        )

        self.assertEqual(
            rows[0],
            [
                "Possui MEPModel?",
                "Não",
            ],
        )

        self.assertEqual(
            rows[3],
            [
                "Quantidade de conectores",
                "0",
            ],
        )

    def test_unknown_connector_count_becomes_nd(self):
        """
        Caso a quantidade de conectores não possa ser determinada,
        deve ser exibido N/D.
        """

        mep_summary = {
            "has_mep_model": True,
            "has_connector_manager": True,
            "has_connector_collection": True,
            "connector_count": None,
        }

        rows = build_mep_summary_rows(
            mep_summary
        )

        self.assertEqual(
            rows[3],
            [
                "Quantidade de conectores",
                "N/D",
            ],
        )

    def test_invalid_mep_summary_raises_type_error(self):
        """
        Um valor que não seja dicionário deve gerar erro explícito.
        """

        with self.assertRaises(TypeError):

            build_mep_summary_rows(
                "isto não é um dicionário"
            )

if __name__ == "__main__":
    unittest.main()