# -*- coding: utf-8 -*-

"""
Comando de desenvolvimento para inspecionar a infraestrutura MEP
de um elemento selecionado no Revit.

Etapa 2A.3 do PluginRevit.

Fluxo:
    1. Obtém a seleção atual.
    2. Valida se existe elemento selecionado.
    3. Lê informações básicas do elemento.
    4. Analisa MEPModel / ConnectorManager / Connectors.
    5. Prepara os dados para relatório.
    6. Exibe o resultado no output do pyRevit.

Este comando é SOMENTE LEITURA.

Nenhuma Transaction é aberta e nenhuma alteração é realizada
no modelo Revit.
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
    Executa o fluxo principal do comando Inspecionar MEP.

    Returns:
        None

    Notes:
        As importações internas do PluginRevit são feitas somente após
        validar a seleção.

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
                title="PluginRevit - Inspecionar MEP",
                warn_icon=True,
            )

            return

        # ==============================================================
        # 3. Importar módulos internos
        # ==============================================================

        from pluginrevit.connector_reader import (
            read_mep_connection_summary,
        )

        from pluginrevit.reporting import (
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
        # 5. Ler informações básicas
        # ==============================================================

        element_info = read_basic_element_info(
            element
        )

        element_rows = build_element_info_rows(
            element_info
        )

        # ==============================================================
        # 6. Analisar infraestrutura MEP
        # ==============================================================
        #
        # Nesta etapa não analisamos ainda cada Connector.
        #
        # Queremos apenas descobrir:
        #
        #     existe MEPModel?
        #     existe ConnectorManager?
        #     existe coleção Connectors?
        #     quantos conectores existem?
        # ==============================================================

        mep_summary = read_mep_connection_summary(
            element
        )

        # ==============================================================
        # 7. Preparar relatório MEP
        # ==============================================================

        mep_rows = build_mep_summary_rows(
            mep_summary
        )

        # ==============================================================
        # 8. Configurar janela de saída
        # ==============================================================

        output.set_title(
            "PluginRevit - Inspecionar MEP"
        )

        output.print_md(
            "# Inspeção MEP"
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
        # 10. Infraestrutura MEP
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
        # 11. Observação de desenvolvimento
        # ==============================================================
        #
        # Ainda NÃO classificamos o elemento como correto ou incorreto.
        #
        # Esta etapa é apenas exploratória.
        # ==============================================================

        output.print_md(
            "*Nesta etapa o PluginRevit apenas inspeciona a estrutura MEP. "
            "Nenhuma regra de auditoria foi aplicada.*"
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
            "# Erro ao executar Inspecionar MEP"
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