# -*- coding: utf-8 -*-

"""
Comando de desenvolvimento para inspecionar os parâmetros de instância
de um elemento selecionado no Revit.

Etapa 1B.3 do PluginRevit.

Fluxo:
    1. Obtém a seleção atual do Revit.
    2. Valida se existe algum elemento selecionado.
    3. Utiliza o primeiro elemento selecionado.
    4. Obtém suas informações básicas.
    5. Lê seus parâmetros de instância.
    6. Normaliza os parâmetros.
    7. Prepara as tabelas de apresentação.
    8. Exibe os resultados no output do pyRevit.

Este comando é SOMENTE LEITURA.

Nenhuma Transaction é aberta e nenhum elemento ou parâmetro
do modelo é modificado.
"""

import traceback

from pyrevit import forms, revit, script


# ======================================================================
# Objetos de diagnóstico do pyRevit
# ======================================================================
#
# Mantemos o output e logger desde o início do comando para que qualquer
# erro ocorrido durante o processamento possa ser apresentado com detalhes.
# ======================================================================

output = script.get_output()
logger = script.get_logger()


def main():
    """
    Executa o fluxo principal do comando Inspecionar Parametros.

    Returns:
        None

    Notes:
        As importações dos módulos responsáveis pelo processamento são
        realizadas somente depois da validação da seleção.

        Isso permite que o comportamento "nenhum elemento selecionado"
        continue funcionando mesmo caso exista algum problema em módulos
        posteriores.
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
                title="PluginRevit - Inspecionar Parametros",
                warn_icon=True,
            )

            return

        # ==============================================================
        # 3. Importar módulos internos
        # ==============================================================
        #
        # A leitura e a apresentação permanecem em módulos separados.
        #
        #     Revit
        #       ↓
        #     readers
        #       ↓
        #     dados Python
        #       ↓
        #     reporting
        #       ↓
        #     interface
        #
        # ==============================================================

        from pluginrevit.parameter_reader import (
            read_element_parameters,
        )

        from pluginrevit.reporting import (
            build_element_info_rows,
            build_parameter_rows,
        )

        from pluginrevit.revit_reader import (
            read_basic_element_info,
        )

        # ==============================================================
        # 4. Obter primeiro elemento selecionado
        # ==============================================================
        #
        # Nesta etapa continuamos trabalhando com somente um elemento.
        # Suporte a múltiplos elementos poderá ser adicionado futuramente
        # caso exista uma necessidade real.
        # ==============================================================

        element = selection.first

        # ==============================================================
        # 5. Obter informações básicas do elemento
        # ==============================================================

        element_info = read_basic_element_info(
            element
        )

        element_rows = build_element_info_rows(
            element_info
        )

        # ==============================================================
        # 6. Ler parâmetros de instância
        # ==============================================================

        parameter_infos = read_element_parameters(
            element
        )

        # ==============================================================
        # 7. Preparar parâmetros para apresentação
        # ==============================================================

        parameter_rows = build_parameter_rows(
            parameter_infos
        )

        # ==============================================================
        # 8. Configurar janela de saída
        # ==============================================================

        output.set_title(
            "PluginRevit - Inspecionar Parametros"
        )

        # ==============================================================
        # 9. Informações básicas
        # ==============================================================

        output.print_md(
            "# Inspeção de Parâmetros"
        )

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
        # 10. Parâmetros encontrados
        # ==============================================================

        output.print_md(
            "## Parâmetros de instância"
        )

        output.print_md(
            "**Quantidade encontrada: {0}**".format(
                len(parameter_infos)
            )
        )

        # ==============================================================
        # 11. Exibir tabela
        # ==============================================================

        if parameter_rows:

            output.print_table(
                table_data=parameter_rows,
                columns=[
                    "Parâmetro",
                    "Valor",
                    "Valor bruto",
                    "StorageType",
                    "Tem valor?",
                    "Somente leitura?",
                ],
            )

        else:

            # ----------------------------------------------------------
            # Esse cenário não é um erro.
            #
            # Alguns elementos podem simplesmente não possuir parâmetros
            # acessíveis pela coleção analisada.
            # ----------------------------------------------------------

            output.print_md(
                "*Nenhum parâmetro de instância foi encontrado "
                "para este elemento.*"
            )

    except Exception:

        # ==============================================================
        # Tratamento de erros
        # ==============================================================
        #
        # Durante o desenvolvimento queremos:
        #
        #     usuário → mensagem simples
        #     desenvolvedor → traceback completo
        #
        # Isso facilita localizar arquivo, linha e exceção sem deixar
        # o comando falhar silenciosamente.
        # ==============================================================

        error_traceback = traceback.format_exc()

        logger.error(
            error_traceback
        )

        output.set_title(
            "PluginRevit - Erro"
        )

        output.print_md(
            "# Erro ao executar Inspecionar Parametros"
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