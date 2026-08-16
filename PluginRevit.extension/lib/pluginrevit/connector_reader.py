# -*- coding: utf-8 -*-

"""
Funções responsáveis pela leitura da infraestrutura MEP dos elementos.

Etapa 2A do PluginRevit.

Este módulo inicia a análise estrutural de conectividade dos componentes.

Fluxo atual:

    Element
        ↓
    MEPModel
        ↓
    ConnectorManager
        ↓
    Connectors

Nesta primeira etapa ainda não analisamos as propriedades individuais
dos conectores.

O objetivo é apenas verificar se a infraestrutura necessária existe
e quantos conectores estão disponíveis.

O módulo evita imports diretos da Revit API sempre que possível para
facilitar os testes unitários fora do Revit.
"""


def _get_connector_collection_size(connector_collection):
    """
    Obtém a quantidade de conectores presente em uma coleção.

    Args:
        connector_collection:
            Objeto compatível com a coleção Connectors do Revit.

    Returns:
        int ou None:
            Quantidade encontrada.

            Retorna 0 quando a coleção é None.

            Retorna None caso exista uma coleção, mas não seja possível
            determinar sua quantidade.

    Notes:
        A coleção utilizada pela Revit API normalmente possui a propriedade
        Size.

        Mantemos também um fallback por iteração para deixar a função mais
        robusta e facilitar testes com objetos Python simulados.
    """

    if connector_collection is None:
        return 0

    # --------------------------------------------------------------
    # Estratégia principal: propriedade Size da coleção Revit.
    # --------------------------------------------------------------

    try:
        return int(
            connector_collection.Size
        )

    except Exception:
        pass

    # --------------------------------------------------------------
    # Fallback:
    # tenta contar os itens percorrendo a coleção.
    # --------------------------------------------------------------

    try:
        return sum(
            1
            for _ in connector_collection
        )

    except Exception:
        return None


def read_mep_connection_summary(element):
    """
    Analisa a infraestrutura MEP básica de um elemento.

    Args:
        element:
            Elemento do Revit que será analisado.

    Returns:
        dict:
            Estrutura normalizada:

            {
                "has_mep_model": bool,
                "has_connector_manager": bool,
                "has_connector_collection": bool,
                "connector_count": int ou None
            }

    Raises:
        ValueError:
            Caso nenhum elemento seja fornecido.

    Notes:
        Esta função é SOMENTE LEITURA.

        Nenhuma Transaction é criada e nenhuma informação do modelo
        Revit é modificada.

        A ausência de MEPModel ou ConnectorManager não é tratada como
        exceção. Ela é um resultado válido da análise.
    """

    if element is None:
        raise ValueError(
            "Nenhum elemento foi fornecido para análise MEP."
        )

    # ==============================================================
    # 1. MEPModel
    # ==============================================================
    #
    # Nem todo FamilyInstance possui infraestrutura MEP.
    # Portanto a ausência de MEPModel é um cenário esperado.
    # ==============================================================

    mep_model = getattr(
        element,
        "MEPModel",
        None,
    )

    if mep_model is None:

        return {
            "has_mep_model": False,
            "has_connector_manager": False,
            "has_connector_collection": False,
            "connector_count": 0,
        }

    # ==============================================================
    # 2. ConnectorManager
    # ==============================================================

    connector_manager = getattr(
        mep_model,
        "ConnectorManager",
        None,
    )

    if connector_manager is None:

        return {
            "has_mep_model": True,
            "has_connector_manager": False,
            "has_connector_collection": False,
            "connector_count": 0,
        }

    # ==============================================================
    # 3. Coleção de conectores
    # ==============================================================

    connector_collection = getattr(
        connector_manager,
        "Connectors",
        None,
    )

    if connector_collection is None:

        return {
            "has_mep_model": True,
            "has_connector_manager": True,
            "has_connector_collection": False,
            "connector_count": 0,
        }

    # ==============================================================
    # 4. Quantidade de conectores
    # ==============================================================

    connector_count = _get_connector_collection_size(
        connector_collection
    )

    return {
        "has_mep_model": True,
        "has_connector_manager": True,
        "has_connector_collection": True,
        "connector_count": connector_count,
    }