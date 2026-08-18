# Auditoria arquitetural — code-smells-project

## Escopo

- Raiz analisada: `code-smells-project/`
- Revisão/branch: `main@3372948`
- Estado Git: limpo, sincronizado com `origin/main`
- Operação: somente leitura
- Exclusões: bancos locais, caches, ambientes virtuais e artefatos gerados

## Resumo do projeto

| Campo             | Resultado                                                            | Evidência                                                        |
| ----------------- | -------------------------------------------------------------------- | ----------------------------------------------------------------- |
| Linguagem         | Python; versão não fixada                                          | `requirements.txt:1`                                            |
| Framework         | Flask 3.1.1 e Flask-CORS 5.0.1 declarados                            | `requirements.txt:1`                                            |
| Domínio          | Produtos, usuários, pedidos e relatório de vendas                  | `app.py:11`                                                     |
| Arquitetura atual | MVC parcial, com persistência e regras concentradas em`models.py` | `controllers.py:1`, `models.py:1`                             |
| Persistência     | SQLite, SQL direto, schema criado no primeiro acesso                 | `database.py:4`                                                 |
| Entry point       | `app.py`, porta 5000 e debug habilitado                            | `app.py:80`                                                     |
| Código-fonte     | 4 arquivos, 780 linhas                                               | Contagem dos quatro`.py` do diretório raiz                     |
| Testes            | Ausentes                                                             | Únicos arquivos funcionais: quatro`.py`, README e requirements |
| Boot              | `python app.py`, não executado nesta fase                         | `README.md:5`                                                   |

## Contratos inventariados

| Método | Rota                                  | Entrada                                                                      | Sucesso                                     | Erros relevantes                     | Efeito                              |
| ------- | ------------------------------------- | ---------------------------------------------------------------------------- | ------------------------------------------- | ------------------------------------ | ----------------------------------- |
| GET     | `/`                                 | —                                                                           | `200`, descrição da API                 | —                                   | Nenhum                              |
| GET     | `/produtos`                         | —                                                                           | `200`, lista em `dados`                 | `500`                              | Leitura                             |
| GET     | `/produtos/busca`                   | Query`q`, `categoria`, `preco_min`, `preco_max`                      | `200`, lista e total                      | `500`, inclusive número inválido | Leitura                             |
| GET     | `/produtos/<int:id>`                | Path`id`                                                                   | `200`, produto                            | `404`, `500`                     | Leitura                             |
| POST    | `/produtos`                         | JSON`nome`, `preco`, `estoque`; opcionais `descricao`, `categoria` | `201`, ID                                 | `400`, `500`                     | Insere produto                      |
| PUT     | `/produtos/<int:id>`                | Mesmo payload de criação                                                   | `200`                                     | `400`, `404`, `500`            | Atualiza produto                    |
| DELETE  | `/produtos/<int:id>`                | Path`id`                                                                   | `200`                                     | `404`, `500`                     | Exclui produto                      |
| GET     | `/usuarios`                         | —                                                                           | `200`, lista de usuários                 | `500`                              | Leitura                             |
| GET     | `/usuarios/<int:id>`                | Path`id`                                                                   | `200`, usuário                           | `404`, `500`                     | Leitura                             |
| POST    | `/usuarios`                         | JSON`nome`, `email`, `senha`                                           | `201`, ID                                 | `400`, `500`                     | Insere usuário                     |
| POST    | `/login`                            | JSON`email`, `senha`                                                     | `200`, usuário                           | `400`, `401`, `500`            | Autenticação sem sessão/token    |
| POST    | `/pedidos`                          | JSON`usuario_id`, `itens[{produto_id, quantidade}]`                      | `201`, ID e total                         | `400`, `500`                     | Insere pedido/itens e reduz estoque |
| GET     | `/pedidos`                          | —                                                                           | `200`, pedidos e itens                    | `500`                              | Leitura                             |
| GET     | `/pedidos/usuario/<int:usuario_id>` | Path`usuario_id`                                                           | `200`, pedidos do usuário                | `500`                              | Leitura                             |
| PUT     | `/pedidos/<int:pedido_id>/status`   | JSON`status`                                                               | `200`                                     | `400`, `500`                     | Atualiza status                     |
| GET     | `/relatorios/vendas`                | —                                                                           | `200`, métricas de vendas                | `500`                              | Leitura agregada                    |
| GET     | `/health`                           | —                                                                           | `200`, saúde, contagens e configuração | `500`                              | Leitura                             |
| POST    | `/admin/reset-db`                   | —                                                                           | `200`                                     | `500` implícito                   | Apaga todas as tabelas              |
| POST    | `/admin/query`                      | JSON`sql`                                                                  | `200`, resultado ou confirmação         | `400`, `500`                     | Executa SQL arbitrário             |

