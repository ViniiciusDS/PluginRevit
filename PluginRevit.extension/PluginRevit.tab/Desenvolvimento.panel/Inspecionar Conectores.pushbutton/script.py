# -*- coding: utf-8 -*-

"""
Comando de desenvolvimento para inspecionar individualmente os conectores
MEP de um elemento selecionado no Revit.

Etapa 2B.3 do PluginRevit.

Fluxo:
    1. Obtém a seleção atual do Revit.
    2. Valida se existe algum elemento selecionado.
    3. Lê as informações básicas do elemento.
    4. Analisa a infraestrutura MEP.
    5. Lê individualmente todos os conectores disponíveis.
    6. Prepara os dados para apresentação.
    7. Exibe as informações no output do pyRevit.

Nesta etapa TODOS os conectores são apresentados.

Ainda não são aplicados filtros por:
    - Domain;
    - ConnectorType;
    - estado de conexão;
    - MEPSystem.

O objetivo atual é entender a estrutura real das famílias utilizadas
no projeto antes de definir regras de auditoria.

Este comando é SOMENTE LEITURA.
Nenhuma Transaction é aberta e nenhuma alteração é realizada no modelo.
"""

import traceback

from pyrevit import forms, revit, script


# ======================================================================
# Infraestrutura de diagnóstico
# ======================================================================

output = script.get_output()
logger = script.get_logger()


def main():
    """
    Executa o fluxo principal do comando Inspecionar Conectores.

    Returns:
        None

    Notes:
        Os módulos internos do PluginRevit são importados somente depois
        da validação da seleção.

        Isso mantém o comportamento "sem seleção" independente das
        demais camadas do plugin.
    """

    try:

        # ==============================================================
        # 1. Obter seleção atual
        # ==============================================================

        selection = revit.get_selection()

        # ==============================================================
        # 2. Validar seleção
        # ==============================================================

        if selection.is_empty:

            forms.alert(
                "Selecione um elemento no modelo antes de executar "
                "este comando.",
                title="PluginRevit - Inspecionar Conectores",
                warn_icon=True,
            )

            return

        # ==============================================================
        # 3. Importar módulos internos
        # ==============================================================

        from pluginrevit.connector_reader import (
            read_element_connectors,
            read_mep_connection_summary,
        )

        from pluginrevit.reporting import (
            build_connector_rows,
            build_element_info_rows,
            build_mep_summary_rows,
        )

        from pluginrevit.revit_reader import (
            read_basic_element_info,
        )

        # ==============================================================
        # 4. Obter primeiro elemento selecionado
        # ==============================================================

        element = selection.first

        # ==============================================================
        # 5. Informações básicas do elemento
        # ==============================================================

        element_info = read_basic_element_info(
            element
        )

        element_rows = build_element_info_rows(
            element_info
        )

        # ==============================================================
        # 6. Resumo da infraestrutura MEP
        # ==============================================================

        mep_summary = read_mep_connection_summary(
            element
        )

        mep_rows = build_mep_summary_rows(
            mep_summary
        )

        # ==============================================================
        # 7. Ler individualmente os conectores
        # ==============================================================
        #
        # Nesta etapa nenhum filtro é aplicado.
        #
        # Queremos visualizar exatamente a coleção entregue pela API.
        # ==============================================================

        connector_infos = read_element_connectors(
            element
        )

        connector_rows = build_connector_rows(
            connector_infos
        )

        # ==============================================================
        # 8. Configurar output
        # ==============================================================

        output.set_title(
            "PluginRevit - Inspecionar Conectores"
        )

        output.print_md(
            "# Inspeção de Conectores"
        )

        # ==============================================================
        # 9. Elemento selecionado
        # ==============================================================

        output.print_md(
            "## Elemento selecionado"
        )

        output.print_table(
            table_data=element_rows,
            columns=[
                "Campo",
                "Valor",
            ],
        )

        # ==============================================================
        # 10. Resumo MEP
        # ==============================================================

        output.print_md(
            "## Infraestrutura MEP"
        )

        output.print_table(
            table_data=mep_rows,
            columns=[
                "Verificação",
                "Resultado",
            ],
        )

        # ==============================================================
        # 11. Conectores encontrados
        # ==============================================================

        output.print_md(
            "## Conectores individuais"
        )

        output.print_md(
            "**Quantidade encontrada: {0}**".format(
                len(connector_infos)
            )
        )

        # ==============================================================
        # 12. Tabela individual
        # ==============================================================

        if connector_rows:

            output.print_table(
                table_data=connector_rows,
                columns=[
                    "#",
                    "Domain",
                    "ConnectorType",
                    "Conectado?",
                    "MEPSystem?",
                ],
            )

        else:

            # ----------------------------------------------------------
            # Não possuir conectores não representa, nesta etapa,
            # necessariamente um erro.
            #
            # Apenas registramos o resultado observado.
            # ----------------------------------------------------------

            output.print_md(
                "*Nenhum conector foi encontrado neste elemento.*"
            )

        # ==============================================================
        # 13. Observação
        # ==============================================================

        output.print_md(
            "*Nesta etapa nenhum conector foi filtrado ou classificado "
            "como correto/incorreto. A tabela representa os dados brutos "
            "normalizados obtidos da infraestrutura MEP.*"
        )

    except Exception:

        # ==============================================================
        # Tratamento de erros
        # ==============================================================

        error_traceback = traceback.format_exc()

        logger.error(
            error_traceback
        )

        output.set_title(
            "PluginRevit - Erro"
        )

        output.print_md(
            "# Erro ao executar Inspecionar Conectores"
        )

        output.print_md(
            "O comando encontrou um erro inesperado. "
            "Traceback completo:"
        )

        output.print_code(
            error_traceback
        )

        forms.alert(
            "Ocorreu um erro ao executar o comando.\n\n"
            "Consulte a janela de saída do pyRevit "
            "para os detalhes.",
            title="PluginRevit - Erro",
            warn_icon=True,
        )


# ======================================================================
# Entrada do comando
# ======================================================================

main()