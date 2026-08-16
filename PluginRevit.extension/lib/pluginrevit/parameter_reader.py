# -*- coding: utf-8 -*-

"""
Funções responsáveis pela leitura dos parâmetros de elementos do Revit.

Este módulo recebe objetos compatíveis com Autodesk.Revit.DB.Parameter e
transforma suas informações em estruturas Python simples.

Uma decisão importante deste módulo é evitar imports diretos da Revit API.
Isso permite testar a maior parte da lógica fora do Revit utilizando objetos
simulados nos testes unitários.

Fluxo esperado:

    Revit Element
        ↓
    read_element_parameters()
        ↓
    lista de dicionários Python
        ↓
    camada de relatório/interface
"""


def _get_element_id_value(element_id):
    """
    Converte um ElementId para um valor Python simples.

    Args:
        element_id:
            Objeto compatível com Autodesk.Revit.DB.ElementId.

    Returns:
        int ou None:
            Valor numérico do ElementId.

            Retorna None caso o valor não possa ser obtido.

    Notes:
        Diferentes versões da Revit API podem expor o valor através de
        propriedades diferentes. Por isso utilizamos mais de uma tentativa.
    """

    if element_id is None:
        return None

    # --------------------------------------------------------------
    # API mais recente.
    # --------------------------------------------------------------

    try:
        return int(element_id.Value)
    except Exception:
        pass

    # --------------------------------------------------------------
    # Fallback para versões anteriores.
    # --------------------------------------------------------------

    try:
        return int(element_id.IntegerValue)
    except Exception:
        return None


def _get_storage_type_name(parameter):
    """
    Obtém o nome do StorageType de um parâmetro.

    Args:
        parameter:
            Objeto compatível com Autodesk.Revit.DB.Parameter.

    Returns:
        str:
            Nome do tipo de armazenamento.

            Exemplos:
                "String"
                "Integer"
                "Double"
                "ElementId"
                "None"
    """

    try:
        storage_type = parameter.StorageType
    except Exception:
        return "Unknown"

    # --------------------------------------------------------------
    # StorageType é um enum .NET.
    #
    # ToString() normalmente retorna diretamente:
    #
    #     String
    #     Integer
    #     Double
    #     ElementId
    # --------------------------------------------------------------

    try:
        return str(storage_type.ToString())
    except Exception:
        pass

    # --------------------------------------------------------------
    # Fallback caso o objeto não exponha ToString().
    # --------------------------------------------------------------

    try:
        storage_name = str(storage_type)

        # Caso recebamos algo semelhante a:
        #
        #     StorageType.String
        #
        # mantemos apenas:
        #
        #     String
        return storage_name.split(".")[-1]

    except Exception:
        return "Unknown"


def _parameter_has_value(parameter):
    """
    Verifica se um parâmetro possui valor.

    Args:
        parameter:
            Objeto compatível com Autodesk.Revit.DB.Parameter.

    Returns:
        bool:
            True caso exista um valor armazenado.
            False caso o parâmetro esteja vazio.

    Notes:
        O fallback retorna True porque versões/objetos que não exponham
        HasValue ainda podem permitir a leitura através de AsString(),
        AsInteger(), AsDouble() etc.
    """

    try:
        return bool(parameter.HasValue)
    except Exception:
        return True


def _read_raw_parameter_value(parameter, storage_type):
    """
    Lê o valor bruto de um parâmetro conforme seu StorageType.

    Args:
        parameter:
            Objeto compatível com Autodesk.Revit.DB.Parameter.

        storage_type (str):
            Nome normalizado do StorageType.

    Returns:
        str, int, float ou None:
            Valor armazenado no parâmetro sem formatação para apresentação.

    Notes:
        Para parâmetros Double, o valor bruto utiliza as unidades internas
        do Revit. A conversão para uma representação amigável é tratada
        separadamente em _read_display_parameter_value().
    """

    if not _parameter_has_value(parameter):
        return None

    try:

        if storage_type == "String":
            return parameter.AsString()

        if storage_type == "Integer":
            return int(parameter.AsInteger())

        if storage_type == "Double":
            return float(parameter.AsDouble())

        if storage_type == "ElementId":
            return _get_element_id_value(
                parameter.AsElementId()
            )

    except Exception:
        return None

    return None


