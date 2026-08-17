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

def _get_enum_name(enum_value):
    """
    Converte um enum .NET da Revit API para texto.

    Args:
        enum_value:
            Valor de enum proveniente da Revit API.

    Returns:
        str:
            Nome normalizado do enum.

            Exemplos possíveis:
                "DomainElectrical"
                "DomainPiping"
                "End"
                "Logical"

            Retorna "N/D" caso o valor não possa ser lido.

    Notes:
        A Revit API utiliza diversos enums .NET para representar
        propriedades dos conectores.

        Centralizar essa conversão evita repetir blocos try/except
        em várias funções.
    """

    if enum_value is None:
        return "N/D"

    # --------------------------------------------------------------
    # Estratégia principal para enums .NET.
    # --------------------------------------------------------------

    try:
        return str(
            enum_value.ToString()
        )

    except Exception:
        pass

    # --------------------------------------------------------------
    # Fallback para objetos simulados ou outras representações.
    # --------------------------------------------------------------

    try:
        enum_text = str(
            enum_value
        )

        # Exemplo:
        #
        #     Domain.DomainElectrical
        #
        # torna-se:
        #
        #     DomainElectrical
        return enum_text.split(".")[-1]

    except Exception:
        return "N/D"

def read_connector_info(connector, index=None):
    """
    Extrai informações básicas de um Connector do Revit.

    Args:
        connector:
            Objeto compatível com Autodesk.Revit.DB.Connector.

        index (int, optional):
            Posição utilizada apenas para facilitar identificação
            durante diagnóstico e apresentação.

    Returns:
        dict:
            Estrutura normalizada:

                {
                    "index": ...,
                    "domain": ...,
                    "connector_type": ...,
                    "is_connected": ...,
                    "has_mep_system": ...
                }

    Raises:
        ValueError:
            Caso nenhum conector seja fornecido.

    Notes:
        Nesta etapa ainda não percorremos AllRefs e não analisamos
        quem está conectado ao conector.

        Isso será feito depois de entendermos primeiro os tipos de
        conectores existentes nas famílias reais.

        A função é SOMENTE LEITURA.
    """

    if connector is None:
        raise ValueError(
            "Nenhum conector foi fornecido para leitura."
        )

    # ==============================================================
    # 1. Domain
    # ==============================================================
    #
    # Domain permite distinguir a disciplina associada ao conector.
    #
    # Isso será essencial para futuramente selecionarmos apenas
    # conectores elétricos.
    # ==============================================================

    try:
        domain = _get_enum_name(
            connector.Domain
        )

    except Exception:
        domain = "N/D"

    # ==============================================================
    # 2. ConnectorType
    # ==============================================================
    #
    # O Revit possui diferentes tipos de Connector, incluindo
    # conectores físicos e lógicos.
    # ==============================================================

    try:
        connector_type = _get_enum_name(
            connector.ConnectorType
        )

    except Exception:
        connector_type = "N/D"

    # ==============================================================
    # 3. Estado de conexão
    # ==============================================================

    try:
        is_connected = bool(
            connector.IsConnected
        )

    except Exception:
        is_connected = None

    # ==============================================================
    # 4. Sistema MEP
    # ==============================================================
    #
    # Um Connector pode ou não estar associado a um MEPSystem.
    # Nesta etapa armazenamos apenas a existência desse relacionamento.
    # ==============================================================

    try:
        mep_system = connector.MEPSystem

        has_mep_system = (
            mep_system is not None
        )

    except Exception:
        has_mep_system = False

    return {
        "index": index,
        "domain": domain,
        "connector_type": connector_type,
        "is_connected": is_connected,
        "has_mep_system": has_mep_system,
    }


def read_element_connectors(element):
    """
    Lê individualmente todos os conectores disponíveis em um elemento.

    Args:
        element:
            Elemento do Revit que será analisado.

    Returns:
        list:
            Lista contendo um dicionário para cada Connector encontrado.

            Exemplo:

                [
                    {
                        "index": 1,
                        "domain": "DomainElectrical",
                        "connector_type": "Logical",
                        "is_connected": True,
                        "has_mep_system": True
                    },
                    ...
                ]

    Raises:
        ValueError:
            Caso nenhum elemento seja fornecido.

    Notes:
        A função reutiliza a mesma cadeia analisada na Etapa 2A:

            Element
                ↓
            MEPModel
                ↓
            ConnectorManager
                ↓
            Connectors

        Caso qualquer estágio não exista, uma lista vazia é retornada.

        Nenhuma Transaction é aberta.
    """

    if element is None:
        raise ValueError(
            "Nenhum elemento foi fornecido para leitura dos conectores."
        )

    # ==============================================================
    # 1. MEPModel
    # ==============================================================

    mep_model = getattr(
        element,
        "MEPModel",
        None,
    )

    if mep_model is None:
        return []

    # ==============================================================
    # 2. ConnectorManager
    # ==============================================================

    connector_manager = getattr(
        mep_model,
        "ConnectorManager",
        None,
    )

    if connector_manager is None:
        return []

    # ==============================================================
    # 3. Connectors
    # ==============================================================

    connector_collection = getattr(
        connector_manager,
        "Connectors",
        None,
    )

    if connector_collection is None:
        return []

    connectors = []

    # ==============================================================
    # 4. Percorrer a coleção
    # ==============================================================
    #
    # Enumeramos a partir de 1 somente para tornar a futura tabela
    # mais natural para leitura humana.
    # ==============================================================

    for index, connector in enumerate(
        connector_collection,
        start=1,
    ):

        connector_info = read_connector_info(
            connector,
            index=index,
        )

        connectors.append(
            connector_info
        )

    return connectors


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