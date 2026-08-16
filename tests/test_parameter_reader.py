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

class FakeBuiltInParameter(object):
    """
    Simula um valor do enum Autodesk.Revit.DB.BuiltInParameter.
    """

    def __init__(
        self,
        name,
        numeric_value=-1,
    ):
        self.name = name
        self.numeric_value = numeric_value

    def ToString(self):
        return self.name

    def __int__(self):
        return self.numeric_value


class FakeForgeTypeId(object):
    """
    Simula Autodesk.Revit.DB.ForgeTypeId.
    """

    def __init__(
        self,
        type_id,
    ):
        self.TypeId = type_id

class FakeDefinition(object):
    """
    Simula a Definition associada a um Parameter.

    Além do nome, esta versão permite testar informações de identidade
    introduzidas na Etapa 1C.
    """

    def __init__(
        self,
        name,
        built_in_parameter="INVALID",
        built_in_numeric_value=-1,
        data_type_id=None,
        definition_id=None,
    ):
        self.Name = name

        self.BuiltInParameter = FakeBuiltInParameter(
            built_in_parameter,
            built_in_numeric_value,
        )

        self._data_type_id = data_type_id

        if definition_id is not None:
            self.Id = FakeElementId(
                definition_id
            )

    def GetDataType(self):
        """
        Simula Definition.GetDataType().
        """

        if self._data_type_id is None:
            return None

        return FakeForgeTypeId(
            self._data_type_id
        )


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
        parameter_id=1000,
        is_shared=False,
        guid=None,
        built_in_parameter="INVALID",
        built_in_numeric_value=-1,
        data_type_id=None,
    ):
        """
        Cria um Parameter falso utilizado pelos testes.

        Args:
            name (str):
                Nome apresentado do parâmetro.

            storage_type (str):
                String, Integer, Double ou ElementId.

            value:
                Valor bruto utilizado pelos métodos As*().

            value_string:
                Representação formatada utilizada por AsValueString().

            has_value (bool):
                Simula Parameter.HasValue.

            is_read_only (bool):
                Simula Parameter.IsReadOnly.

            parameter_id (int):
                ID associado ao parâmetro.

            is_shared (bool):
                Simula Parameter.IsShared.

            guid:
                GUID utilizado quando o parâmetro é compartilhado.

            built_in_parameter (str):
                Nome do BuiltInParameter.

            built_in_numeric_value (int):
                Valor numérico correspondente ao enum BuiltInParameter.

            data_type_id (str):
                TypeId utilizado por Definition.GetDataType().
        """

        self.Definition = FakeDefinition(
            name=name,
            built_in_parameter=built_in_parameter,
            built_in_numeric_value=built_in_numeric_value,
            data_type_id=data_type_id,
        )

        self.StorageType = FakeStorageType(
            storage_type
        )

        self.Id = FakeElementId(
            parameter_id
        )

        self.IsShared = is_shared
        self.GUID = guid

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

    def test_builtin_parameter_identity(self):
        """
        Deve identificar corretamente um parâmetro built-in.
        """

        parameter = FakeParameter(
            name="Painel",
            storage_type="String",
            value="QDC",
            parameter_id=-1140123,
            built_in_parameter="RBS_ELEC_PANEL_NAME",
            built_in_numeric_value=-1140123,
            data_type_id="autodesk.spec:string",
        )

        info = read_parameter_info(
            parameter
        )

        self.assertEqual(
            info["parameter_id"],
            -1140123,
        )

        self.assertEqual(
            info["identity_kind"],
            "BuiltIn",
        )

        self.assertEqual(
            info["built_in_parameter"],
            "RBS_ELEC_PANEL_NAME",
        )

        self.assertFalse(
            info["is_shared"]
        )

        self.assertIsNone(
            info["guid"]
        )

        self.assertEqual(
            info["data_type_id"],
            "autodesk.spec:string",
        )

    def test_shared_parameter_identity(self):
        """
        Deve identificar corretamente um Shared Parameter e preservar
        seu GUID.
        """

        guid = (
            "12345678-1234-1234-1234-123456789abc"
        )

        parameter = FakeParameter(
            name="ID do comando",
            storage_type="String",
            value="d",
            parameter_id=250001,
            is_shared=True,
            guid=guid,
            data_type_id="autodesk.spec:string",
        )

        info = read_parameter_info(
            parameter
        )

        self.assertEqual(
            info["identity_kind"],
            "Shared",
        )

        self.assertTrue(
            info["is_shared"]
        )

        self.assertEqual(
            info["guid"],
            guid,
        )

        self.assertIsNone(
            info["built_in_parameter"]
        )

    def test_custom_parameter_identity(self):
        """
        Um parâmetro que não seja built-in nem shared deve ser
        classificado como Custom/Other.
        """

        parameter = FakeParameter(
            name="RN1",
            storage_type="Double",
            value=0.041,
            parameter_id=250100,
            data_type_id="autodesk.spec:number",
        )

        info = read_parameter_info(
            parameter
        )

        self.assertEqual(
            info["identity_kind"],
            "Custom/Other",
        )

        self.assertEqual(
            info["parameter_id"],
            250100,
        )

        self.assertFalse(
            info["is_shared"]
        )

        self.assertIsNone(
            info["guid"]
        )

        self.assertIsNone(
            info["built_in_parameter"]
        )

    def test_missing_data_type_returns_none(self):
        """
        A ausência de DataType não deve impedir a leitura do parâmetro.
        """

        parameter = FakeParameter(
            name="Parâmetro Teste",
            storage_type="String",
            value="abc",
            data_type_id=None,
        )

        info = read_parameter_info(
            parameter
        )

        self.assertIsNone(
            info["data_type_id"]
        )

    def test_same_name_parameters_preserve_distinct_ids(self):
        """
        Dois parâmetros com o mesmo nome devem continuar distinguíveis
        através de sua identidade.

        Esse cenário reproduz situações reais observadas no Revit,
        como dois parâmetros chamados "Nível" no mesmo elemento.
        """

        element = FakeElement([
            FakeParameter(
                name="Nível",
                storage_type="ElementId",
                value=500,
                parameter_id=-100001,
                built_in_parameter="LEVEL_PARAM_A",
                built_in_numeric_value=-100001,
            ),
            FakeParameter(
                name="Nível",
                storage_type="ElementId",
                value=500,
                parameter_id=-100002,
                built_in_parameter="LEVEL_PARAM_B",
                built_in_numeric_value=-100002,
            ),
        ])

        parameters = read_element_parameters(
            element
        )

        self.assertEqual(
            len(parameters),
            2,
        )

        parameter_ids = {
            item["parameter_id"]
            for item in parameters
        }

        self.assertEqual(
            parameter_ids,
            {
                -100001,
                -100002,
            },
        )


if __name__ == "__main__":
    unittest.main()