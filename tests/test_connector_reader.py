# -*- coding: utf-8 -*-

"""
Testes unitários do módulo connector_reader.

Os testes utilizam objetos simulados para reproduzir somente a interface
MEP necessária nesta etapa.

Nenhuma instalação ou sessão do Revit é necessária para executar
estes testes.
"""

import sys
import unittest
from pathlib import Path


# ======================================================================
# Python Path
# ======================================================================

REPO_ROOT = Path(__file__).resolve().parents[1]

LIB_PATH = (
    REPO_ROOT
    / "PluginRevit.extension"
    / "lib"
)

if str(LIB_PATH) not in sys.path:
    sys.path.insert(
        0,
        str(LIB_PATH),
    )


from pluginrevit.connector_reader import (
    read_mep_connection_summary,
)


# ======================================================================
# Objetos simulados
# ======================================================================


class FakeConnectorCollection(object):
    """
    Simula uma coleção Connectors com propriedade Size.
    """

    def __init__(self, size):
        self.Size = size


class FakeConnectorManager(object):
    """
    Simula ConnectorManager.
    """

    def __init__(self, connectors=None):
        self.Connectors = connectors


class FakeMEPModel(object):
    """
    Simula MEPModel.
    """

    def __init__(self, connector_manager=None):
        self.ConnectorManager = connector_manager


class FakeElement(object):
    """
    Simula um elemento que pode ou não possuir MEPModel.
    """

    def __init__(self, mep_model=None):
        self.MEPModel = mep_model


# ======================================================================
# Testes
# ======================================================================


class TestConnectorReader(unittest.TestCase):
    """
    Testes da leitura básica da infraestrutura MEP.
    """

    def test_element_without_mep_model(self):
        """
        Elemento sem MEPModel deve ser identificado corretamente.
        """

        element = FakeElement(
            mep_model=None
        )

        result = read_mep_connection_summary(
            element
        )

        self.assertFalse(
            result["has_mep_model"]
        )

        self.assertFalse(
            result["has_connector_manager"]
        )

        self.assertEqual(
            result["connector_count"],
            0,
        )

    def test_mep_model_without_connector_manager(self):
        """
        MEPModel existente sem ConnectorManager deve ser tratado
        como resultado válido.
        """

        element = FakeElement(
            FakeMEPModel(
                connector_manager=None
            )
        )

        result = read_mep_connection_summary(
            element
        )

        self.assertTrue(
            result["has_mep_model"]
        )

        self.assertFalse(
            result["has_connector_manager"]
        )

        self.assertEqual(
            result["connector_count"],
            0,
        )

    def test_connector_manager_without_collection(self):
        """
        ConnectorManager sem coleção Connectors deve ser identificado.
        """

        element = FakeElement(
            FakeMEPModel(
                FakeConnectorManager(
                    connectors=None
                )
            )
        )

        result = read_mep_connection_summary(
            element
        )

        self.assertTrue(
            result["has_connector_manager"]
        )

        self.assertFalse(
            result["has_connector_collection"]
        )

        self.assertEqual(
            result["connector_count"],
            0,
        )

    def test_element_with_connectors(self):
        """
        Deve contar corretamente os conectores encontrados.
        """

        connectors = FakeConnectorCollection(
            size=2
        )

        element = FakeElement(
            FakeMEPModel(
                FakeConnectorManager(
                    connectors=connectors
                )
            )
        )

        result = read_mep_connection_summary(
            element
        )

        self.assertTrue(
            result["has_mep_model"]
        )

        self.assertTrue(
            result["has_connector_manager"]
        )

        self.assertTrue(
            result["has_connector_collection"]
        )

        self.assertEqual(
            result["connector_count"],
            2,
        )

    def test_none_element_raises_value_error(self):
        """
        None não representa um elemento válido e deve gerar erro explícito.
        """

        with self.assertRaises(ValueError):

            read_mep_connection_summary(
                None
            )


if __name__ == "__main__":
    unittest.main()