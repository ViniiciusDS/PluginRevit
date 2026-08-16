# -*- coding: utf-8 -*-

"""
Funções responsáveis pela preparação dos dados exibidos ao usuário.

Este módulo recebe estruturas Python simples e transforma essas informações
em dados adequados para apresentação em tabelas ou relatórios.

IMPORTANTE:
Este arquivo não depende diretamente da Revit API. Essa separação permite
testar a lógica de apresentação fora do Revit utilizando unittest.
"""


# ----------------------------------------------------------------------
# Campos que serão exibidos na inspeção básica de um elemento.
#
# Cada tupla contém:
#     ("Nome apresentado ao usuário", "chave no dicionário")
#
# A ordem definida aqui também determina a ordem das linhas da tabela.
# ----------------------------------------------------------------------

ELEMENT_INFO_FIELDS = (
    ("ID", "id"),
    ("Unique ID", "unique_id"),
    ("Categoria", "category"),
    ("Família", "family"),
    ("Tipo", "type"),
    ("Classe API", "api_class"),
)


def _normalize_display_value(value):
    """
    Normaliza valores antes de apresentá-los ao usuário.

    Args:
        value:
            Valor que será exibido na interface ou relatório.

    Returns:
        str:
            Valor convertido para texto.

            Caso o valor seja None ou uma string vazia, retorna "N/D".

    Notes:
        O valor numérico 0 é válido e deve ser preservado.
        Por isso não utilizamos simplesmente:

            if not value:

        pois isso também consideraria 0 como um valor ausente.
    """

    if value is None or value == "":
        return "N/D"

    return str(value)


def build_element_info_rows(element_info):
    """
    Converte informações normalizadas de um elemento em linhas de tabela.

    Args:
        element_info (dict):
            Dicionário contendo informações básicas de um elemento.

            Exemplo:
                {
                    "id": 12345,
                    "unique_id": "abc-123",
                    "category": "Tomadas elétricas",
                    "family": "Tomada 2P+T",
                    "type": "10 A",
                    "api_class": "FamilyInstance",
                }

    Returns:
        list:
            Lista bidimensional pronta para ser utilizada pelo
            output.print_table() do pyRevit.

            Exemplo:
                [
                    ["ID", "12345"],
                    ["Categoria", "Tomadas elétricas"],
                    ...
                ]

    Raises:
        TypeError:
            Caso element_info não seja um dicionário.
    """

    if not isinstance(element_info, dict):
        raise TypeError("element_info deve ser um dicionário.")

    rows = []

    # Percorre os campos na ordem definida em ELEMENT_INFO_FIELDS.
    for label, key in ELEMENT_INFO_FIELDS:

        # .get() evita KeyError caso alguma informação esteja ausente.
        value = element_info.get(key)

        rows.append([
            label,
            _normalize_display_value(value),
        ])

    return rows


# ======================================================================
# Relatórios de parâmetros
# ======================================================================


def _format_boolean(value):
    """
    Converte valores booleanos para uma representação amigável.

    Args:
        value:
            Valor que será convertido.

            Normalmente será True ou False.

    Returns:
        str:
            "Sim" para True.
            "Não" para False.
            "N/D" caso o valor seja None.

    Notes:
        Esta função existe para manter a interface do plugin em português
        e evitar que detalhes internos do Python, como True e False,
        apareçam diretamente para o usuário.
    """

    if value is None:
        return "N/D"

    return "Sim" if bool(value) else "Não"


def build_parameter_rows(parameter_infos):
    """
    Converte informações de parâmetros em linhas de tabela.

    Args:
        parameter_infos (list):
            Lista de dicionários produzidos por
            parameter_reader.read_element_parameters().

            Cada item deve possuir, idealmente:

                {
                    "name": ...,
                    "storage_type": ...,
                    "raw_value": ...,
                    "display_value": ...,
                    "has_value": ...,
                    "is_read_only": ...
                }

    Returns:
        list:
            Lista bidimensional pronta para ser utilizada pelo
            output.print_table() do pyRevit.

            Exemplo:

                [
                    [
                        "Circuito",
                        "C1",
                        "C1",
                        "String",
                        "Sim",
                        "Sim"
                    ],
                    ...
                ]

    Raises:
        TypeError:
            Caso parameter_infos não seja uma lista ou tupla.

            Também é gerado caso algum item da coleção não seja
            um dicionário.

    Notes:
        A função não ordena os parâmetros.

        A ordenação é responsabilidade de parameter_reader.py,
        pois é naquela camada que os dados são normalizados.

        Dessa forma, reporting.py apenas apresenta os dados na
        ordem em que foram recebidos.
    """

    # ------------------------------------------------------------------
    # Validação da coleção recebida.
    # ------------------------------------------------------------------

    if not isinstance(parameter_infos, (list, tuple)):
        raise TypeError(
            "parameter_infos deve ser uma lista ou tupla."
        )

    rows = []

    # ------------------------------------------------------------------
    # Cada dicionário representa um Parameter já normalizado pelo
    # parameter_reader.py.
    # ------------------------------------------------------------------

    for index, parameter_info in enumerate(parameter_infos):

        if not isinstance(parameter_info, dict):
            raise TypeError(
                "O parâmetro na posição {0} deve ser um dicionário.".format(
                    index
                )
            )

        # --------------------------------------------------------------
        # Nome
        # --------------------------------------------------------------

        name = _normalize_display_value(
            parameter_info.get("name")
        )

        # --------------------------------------------------------------
        # Valor apresentado no Revit.
        #
        # Exemplo:
        #
        #     raw_value     = 0.9842519685
        #     display_value = "300 mm"
        #
        # Para o usuário, display_value normalmente será mais útil.
        # --------------------------------------------------------------

        display_value = _normalize_display_value(
            parameter_info.get("display_value")
        )

        # --------------------------------------------------------------
        # Valor bruto.
        #
        # Mantemos este valor visível porque estamos construindo
        # inicialmente uma ferramenta de diagnóstico/desenvolvimento.
        #
        # Mais tarde, na interface destinada ao usuário final, talvez
        # essa coluna não seja necessária.
        # --------------------------------------------------------------

        raw_value = _normalize_display_value(
            parameter_info.get("raw_value")
        )

        # --------------------------------------------------------------
        # StorageType.
        #
        # Exemplos:
        #     String
        #     Integer
        #     Double
        #     ElementId
        # --------------------------------------------------------------

        storage_type = _normalize_display_value(
            parameter_info.get("storage_type")
        )

        # --------------------------------------------------------------
        # Informações de estado.
        # --------------------------------------------------------------

        has_value = _format_boolean(
            parameter_info.get("has_value")
        )

        is_read_only = _format_boolean(
            parameter_info.get("is_read_only")
        )

        rows.append([
            name,
            display_value,
            raw_value,
            storage_type,
            has_value,
            is_read_only,
        ])

    return rows