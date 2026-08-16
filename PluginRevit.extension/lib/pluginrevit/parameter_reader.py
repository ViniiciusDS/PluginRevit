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


def read_parameter_info(parameter):
    """
    Extrai informações normalizadas de um único parâmetro.

    Args:
        parameter:
            Objeto compatível com Autodesk.Revit.DB.Parameter.

    Returns:
        dict:
            Estrutura contendo:

            {
                "name": ...,
                "storage_type": ...,
                "raw_value": ...,
                "display_value": ...,
                "has_value": ...,
                "is_read_only": ...
            }

    Notes:
        Esta função não altera o parâmetro.
        Nenhuma operação Set() é realizada.
    """

    if parameter is None:
        raise ValueError(
            "Nenhum parâmetro foi fornecido para leitura."
        )

    # --------------------------------------------------------------
    # Nome do parâmetro
    # --------------------------------------------------------------

    try:
        definition = parameter.Definition
        parameter_name = str(definition.Name)

    except Exception:
        parameter_name = "N/D"

    # --------------------------------------------------------------
    # Tipo de armazenamento
    # --------------------------------------------------------------

    storage_type = _get_storage_type_name(parameter)

    # --------------------------------------------------------------
    # Presença de valor
    # --------------------------------------------------------------

    has_value = _parameter_has_value(parameter)

    # --------------------------------------------------------------
    # Valor bruto
    # --------------------------------------------------------------

    raw_value = _read_raw_parameter_value(
        parameter,
        storage_type,
    )

    # --------------------------------------------------------------
    # Valor para apresentação
    # --------------------------------------------------------------

    display_value = _read_display_parameter_value(
        parameter,
        storage_type,
        raw_value,
    )

    # --------------------------------------------------------------
    # Estado de edição
    #
    # Isso será importante futuramente quando o plugin começar a
    # modificar parâmetros.
    # --------------------------------------------------------------

    try:
        is_read_only = bool(parameter.IsReadOnly)
    except Exception:
        is_read_only = True

    return {
        "name": parameter_name,
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