As rotas estão registradas em `app.py:11-30` e `app.py:32-78`.

## Sumário dos findings

| Severidade      |   Quantidade |
| --------------- | -----------: |
| CRITICAL        |            4 |
| HIGH            |            4 |
| MEDIUM          |            5 |
| LOW             |            2 |
| **Total** | **15** |

## Findings

### SEC-001 — [CRITICAL] Segredo hardcoded

- **Local:** `app.py:7-8`
- **Catálogo:** AP-01
- **Evidência:** `SECRET_KEY` possui valor fixo no código e debug está permanentemente habilitado.
- **Impacto:** qualquer cópia do repositório compartilha o segredo; sessões ou recursos assinados ficam comprometidos.
- **Recomendação:** carregar configuração do ambiente, validar o segredo no boot e desabilitar debug por padrão.
- **Contrato afetado:** configuração da aplicação.
- **Risco de regressão:** médio; configuração de boot precisa ser fornecida no ambiente.

### SEC-002 — [CRITICAL] SQL Injection e execução de SQL arbitrário

- **Local:** `app.py:59-76`, `models.py:43-60`, `models.py:105-168`, `models.py:285-300`
- **Catálogo:** AP-02
- **Evidência:** dados de JSON e query string são concatenados em SQL; `/admin/query` envia diretamente `dados["sql"]` a `cursor.execute`.
- **Impacto:** leitura, alteração ou exclusão integral do banco.
- **Recomendação:** queries parametrizadas; remover ou substituir a execução arbitrária por operações administrativas allowlisted.
- **Contrato afetado:** login, CRUD, pedidos, busca e `/admin/query`.
- **Risco de regressão:** alto; restringir `/admin/query` altera intencionalmente seu comportamento inseguro.

### SEC-003 — [CRITICAL] Autenticação e autorização ausentes/quebradas

- **Local:** `app.py:11-30`, `app.py:47-60`, `models.py:105-130`
- **Catálogo:** AP-03
- **Evidência:** não existe middleware/decorator de autenticação; senhas são comparadas e armazenadas em texto puro; login não cria sessão nem token. Reset, SQL administrativo e todas as mutações são públicos.
- **Impacto:** qualquer cliente pode consultar dados, alterar estoque, pedidos e usuários ou apagar o banco.
- **Recomendação:** hash adaptativo para senhas, autenticação real e autorização por papel/recurso com negação por padrão.
- **Contrato afetado:** praticamente todos os endpoints.
- **Risco de regressão:** alto; proteção adiciona headers e respostas `401/403`, exigindo autorização explícita para mudar contratos.

### SEC-004 — [CRITICAL] Exposição de senhas e segredo

- **Local:** `models.py:72-103`, `controllers.py:128-144`, `controllers.py:264-290`
- **Catálogo:** AP-04
- **Evidência:** `GET /usuarios` e `GET /usuarios/<id>` incluem `senha`; `/health` devolve o `secret_key`.
- **Impacto:** comprometimento de contas e falsificação de dados assinados.
- **Recomendação:** DTOs seguros que nunca serializem senha/segredo e health check mínimo.
- **Contrato afetado:** três endpoints de leitura.
- **Risco de regressão:** alto; remover campos altera respostas externas, embora seja uma correção necessária.

### ARCH-001 — [HIGH] God Module no acesso a dados

- **Local:** `models.py:4-314`
- **Catálogo:** AP-05
- **Evidência:** o módulo reúne CRUD de três recursos, autenticação, cálculo de pedidos, estoque, montagem de DTOs, busca e relatório financeiro.
- **Impacto:** baixa coesão, testes difíceis e grande área de regressão.
- **Recomendação:** separar models/repositórios por domínio e mover regras para serviços.
- **Contrato afetado:** todos, indiretamente.
- **Risco de regressão:** alto devido ao alcance do módulo.

### ARCH-002 — [HIGH] Regras de negócio presas ao transporte