def _read_display_parameter_value(
    parameter,
    storage_type,
    raw_value,
):
    """
    Obtém uma representação amigável do valor do parâmetro.

    Args:
        parameter:
            Objeto compatível com Autodesk.Revit.DB.Parameter.

        storage_type (str):
            Tipo de armazenamento normalizado.

        raw_value:
            Valor bruto obtido anteriormente.

    Returns:
        str:
            Texto apropriado para exibição ao usuário.

    Notes:
        Para Double e Integer tentamos utilizar AsValueString(), pois essa
        função pode devolver o valor já formatado conforme as unidades e
        configurações do projeto.

        Caso não exista representação formatada, utilizamos o valor bruto.
    """

    if raw_value is None:
        return "N/D"

    # --------------------------------------------------------------
    # Valores numéricos podem possuir uma representação formatada.
    #
    # Exemplo:
    #
    #     bruto:    0.984251...
    #     exibido:  300 mm
    # --------------------------------------------------------------

    if storage_type in ("Double", "Integer"):

        try:
            formatted_value = parameter.AsValueString()

            if formatted_value not in (None, ""):
                return str(formatted_value)

        except Exception:
            pass

    # --------------------------------------------------------------
    # String e ElementId, ou valores numéricos sem uma representação
    # formatada, utilizam diretamente o valor bruto.
    # --------------------------------------------------------------

    if raw_value == "":
        return "N/D"

    return str(raw_value)

def _get_parameter_id_value(parameter):
    """
    Obtém o identificador associado a um parâmetro.

    Args:
        parameter:
            Objeto compatível com Autodesk.Revit.DB.Parameter.

    Returns:
        int ou None:
            ID numérico associado ao parâmetro.

            Para parâmetros built-in, normalmente será um valor negativo.
            Para parâmetros personalizados, normalmente será um ID associado
            ao documento atual.

            Retorna None caso não seja possível determinar o ID.

    Notes:
        Utilizamos múltiplas estratégias para reduzir dependência de uma
        única representação da Revit API.
    """

    if parameter is None:
        return None

    # --------------------------------------------------------------
    # Tentativa principal:
    # Parameter.Id representa diretamente a identidade do parâmetro.
    # --------------------------------------------------------------

    try:
        parameter_id = parameter.Id

        value = _get_element_id_value(
            parameter_id
        )

        if value is not None:
            return value

    except Exception:
        pass

    # --------------------------------------------------------------
    # Fallback para parâmetros built-in.
    #
    # O enum BuiltInParameter também possui um valor numérico que pode
    # representar a identidade do parâmetro.
    # --------------------------------------------------------------

    try:
        definition = parameter.Definition
        built_in_parameter = definition.BuiltInParameter

        return int(built_in_parameter)

    except Exception:
        pass

    # --------------------------------------------------------------
    # Último fallback:
    # parâmetros personalizados podem possuir um ParameterElement
    # associado à InternalDefinition.
    # --------------------------------------------------------------

    try:
        definition_id = parameter.Definition.Id

        return _get_element_id_value(
            definition_id
        )

    except Exception:
        return None


def _get_builtin_parameter_name(parameter):
    """
    Identifica se o parâmetro corresponde a um BuiltInParameter.

    Args:
        parameter:
            Objeto compatível com Autodesk.Revit.DB.Parameter.

    Returns:
        str ou None:
            Nome do BuiltInParameter.

            Exemplo:
                "RBS_ELEC_PANEL_NAME"

            Retorna None quando o parâmetro não é built-in.

    Notes:
        Para parâmetros personalizados, a Revit API utiliza o valor
        BuiltInParameter.INVALID.
    """

    try:
        built_in_parameter = (
            parameter.Definition.BuiltInParameter
        )

    except Exception:
        return None

    # --------------------------------------------------------------
    # Primeiro tentamos utilizar ToString(), pois estamos trabalhando
    # com um enum .NET.
    # --------------------------------------------------------------

    try:
        name = str(
            built_in_parameter.ToString()
        )

    except Exception:

        try:
            name = str(
                built_in_parameter
            ).split(".")[-1]

        except Exception:
            return None

    # --------------------------------------------------------------
    # INVALID significa que a definição não representa um parâmetro
    # built-in.
    # --------------------------------------------------------------

    normalized_name = name.upper()

    if (
        normalized_name == "INVALID"
        or normalized_name.endswith(".INVALID")
    ):
        return None

    return name


