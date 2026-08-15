# -*- coding: utf-8 -*-

from pyrevit import HOST_APP, forms, revit

from pluginrevit.core import build_hello_message


doc = revit.doc

if doc:
    document_title = doc.Title
else:
    document_title = None

message = build_hello_message(
    document_title=document_title,
    revit_version=str(HOST_APP.version),
)

forms.alert(
    message,
    title="PluginRevit - Etapa 0",
    warn_icon=False,
)