- **Local:** `controllers.py:24-58`, `controllers.py:188-220`
- **Catálogo:** AP-06
- **Evidência:** controllers definem categorias, regras de produto e disparam notificações de pedido diretamente.
- **Impacto:** regras não reutilizáveis e testes dependentes do contexto Flask.
- **Recomendação:** manter parsing HTTP no controller e extrair políticas/casos de uso para serviços.
- **Contrato afetado:** `POST/PUT /produtos` e `POST /pedidos`.
- **Risco de regressão:** médio.

### ARCH-003 — [HIGH] Conexão SQLite global compartilhada

- **Local:** `database.py:4-11`
- **Catálogo:** AP-07
- **Evidência:** `db_connection` global reutiliza uma conexão com `check_same_thread=False`, sem sincronização nem escopo por request.
- **Impacto:** concorrência entre requests, transações misturadas e testes contaminados.
- **Recomendação:** conexão com ciclo de vida por request e fechamento via teardown.
- **Contrato afetado:** todos os endpoints que acessam SQLite.
- **Risco de regressão:** médio.

### ARCH-004 — [HIGH] Fronteira transacional sem rollback

- **Local:** `models.py:133-169`, `controllers.py:218-220`
- **Catálogo:** AP-08
- **Evidência:** criação de pedido realiza múltiplos inserts e updates, mas não faz rollback em falhas; a exceção é capturada fora da camada transacional.
- **Impacto:** alterações parciais podem permanecer na conexão global e ser confirmadas por um commit posterior.
- **Recomendação:** transação explícita com commit único, rollback garantido e constraints referenciais.
- **Contrato afetado:** `POST /pedidos`.
- **Risco de regressão:** médio.

### PERF-001 — [MEDIUM] Query N+1 em pedidos

- **Local:** `models.py:171-233`
- **Catálogo:** AP-09
- **Evidência:** após listar pedidos, executa uma consulta de itens por pedido e outra de produto por item.
- **Impacto:** o número de queries cresce com pedidos e itens.
- **Recomendação:** obter pedidos, itens e produtos com JOIN ou carregamento em lote.
- **Contrato afetado:** `GET /pedidos` e `GET /pedidos/usuario/<usuario_id>`.
- **Risco de regressão:** médio; a forma aninhada da resposta precisa ser preservada.

### QUAL-001 — [MEDIUM] Validação incompleta e inconsistente

- **Local:** `controllers.py:24-54`, `controllers.py:111-126`, `controllers.py:167-220`, `controllers.py:237-255`
- **Catálogo:** AP-10
- **Evidência:** tipos não são verificados; conversões inválidas viram `500`; login/status acessam `.get` sem confirmar JSON; itens do pedido não validam formato, quantidade ou usuário.
- **Impacto:** erros internos e dados inválidos.
- **Recomendação:** schemas centralizados e respostas `400/422` consistentes.
- **Contrato afetado:** busca, login, produtos, usuários e pedidos.
- **Risco de regressão:** médio.

### QUAL-002 — [MEDIUM] Tratamento de erro repetido e vazamento interno

- **Local:** `controllers.py:5-292`, `app.py:68-78`
- **Catálogo:** AP-11
- **Evidência:** dezesseis blocos `except Exception` retornam `str(e)` ao cliente; não existe handler central nem rollback.
- **Impacto:** detalhes internos expostos, respostas inconsistentes e diagnóstico baseado em `print`.
- **Recomendação:** exceções tipadas e error handler Flask centralizado, com logging estruturado.
- **Contrato afetado:** quase todos.
- **Risco de regressão:** médio; mensagens devem mudar, status existentes podem ser preservados quando corretos.

### PERF-002 — [MEDIUM] Listagens sem paginação

- **Local:** `models.py:4-22`, `models.py:72-87`, `models.py:203-233`
- **Catálogo:** AP-12
- **Evidência:** produtos, usuários e pedidos são carregados integralmente, sem limite.
- **Impacto:** consumo crescente de memória e latência; pedidos ainda amplificam o N+1.
- **Recomendação:** paginação com limites máximos e ordenação estável.
- **Contrato afetado:** três endpoints de listagem.
- **Risco de regressão:** alto; paginação altera o formato/comportamento se não for introduzida de forma compatível.

### QUAL-003 — [MEDIUM] Duplicação de serialização e validação

