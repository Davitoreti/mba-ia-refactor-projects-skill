# Análise de projeto

Usar estas heurísticas para produzir inventário verificável sem alterar o projeto.

## 1. Definir escopo

- Ler instruções do repositório antes do código.
- Verificar estado do versionamento e preservar mudanças locais.
- Enumerar arquivos com ferramenta de busca rápida.
- Excluir dependências, caches, builds, cobertura, bancos e arquivos gerados.
- Considerar como fonte arquivos implementados, não apenas nomes sugeridos em documentação.

## 2. Detectar stack

Combinar evidências; não concluir pela extensão isolada.

| Evidência | Exemplos |
|---|---|
| Manifest | `requirements.txt`, `pyproject.toml`, `package.json`, `pom.xml`, `go.mod` |
| Lockfile | `package-lock.json`, `poetry.lock`, `uv.lock`, `yarn.lock` |
| Imports | `flask`, `express`, `django`, `fastapi`, `spring` |
| Entry point | `app.py`, `main.py`, `server.js`, `index.ts` |
| Configuração | URI de banco, portas, plugins, middlewares |

- Informar versão declarada e versão resolvida separadamente quando divergirem.
- Informar `não determinada` quando runtime não estiver fixado.
- Não instalar nem executar dependências nas fases 1 e 2.

## 3. Mapear arquitetura

Identificar responsabilidades reais, não somente diretórios:

- bootstrap e composition root;
- rotas ou adaptadores de entrada;
- controllers ou handlers;
- serviços e casos de uso;
- models, entidades e persistência;
- integrações externas;
- configuração, middlewares e tratamento de erros;
- jobs, workers e scripts administrativos.

Classificar estrutura como monolítica, modular, em camadas, MVC parcial ou outra forma sustentada pelo código. Registrar dependências entre módulos e violações aparentes apenas na fase 2.

## 4. Mapear domínio e dados

- Inferir recursos por rotas, models, tabelas e nomes de casos de uso.
- Listar banco, driver, ORM ou SQL direto.
- Identificar criação de schema, migrations, seed e ciclo da conexão.
- Registrar relações, chaves, transações e dados persistentes relevantes.
- Distinguir banco em memória de banco em arquivo ou serviço externo.

## 5. Inventariar contratos

Para cada interface externa, registrar:

| Campo | Conteúdo |
|---|---|
| Tipo | HTTP, CLI, job, mensagem ou biblioteca |
| Identidade | Método e rota, comando ou tópico |
| Entrada | Path, query, headers, payload e tipos inferidos |
| Saída | Corpo, status, headers e formato |
| Erros | Condições e respostas observadas |
| Efeitos | Escritas, chamadas externas e eventos |

Não executar chamadas destrutivas para descobrir contratos. Usar análise estática quando boot ou seed alterarem dados.

## 6. Contar código

- Definir extensões consideradas fonte.
- Excluir testes somente se a métrica declarar essa exclusão.
- Contar arquivos e linhas com comando reproduzível.
- Não contar lockfiles, documentação ou dependências como código-fonte.
- Registrar limitações para rotas dinâmicas ou código gerado.

## 7. Descobrir validações disponíveis

Procurar scripts de instalação, boot, teste, lint, formatação, tipos, migrations, seed e smoke test.

Não afirmar ausência apenas porque README não menciona. Procurar manifests, diretórios de teste e configuração de CI.

## 8. Evidência mínima

Toda conclusão deve apontar para arquivo, manifesto ou comando. Separar:

- confirmado no código;
- inferido com justificativa;
- não determinado;
- não validado por dependência ou efeito colateral.
