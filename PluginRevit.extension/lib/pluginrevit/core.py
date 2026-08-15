# -*- coding: utf-8 -*-

PROJECT_NAME = "PluginRevit"
PROJECT_VERSION = "0.1.0-dev"


def get_project_info():
    """Retorna informações básicas independentes da Revit API."""
    return {
        "name": PROJECT_NAME,
        "version": PROJECT_VERSION,
    }


def build_hello_message(document_title, revit_version):
    """Monta a mensagem usada pelo primeiro comando do plugin."""
    title = document_title or "Nenhum documento aberto"
    version = revit_version or "desconhecida"

    return (
        "PluginRevit carregado com sucesso!\n\n"
        "Projeto: {0}\n"
        "Revit: {1}"
    ).format(title, version)
