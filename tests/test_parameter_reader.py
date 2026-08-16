# -*- coding: utf-8 -*-

"""
Testes unitários do módulo parameter_reader.

Os testes utilizam objetos simulados que reproduzem apenas a interface
necessária de Autodesk.Revit.DB.Parameter.

Isso permite validar a lógica de leitura de parâmetros sem precisar abrir
o Revit durante os testes automáticos.
"""

import sys
import unittest
from pathlib import Path


# ----------------------------------------------------------------------
# Adiciona a biblioteca compartilhada do PluginRevit ao Python Path.
# ----------------------------------------------------------------------

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


from pluginrevit.parameter_reader import (
    read_element_parameters,
    read_parameter_info,
)


# ======================================================================
# Objetos falsos utilizados nos testes
# ======================================================================


class FakeStorageType(object):
    """
    Simula o enum StorageType da Revit API.
    """

    def __init__(self, name):
        self.name = name

    def ToString(self):
        return self.name


class FakeDefinition(object):
    """
    Simula a Definition associada a um Parameter.
    """

    def __init__(self, name):
        self.Name = name


class FakeElementId(object):
    """
    Simula Autodesk.Revit.DB.ElementId.
    """

    def __init__(self, value):
        self.Value = value


class FakeParameter(object):
    """
    Simula somente as propriedades e métodos de Parameter utilizados
    pelo PluginRevit.
    """

    def __init__(
        self,
        name,
        storage_type,
        value=None,
        value_string=None,
        has_value=True,
        is_read_only=False,
    ):
        self.Definition = FakeDefinition(name)

        self.StorageType = FakeStorageType(
            storage_type
        )

        self._value = value
        self._value_string = value_string

        self.HasValue = has_value
        self.IsReadOnly = is_read_only

    def AsString(self):
        return self._value

    def AsInteger(self):
        return self._value

    def AsDouble(self):
        return self._value

    def AsElementId(self):
        return FakeElementId(
            self._value
        )

    def AsValueString(self):
        return self._value_string


class FakeElement(object):
    """
    Simula um elemento contendo uma coleção Parameters.
    """

    def __init__(self, parameters):
        self.Parameters = parameters


# ======================================================================
# Testes
# ======================================================================


class TestParameterReader(unittest.TestCase):
    """
    Testes da leitura e normalização de parâmetros.
    """

    def test_string_parameter(self):
        """
        Deve ler corretamente um parâmetro String.
        """

        parameter = FakeParameter(
            name="Painel",
            storage_type="String",
            value="QD-01",
            is_read_only=True,
        )

        info = read_parameter_info(
            parameter
        )

        self.assertEqual(
            info["name"],
            "Painel",
        )

        self.assertEqual(
            info["storage_type"],
            "String",
        )

        self.assertEqual(
            info["raw_value"],
            "QD-01",
        )

        self.assertEqual(
            info["display_value"],
            "QD-01",
        )

        self.assertTrue(
            info["is_read_only"]
        )

    def test_integer_parameter(self):
        """
        Deve ler corretamente um parâmetro Integer.
        """

        parameter = FakeParameter(
            name="Número",
            storage_type="Integer",
            value=15,
        )

        info = read_parameter_info(
            parameter
        )

        self.assertEqual(
            info["raw_value"],
            15,
        )

        self.assertEqual(
            info["display_value"],
            "15",
        )

    def test_double_parameter_uses_formatted_value(self):
        """
        Double deve preservar o valor bruto e utilizar a representação
        formatada quando AsValueString() estiver disponível.
        """

        parameter = FakeParameter(
            name="Elevação",
            storage_type="Double",
            value=0.9842519685,
            value_string="300 mm",
        )

        info = read_parameter_info(
            parameter
        )

        self.assertAlmostEqual(
            info["raw_value"],
            0.9842519685,
        )

        self.assertEqual(
            info["display_value"],
            "300 mm",
        )

    def test_element_id_parameter(self):
        """
        Deve converter um parâmetro ElementId para inteiro.
        """

        parameter = FakeParameter(
            name="Nível",
            storage_type="ElementId",
            value=1234,
        )

        info = read_parameter_info(
            parameter
        )

        self.assertEqual(
            info["raw_value"],
            1234,
        )

        self.assertEqual(
            info["display_value"],
            "1234",
        )

    def test_parameter_without_value(self):
        """
        Parâmetros sem valor devem retornar None no valor bruto
        e N/D na apresentação.
        """

        parameter = FakeParameter(
            name="Comentários",
            storage_type="String",
            value=None,
            has_value=False,
        )

        info = read_parameter_info(
            parameter
        )

        self.assertIsNone(
            info["raw_value"]
        )

        self.assertEqual(
            info["display_value"],
            "N/D",
        )

        self.assertFalse(
            info["has_value"]
        )

    def test_element_parameters_are_sorted(self):
        """
        Os parâmetros retornados devem estar em ordem alfabética,
        independentemente da ordem recebida da API.
        """

        element = FakeElement([
            FakeParameter(
                name="Tensão",
                storage_type="Double",
                value=127.0,
            ),
            FakeParameter(
                name="Circuito",
                storage_type="String",
                value="C1",
            ),
            FakeParameter(
                name="Painel",
                storage_type="String",
                value="QD-01",
            ),
        ])

        parameters = read_element_parameters(
            element
        )

        names = [
            parameter["name"]
            for parameter in parameters
        ]

        self.assertEqual(
            names,
            [
                "Circuito",
                "Painel",
                "Tensão",
            ],
        )


if __name__ == "__main__":
    unittest.main()