- **Local:** `models.py:4-41`, `models.py:171-233`, `models.py:285-314`, `controllers.py:24-96`
- **Catálogo:** AP-13
- **Evidência:** mapeamento de produtos e pedidos é repetido; create/update repetem validações com regras divergentes.
- **Impacto:** campos e validações evoluem de maneira inconsistente.
- **Recomendação:** mappers/DTOs e schemas compartilhados.
- **Contrato afetado:** produtos e pedidos.
- **Risco de regressão:** baixo a médio.

### QUAL-004 — [LOW] Magic values

- **Local:** `controllers.py:52-54`, `controllers.py:242-250`, `models.py:256-262`
- **Catálogo:** AP-14
- **Evidência:** categorias, estados, limites e percentuais de desconto aparecem como listas e números locais.
- **Impacto:** alterações exigem localizar múltiplos pontos e podem divergir.
- **Recomendação:** constantes, enums e políticas nomeadas.
- **Contrato afetado:** produtos, status de pedidos e relatório.
- **Risco de regressão:** baixo.

### QUAL-005 — [LOW] Imports não utilizados

- **Local:** `models.py:2`, `database.py:2`
- **Catálogo:** AP-15
- **Evidência:** `sqlite3` em `models.py` e `os` em `database.py` não têm consumidores.
- **Impacto:** ruído e dependências aparentes incorretas.
- **Recomendação:** remover os imports.
- **Contrato afetado:** nenhum.
- **Risco de regressão:** baixo.

## Cobertura do catálogo

| ID    | Anti-pattern                          | Resultado       | Evidência/justificativa                                 |
| ----- | ------------------------------------- | --------------- | -------------------------------------------------------- |
| AP-01 | Segredo hardcoded                     | Encontrado      | SEC-001                                                  |
| AP-02 | Injection                             | Encontrado      | SEC-002                                                  |
| AP-03 | Autenticação/autorização quebrada | Encontrado      | SEC-003                                                  |
| AP-04 | Exposição de dados sensíveis       | Encontrado      | SEC-004                                                  |
| AP-05 | God Module                            | Encontrado      | ARCH-001                                                 |
| AP-06 | Regra presa ao transporte             | Encontrado      | ARCH-002                                                 |
| AP-07 | Estado/conexão global                | Encontrado      | ARCH-003                                                 |
| AP-08 | Fronteira transacional quebrada       | Encontrado      | ARCH-004                                                 |
| AP-09 | N+1                                   | Encontrado      | PERF-001                                                 |
| AP-10 | Validação inconsistente             | Encontrado      | QUAL-001                                                 |
| AP-11 | Erros inadequados                     | Encontrado      | QUAL-002                                                 |
| AP-12 | Acesso sem limite                     | Encontrado      | PERF-002                                                 |
| AP-13 | Duplicação estrutural               | Encontrado      | QUAL-003                                                 |
| AP-14 | Magic values                          | Encontrado      | QUAL-004                                                 |
| AP-15 | Código morto/import não usado       | Encontrado      | QUAL-005                                                 |
| AP-16 | Complexidade acidental                | Consolidado     | Sinais já cobertos por AP-02, AP-13 e AP-14             |
| AP-17 | API deprecated                        | Não encontrada | Nenhum uso confirmável no código e versões declaradas |

## APIs deprecated

Nenhuma ocorrência confirmada na versão Flask 3.1.1 declarada. A versão efetivamente instalada e a versão do runtime Python não foram verificadas porque as dependências não foram executadas ou instaladas.

## Limitações

- Análise estática: o boot criaria e popularia `loja.db`.
- Não existem testes automatizados, configuração de lint ou checagem de tipos.
- Versões resolvidas das dependências não foram verificadas.
- Erros e efeitos de concorrência foram inferidos do fluxo implementado, sem tráfego real.
- Corrigir autenticação e remover campos sensíveis exigirá autorização para mudar contratos externos.

## Prioridade sugerida

1. Bloquear SQL arbitrário, introduzir autenticação/autorização e eliminar exposição de segredos/senhas.
2. Parametrizar SQL, corrigir transações e trocar a conexão global por escopo de request.
3. Separar responsabilidades, centralizar validação/erros e eliminar N+1.
4. Preservar os contratos que não exigem mudança de segurança e validar todos os 19 endpoints.

## Gate

Fase 2 concluída. Deseja executar a Fase 3 e aplicar a refatoração? [sim/não]
