# -*- coding: utf-8 -*-

"""
Comando de desenvolvimento para inspecionar um elemento selecionado no Revit.

Etapa 1A do PluginRevit.

Fluxo:
    1. Obtém a seleção atual do Revit.
    2. Valida se existe algum elemento selecionado.
    3. Utiliza o primeiro elemento da seleção.
    4. Extrai informações básicas através de revit_reader.py.
    5. Converte os dados para uma tabela através de reporting.py.
    6. Exibe o resultado na janela de output do pyRevit.

Este comando é somente leitura.
Nenhum elemento do modelo é criado, editado ou removido.
"""

import traceback

from pyrevit import forms, revit, script


# ----------------------------------------------------------------------
# Objetos de diagnóstico do pyRevit.
#
# O output será utilizado tanto para mostrar o resultado normal quanto
# para apresentar informações detalhadas caso aconteça algum erro.
# ----------------------------------------------------------------------

output = script.get_output()
logger = script.get_logger()


def main():
    """
    Executa o fluxo principal do comando Inspecionar Elemento.

    Returns:
        None

    Notes:
        Primeiro validamos a seleção.

        As funções responsáveis por processar o elemento são importadas
        somente depois que sabemos que existe algo válido para analisar.
    """

    try:

        # --------------------------------------------------------------
        # 1. Obter seleção atual
        # --------------------------------------------------------------

        selection = revit.get_selection()

        # --------------------------------------------------------------
        # 2. Validar seleção
        # --------------------------------------------------------------

        if selection.is_empty:

            forms.alert(
                "Selecione um elemento no modelo antes de executar "
                "este comando.",
                title="PluginRevit - Inspecionar Elemento",
                warn_icon=True,
            )

            return

        # --------------------------------------------------------------
        # 3. Importar módulos necessários para processar o elemento
        # --------------------------------------------------------------

        from pluginrevit.reporting import build_element_info_rows
        from pluginrevit.revit_reader import read_basic_element_info

        # --------------------------------------------------------------
        # 4. Obter primeiro elemento da seleção
        # --------------------------------------------------------------

        element = selection.first

        # --------------------------------------------------------------
        # 5. Ler informações
        # --------------------------------------------------------------

        element_info = read_basic_element_info(element)

        # --------------------------------------------------------------
        # 6. Preparar relatório
        # --------------------------------------------------------------

        table_rows = build_element_info_rows(element_info)

        # --------------------------------------------------------------
        # 7. Exibir resultado
        # --------------------------------------------------------------

        output.set_title(
            "PluginRevit - Inspecionar Elemento"
        )

        output.print_md(
            "# Inspeção de Elemento"
        )

        output.print_md(
            "Informações básicas obtidas do primeiro elemento "
            "selecionado no modelo."
        )

        output.print_table(
            table_data=table_rows,
            columns=["Campo", "Valor"],
        )

    except Exception:

        error_traceback = traceback.format_exc()

        logger.error(error_traceback)

        output.set_title(
            "PluginRevit - Erro"
        )

        output.print_md(
            "# Erro ao executar Inspecionar Elemento"
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

# ----------------------------------------------------------------------
# Entrada do comando
# ----------------------------------------------------------------------

main()