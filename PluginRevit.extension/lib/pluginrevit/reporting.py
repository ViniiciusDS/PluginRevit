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