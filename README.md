# PluginRevit

Plugin modular para auditoria e automação de projetos elétricos no Autodesk Revit.

## Objetivo inicial

Desenvolver incrementalmente ferramentas para:

1. auditar elementos elétricos;
2. verificar conectividade e circuitos;
3. verificar comandos de iluminação;
4. verificar interferências;
5. gerar fiação;
6. futuramente estudar roteamento automático de tubulação.

Cada etapa deve incluir testes da funcionalidade nova e testes de regressão das funcionalidades anteriores.

## Estrutura inicial

```text
PluginRevit/
├── PluginRevit.extension/
│   ├── PluginRevit.tab/
│   │   └── Desenvolvimento.panel/
│   │       └── Hello Revit.pushbutton/
│   │           └── script.py
│   └── lib/
│       └── pluginrevit/
│           ├── __init__.py
│           └── core.py
├── tests/
│   └── test_core.py
├── run_tests.bat
├── .gitignore
└── README.md
```

## Testes Python externos

No terminal, na raiz do repositório:

```powershell
.\run_tests.bat
```

ou:

```powershell
python -m unittest discover -s tests -v
```

## Smoke test no Revit

Após configurar a pasta do repositório como caminho de extensão do pyRevit:

1. abra o Revit;
2. recarregue o pyRevit;
3. abra a aba `PluginRevit`;
4. clique em `Hello Revit`.

O comando deve exibir o nome do projeto aberto e a versão do Revit.

## Regra de desenvolvimento

Uma etapa só é considerada concluída quando:

- a nova funcionalidade funciona;
- seus testes passam;
- todos os testes anteriores continuam passando.
