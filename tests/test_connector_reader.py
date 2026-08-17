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
    read_connector_info,
    read_element_connectors,
    read_mep_connection_summary,
)


# ======================================================================
# Objetos simulados
# ======================================================================


class FakeConnectorCollection(object):
    """
    Simula uma coleção Connectors.

    A coleção oferece:
        - propriedade Size;
        - suporte à iteração.

    Isso permite testar tanto a Etapa 2A quanto a Etapa 2B.
    """

    def __init__(
        self,
        connectors=None,
        size=None,
    ):
        self._connectors = (
            connectors
            if connectors is not None
            else []
        )

        # ----------------------------------------------------------
        # Permite manter compatibilidade com os testes antigos que
        # instanciam explicitamente uma quantidade.
        # ----------------------------------------------------------

        if size is not None:
            self.Size = size
        else:
            self.Size = len(
                self._connectors
            )

    def __iter__(self):
        return iter(
            self._connectors
        )


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

class FakeEnum(object):
    """
    Simula um enum .NET utilizado pela Revit API.
    """

    def __init__(self, name):
        self.name = name

    def ToString(self):
        return self.name


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

    def test_read_electrical_connector(self):
        """
        Deve identificar domínio e tipo de um Connector elétrico.
        """

        connector = FakeConnector(
            domain="DomainElectrical",
            connector_type="Logical",
            is_connected=True,
            mep_system=object(),
        )

        info = read_connector_info(
            connector,
            index=1,
        )

        self.assertEqual(
            info["index"],
            1,
        )

        self.assertEqual(
            info["domain"],
            "DomainElectrical",
        )

        self.assertEqual(
            info["connector_type"],
            "Logical",
        )

        self.assertTrue(
            info["is_connected"]
        )

        self.assertTrue(
            info["has_mep_system"]
        )

    def test_unconnected_connector(self):
        """
        Connector sem conexão deve ser identificado corretamente.
        """

        connector = FakeConnector(
            domain="DomainElectrical",
            connector_type="End",
            is_connected=False,
            mep_system=None,
        )

        info = read_connector_info(
            connector
        )

        self.assertFalse(
            info["is_connected"]
        )

        self.assertFalse(
            info["has_mep_system"]
        )

    def test_non_electrical_connector_is_preserved(self):
        """
        Nesta etapa conectores de outros domínios não devem ser
        removidos.

        Primeiro queremos descobrir como as famílias estão estruturadas.
        A filtragem elétrica será feita posteriormente.
        """

        connector = FakeConnector(
            domain="DomainPiping",
            connector_type="End",
        )

        info = read_connector_info(
            connector
        )

        self.assertEqual(
            info["domain"],
            "DomainPiping",
        )

    def test_read_multiple_element_connectors(self):
        """
        Deve percorrer todos os conectores de um elemento.
        """

        connector_collection = FakeConnectorCollection(
            connectors=[
                FakeConnector(
                    "DomainElectrical",
                    "Logical",
                ),
                FakeConnector(
                    "DomainElectrical",
                    "End",
                ),
                FakeConnector(
                    "DomainPiping",
                    "End",
                ),
            ]
        )

        element = FakeElement(
            FakeMEPModel(
                FakeConnectorManager(
                    connector_collection
                )
            )
        )

        connectors = read_element_connectors(
            element
        )

        self.assertEqual(
            len(connectors),
            3,
        )

        self.assertEqual(
            connectors[0]["index"],
            1,
        )

        self.assertEqual(
            connectors[2]["index"],
            3,
        )

    def test_element_without_mep_returns_empty_connector_list(self):
        """
        Elemento sem infraestrutura MEP deve retornar lista vazia.
        """

        element = FakeElement(
            mep_model=None
        )

        connectors = read_element_connectors(
            element
        )

        self.assertEqual(
            connectors,
            [],
        )

    def test_none_connector_raises_value_error(self):
        """
        None não representa um Connector válido.
        """

        with self.assertRaises(ValueError):

            read_connector_info(
                None
            )

class FakeConnector(object):
    """
    Simula um Connector individual da Revit API.
    """

    def __init__(
        self,
        domain,
        connector_type,
        is_connected=False,
        mep_system=None,
    ):
        self.Domain = FakeEnum(
            domain
        )

        self.ConnectorType = FakeEnum(
            connector_type
        )

        self.IsConnected = is_connected
        self.MEPSystem = mep_system

if __name__ == "__main__":
    unittest.main()