def _is_shared_parameter(parameter):
    """
    Verifica se o parâmetro é um Shared Parameter.

    Args:
        parameter:
            Objeto compatível com Autodesk.Revit.DB.Parameter.

    Returns:
        bool:
            True quando o parâmetro é compartilhado.
            False nos demais casos.
    """

    try:
        return bool(
            parameter.IsShared
        )

    except Exception:
        return False


def _get_shared_parameter_guid(
    parameter,
    is_shared,
):
    """
    Obtém o GUID de um Shared Parameter.

    Args:
        parameter:
            Objeto compatível com Autodesk.Revit.DB.Parameter.

        is_shared (bool):
            Resultado previamente obtido por _is_shared_parameter().

    Returns:
        str ou None:
            GUID do parâmetro compartilhado.

            Retorna None para parâmetros que não são Shared Parameters.

    Notes:
        Evitamos acessar Parameter.GUID quando o parâmetro não é
        compartilhado, pois essa informação não é aplicável nesse caso.
    """

    if not is_shared:
        return None

    try:
        guid = parameter.GUID

        if guid is None:
            return None

        guid_text = str(guid)

        if not guid_text:
            return None

        return guid_text

    except Exception:
        return None


def _get_data_type_id(parameter):
    """
    Obtém o identificador do tipo de dado da Definition.

    Args:
        parameter:
            Objeto compatível com Autodesk.Revit.DB.Parameter.

    Returns:
        str ou None:
            TypeId retornado pelo ForgeTypeId associado ao parâmetro.

            Retorna None quando a informação não estiver disponível.

    Notes:
        O data_type_id descreve o significado do dado e não deve ser
        confundido com StorageType.

        StorageType responde COMO o valor é armazenado.

        GetDataType() ajuda a responder O QUE o valor representa.
    """

    try:
        definition = parameter.Definition

        data_type = definition.GetDataType()

        if data_type is None:
            return None

    except Exception:
        return None

    # --------------------------------------------------------------
    # ForgeTypeId normalmente possui a propriedade TypeId.
    # --------------------------------------------------------------

    try:
        type_id = data_type.TypeId

        if type_id:
            return str(type_id)

    except Exception:
        pass

    # --------------------------------------------------------------
    # Fallback defensivo.
    # --------------------------------------------------------------

    try:
        data_type_text = str(data_type)

        if data_type_text:
            return data_type_text

    except Exception:
        pass

    return None


def _classify_parameter_identity(
    built_in_parameter,
    is_shared,
):
    """
    Classifica a origem identificável do parâmetro.

    Args:
        built_in_parameter (str ou None):
            Nome do BuiltInParameter, quando aplicável.

        is_shared (bool):
            Indica se o parâmetro é compartilhado.

    Returns:
        str:
            Uma das classificações:

                "BuiltIn"
                "Shared"
                "Custom/Other"

    Notes:
        Nesta etapa não tentamos distinguir automaticamente parâmetros
        de projeto de parâmetros de família.

        Essa classificação exigiria contexto adicional e será tratada
        somente caso seja necessária para as futuras regras do plugin.
    """

    if built_in_parameter is not None:
        return "BuiltIn"

    if is_shared:
        return "Shared"

    return "Custom/Other"

