# -*- coding: utf-8 -*-

"""
Funções responsáveis pela leitura de informações da Revit API.

Este módulo concentra funções que recebem objetos do Revit e extraem
informações em formatos simples do Python.

Objetivo da separação:
    Revit API
        ↓
    revit_reader.py
        ↓
    dados Python normalizados
        ↓
    restante do PluginRevit

Isso evita espalhar acessos diretos à Revit API pelos scripts dos botões
e facilita manutenção, debug e futuras alterações de compatibilidade.
"""

from pyrevit.revit.db import query


def _get_element_id_value(element_id):
    """
    Converte um ElementId do Revit em um valor Python simples.

    Args:
        element_id:
            Autodesk.Revit.DB.ElementId que será convertido.

    Returns:
        int ou str:
            Valor numérico do ElementId.

            Caso não seja possível obter o valor, retorna "N/D".

    Notes:
        O tratamento possui mais de uma tentativa porque diferentes
        versões da Revit API podem expor o valor interno do ElementId
        por propriedades diferentes.
    """

    if element_id is None:
        return "N/D"

    # --------------------------------------------------------------
    # Tentativa principal.
    #
    # Nas versões mais recentes da Revit API, ElementId possui
    # a propriedade Value.
    # --------------------------------------------------------------

    try:
        return int(element_id.Value)
    except Exception:
        pass

    # --------------------------------------------------------------
    # Fallback para versões que utilizam IntegerValue.
    # --------------------------------------------------------------

    try:
        return int(element_id.IntegerValue)
    except Exception:
        return "N/D"


def _safe_get_name(element):
    """
    Obtém o nome de um elemento de maneira segura.

    Args:
        element:
            Elemento da Revit API.

    Returns:
        str:
            Nome do elemento.

            Caso o elemento seja None ou aconteça algum erro durante
            a leitura, retorna "N/D".
    """

    if element is None:
        return "N/D"

    try:
        return query.get_name(element) or "N/D"
    except Exception:
        return "N/D"


def read_basic_element_info(element):
    """
    Extrai informações básicas de um elemento do Revit.

    Esta é a função principal deste módulo na Etapa 1A.

    Args:
        element:
            Autodesk.Revit.DB.Element que será analisado.

    Returns:
        dict:
            Dicionário contendo informações normalizadas:

            {
                "id": ...,
                "unique_id": ...,
                "category": ...,
                "family": ...,
                "type": ...,
                "api_class": ...
            }

    Raises:
        ValueError:
            Caso nenhum elemento válido seja fornecido.

    Notes:
        Esta função é SOMENTE LEITURA.

        Nenhuma Transaction é criada e nenhuma informação do modelo
        Revit é modificada.
    """

    # --------------------------------------------------------------
    # Validação de entrada
    # --------------------------------------------------------------

    if element is None:
        raise ValueError(
            "Nenhum elemento foi fornecido para leitura."
        )

    # --------------------------------------------------------------
    # 1. ID
    # --------------------------------------------------------------

    element_id = _get_element_id_value(element.Id)

    # --------------------------------------------------------------
    # 2. UniqueId
    #
    # Diferente do ElementId, o UniqueId é uma identificação textual
    # persistente utilizada pelo Revit para identificar o elemento.
    # --------------------------------------------------------------

    try:
        unique_id = str(element.UniqueId)
    except Exception:
        unique_id = "N/D"

    # --------------------------------------------------------------
    # 3. Categoria
    # --------------------------------------------------------------

    category = getattr(element, "Category", None)

    if category is not None:
        try:
            category_name = category.Name
        except Exception:
            category_name = "N/D"
    else:
        category_name = "Sem categoria"

    # --------------------------------------------------------------
    # 4. Família e Tipo
    #
    # Elementos baseados em família, como tomadas e luminárias,
    # normalmente são FamilyInstance e possuem a propriedade Symbol.
    #
    # Symbol representa o tipo da família.
    # --------------------------------------------------------------

    symbol = getattr(element, "Symbol", None)

    family_name = "N/D"
    type_name = "N/D"

    if symbol is not None:

        # ----------------------------------------------------------
        # Elemento baseado em FamilyInstance.
        # ----------------------------------------------------------

        try:
            family_name = query.get_family_name(element) or "N/D"
        except Exception:
            family_name = "N/D"

        try:
            type_name = query.get_symbol_name(element) or "N/D"
        except Exception:
            type_name = "N/D"

    else:

        # ----------------------------------------------------------
        # Nem todo elemento do Revit é uma FamilyInstance.
        #
        # Nesse caso tentamos obter seu ElementType diretamente.
        # ----------------------------------------------------------

        try:
            element_type = query.get_type(element)
            type_name = _safe_get_name(element_type)
        except Exception:
            type_name = "N/D"

    # --------------------------------------------------------------
    # 5. Classe da Revit API
    #
    # Exemplos possíveis:
    #     FamilyInstance
    #     Wall
    #     Floor
    #     ElectricalSystem
    # --------------------------------------------------------------

    try:
        api_class = element.GetType().Name
    except Exception:

        # Fallback caso GetType() não esteja disponível.
        api_class = type(element).__name__

    # --------------------------------------------------------------
    # 6. Resultado normalizado
    #
    # O restante do PluginRevit recebe um dict simples, sem precisar
    # conhecer os detalhes internos da Revit API.
    # --------------------------------------------------------------

    return {
        "id": element_id,
        "unique_id": unique_id,
        "category": category_name,
        "family": family_name,
        "type": type_name,
        "api_class": api_class,
    }