def read_parameter_info(parameter):
    """
    Extrai informações normalizadas de um único parâmetro.

    Args:
        parameter:
            Objeto compatível com Autodesk.Revit.DB.Parameter.

    Returns:
        dict:
            Dicionário contendo informações de identidade, valor
            e estado do parâmetro.

            Estrutura retornada:

                {
                    "name": ...,
                    "parameter_id": ...,
                    "identity_kind": ...,
                    "built_in_parameter": ...,
                    "is_shared": ...,
                    "guid": ...,
                    "data_type_id": ...,

                    "storage_type": ...,
                    "raw_value": ...,
                    "display_value": ...,
                    "has_value": ...,
                    "is_read_only": ...
                }

    Raises:
        ValueError:
            Caso nenhum parâmetro seja fornecido.

    Notes:
        Esta função é SOMENTE LEITURA.

        Nenhuma chamada Parameter.Set() é realizada e nenhum dado
        do modelo Revit é alterado.
    """

    # ==============================================================
    # 1. Validar entrada
    # ==============================================================

    if parameter is None:
        raise ValueError(
            "Nenhum parâmetro foi fornecido para leitura."
        )

    # ==============================================================
    # 2. Nome apresentado do parâmetro
    # ==============================================================
    #
    # O nome é útil para interface e diagnóstico, mas não será usado
    # sozinho como identidade definitiva do parâmetro.
    # ==============================================================

    try:
        definition = parameter.Definition
        parameter_name = str(
            definition.Name
        )

    except Exception:
        parameter_name = "N/D"

    # ==============================================================
    # 3. Identidade do parâmetro
    # ==============================================================
    #
    # A Etapa 1C adiciona informações que permitem distinguir
    # parâmetros mesmo quando possuem o mesmo nome.
    # ==============================================================

    parameter_id = _get_parameter_id_value(
        parameter
    )

    built_in_parameter = _get_builtin_parameter_name(
        parameter
    )

    is_shared = _is_shared_parameter(
        parameter
    )

    guid = _get_shared_parameter_guid(
        parameter,
        is_shared,
    )

    data_type_id = _get_data_type_id(
        parameter
    )

    identity_kind = _classify_parameter_identity(
        built_in_parameter,
        is_shared,
    )

    # ==============================================================
    # 4. StorageType
    # ==============================================================

    storage_type = _get_storage_type_name(
        parameter
    )

    # ==============================================================
    # 5. Presença de valor
    # ==============================================================

    has_value = _parameter_has_value(
        parameter
    )

    # ==============================================================
    # 6. Valor bruto
    # ==============================================================

    raw_value = _read_raw_parameter_value(
        parameter,
        storage_type,
    )

    # ==============================================================
    # 7. Valor apresentado
    # ==============================================================
    #
    # Para grandezas numéricas, este valor pode estar formatado
    # conforme as unidades e configurações do projeto Revit.
    # ==============================================================

    display_value = _read_display_parameter_value(
        parameter,
        storage_type,
        raw_value,
    )

    # ==============================================================
    # 8. Estado de edição
    # ==============================================================

    try:
        is_read_only = bool(
            parameter.IsReadOnly
        )

    except Exception:

        # Caso não seja possível determinar, adotamos a opção mais
        # conservadora e consideramos o parâmetro somente leitura.
        is_read_only = True

    # ==============================================================
    # 9. Resultado normalizado
    # ==============================================================
    #
    # O restante do PluginRevit recebe apenas uma estrutura Python
    # simples, sem precisar conhecer os detalhes internos da API.
    # ==============================================================

    return {
        # ----------------------------------------------------------
        # Identificação
        # ----------------------------------------------------------

        "name": parameter_name,
        "parameter_id": parameter_id,
        "identity_kind": identity_kind,
        "built_in_parameter": built_in_parameter,
        "is_shared": is_shared,
        "guid": guid,
        "data_type_id": data_type_id,

        # ----------------------------------------------------------
        # Valor e estado
        # ----------------------------------------------------------

        "storage_type": storage_type,
        "raw_value": raw_value,
        "display_value": display_value,
        "has_value": has_value,
        "is_read_only": is_read_only,
    }


def read_element_parameters(element):
    """
    Extrai todos os parâmetros de instância de um elemento.

    Args:
        element:
            Elemento do Revit que será analisado.

    Returns:
        list:
            Lista de dicionários produzidos por read_parameter_info().

    Raises:
        ValueError:
            Caso nenhum elemento seja fornecido.

    Notes:
        Os parâmetros são ordenados alfabeticamente para tornar o resultado
        determinístico e facilitar comparação, debug e testes.

        Nesta etapa estamos analisando somente os parâmetros presentes na
        instância recebida. Parâmetros do ElementType serão tratados
        separadamente em uma etapa futura.
    """

    if element is None:
        raise ValueError(
            "Nenhum elemento foi fornecido para leitura dos parâmetros."
        )

    parameters = []

    # --------------------------------------------------------------
    # Element.Parameters retorna os parâmetros associados ao elemento.
    # --------------------------------------------------------------

    for parameter in element.Parameters:

        parameter_info = read_parameter_info(
            parameter
        )

        parameters.append(
            parameter_info
        )

    # --------------------------------------------------------------
    # ParameterSet não deve definir a ordem apresentada ao usuário.
    #
    # Ordenamos explicitamente pelo nome para garantir resultado
    # previsível em diferentes execuções.
    # --------------------------------------------------------------

    parameters.sort(
        key=lambda item: item["name"].lower()
    )

    return parameters