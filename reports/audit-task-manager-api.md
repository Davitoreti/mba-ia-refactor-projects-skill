# Auditoria arquitetural — task-manager-api

## Escopo

- Raiz analisada: `task-manager-api/`
- Revisão/branch: `main` — `37accd1`
- Operação: somente leitura
- Estado inicial: `.codex/` não rastreada, preservada sem alterações
- Exclusões: `.codex/`, caches, ambientes virtuais, banco SQLite e artefatos gerados

## Resumo do projeto

| Campo | Resultado | Evidência |
|---|---|---|
| Linguagem | Python, versão não fixada | `requirements.txt:1` |
| Framework | Flask 3.0.0; Flask-SQLAlchemy 3.1.1 | `requirements.txt:1` |
| Domínio | Usuários, tarefas, categorias e relatórios | `models/` e `routes/` |
| Arquitetura atual | MVC parcial; handlers acumulam transporte, regras, persistência e serialização | `routes/task_routes.py:11` |
| Persistência | SQLite via Flask-SQLAlchemy; schema criado durante import | `app.py:11` |
| Entry point | `app.py` | `app.py:9` |
| Código-fonte | 15 arquivos / 1.158 linhas | `rg --files task-manager-api -g '*.py' -g '!**/.codex/**'` |
| Testes | Ausentes | Nenhum arquivo ou manifesto de teste encontrado |
| Comandos | `pip install`, `python seed.py`, `python app.py` | `README.md:5` |

## Contratos inventariados

| Método | Rota | Entrada | Sucesso | Erros relevantes | Efeito |
|---|---|---|---|---|---|
| GET | `/` | — | 200, nome e versão | 500 implícito | Leitura |
| GET | `/health` | — | 200, status e timestamp | 500 implícito | Leitura |
| GET | `/users` | — | 200, usuários e `task_count` | 500 implícito | Leitura |
| GET | `/users/<user_id>` | Path inteiro | 200, usuário com hash e tarefas | 404 | Leitura |
| POST | `/users` | `name`, `email`, `password`; `role?` | 201, usuário com hash | 400, 409, 500 | Cria usuário |
| PUT | `/users/<user_id>` | Campos parciais do usuário | 200, usuário com hash | 400, 404, 409, 500 | Atualiza usuário |
| DELETE | `/users/<user_id>` | Path inteiro | 200, mensagem | 404, 500 | Exclui usuário e tarefas |
| GET | `/users/<user_id>/tasks` | Path inteiro | 200, tarefas resumidas | 404 | Leitura |
| POST | `/login` | `email`, `password` | 200, usuário e token | 400, 401, 403 | Autenticação aparente |
| GET | `/tasks` | — | 200, tarefas enriquecidas | 500 | Leitura |
| GET | `/tasks/<task_id>` | Path inteiro | 200, tarefa | 404 | Leitura |
| POST | `/tasks` | Dados da tarefa | 201, tarefa | 400, 404, 500 | Cria tarefa |
| PUT | `/tasks/<task_id>` | Campos parciais da tarefa | 200, tarefa | 400, 404, 500 | Atualiza tarefa |
| DELETE | `/tasks/<task_id>` | Path inteiro | 200, mensagem | 404, 500 | Exclui tarefa |
| GET | `/tasks/search` | `q?`, `status?`, `priority?`, `user_id?` | 200, tarefas | 500 para inteiros inválidos | Leitura |
| GET | `/tasks/stats` | — | 200, estatísticas | 500 implícito | Leitura/agregação |
| GET | `/reports/summary` | — | 200, relatório global | 500 implícito | Leitura/agregação |
| GET | `/reports/user/<user_id>` | Path inteiro | 200, relatório | 404 | Leitura/agregação |
| GET | `/categories` | — | 200, categorias e contagem | 500 implícito | Leitura |
| POST | `/categories` | `name`; `description?`, `color?` | 201, categoria | 400, 500 | Cria categoria |
| PUT | `/categories/<cat_id>` | Campos parciais | 200, categoria | 404, 500 | Atualiza categoria |
| DELETE | `/categories/<cat_id>` | Path inteiro | 200, mensagem | 404, 500 | Exclui categoria |

Observação: existem 19 identidades de rota, mas 22 combinações método/rota devido a `/users`, `/tasks` e `/categories` aceitarem mais de um método.

## Sumário dos findings

| Severidade | Quantidade |
|---|---:|
| CRITICAL | 3 |
| HIGH | 1 |
| MEDIUM | 5 |
| LOW | 3 |
| **Total** | **12** |

## Findings

### SEC-001 — [CRITICAL] Autenticação e autorização quebradas

- **Local:** `user_routes.py:42`, `user_routes.py:185`, `user.py:27`
- **Catálogo:** AP-03
- **Evidência:** qualquer cliente pode criar ou atualizar usuários com papel `admin`; não há middleware de autenticação; o login retorna `fake-jwt-token-<id>`; senhas usam MD5 sem salt.
- **Impacto:** elevação de privilégio, falsificação de identidade e comprometimento rápido das senhas.
- **Recomendação:** hash adaptativo, token assinado com expiração, autenticação obrigatória e autorização por papel/recurso.
- **Contrato afetado:** todas as operações mutáveis e `/login`.
- **Risco de regressão:** alto; a correção adiciona requisitos de autenticação antes inexistentes e precisa ser autorizada como mudança contratual.

### SEC-002 — [CRITICAL] Exposição de hash de senha

- **Local:** `user.py:16`, `user_routes.py:33`, `user_routes.py:207`
- **Catálogo:** AP-04
- **Evidência:** `User.to_dict()` inclui `password`; esse serializer é usado em consulta, criação, atualização e login.
- **Impacto:** clientes obtêm hashes MD5 reutilizáveis em ataques offline.
- **Recomendação:** DTO público sem `password` e serializer específico para respostas.
- **Contrato afetado:** `GET /users/<id>`, `POST /users`, `PUT /users/<id>` e `POST /login`.
- **Risco de regressão:** médio; remove um campo inseguro das respostas.

### SEC-003 — [CRITICAL] Segredo criptográfico hardcoded

- **Local:** `app.py:11`
- **Catálogo:** AP-01
- **Evidência:** `SECRET_KEY` contém valor fixo diretamente no código.
- **Impacto:** permite falsificação de dados assinados pelo Flask quando sessões ou recursos equivalentes forem usados.
- **Recomendação:** carregar de variável de ambiente e falhar no boot quando ausente.
- **Contrato afetado:** infraestrutura de autenticação/sessão.
- **Risco de regressão:** baixo, desde que a configuração seja fornecida no ambiente.

O valor SMTP em `notification_service.py:10` também tem formato de credencial, mas não foi incluído no finding porque o serviço não possui consumidor e não foi possível confirmar que o valor é utilizável.

### ARCH-001 — [HIGH] Regras e casos de uso presos ao transporte HTTP

- **Local:** `task_routes.py:11`, `report_routes.py:12`, `user_routes.py:42`
- **Catálogo:** AP-06
- **Evidência:** handlers validam regras de domínio, consultam e alteram o ORM, calculam atraso/produtividade, controlam transações e serializam respostas.
- **Impacto:** regras não podem ser testadas ou reutilizadas sem Flask e banco; alterações de domínio afetam diretamente o contrato HTTP.
- **Recomendação:** manter routes como adaptadores HTTP e extrair controllers/casos de uso e serviços de relatório.
- **Contrato afetado:** usuários, tarefas, categorias e relatórios.
- **Risco de regressão:** alto devido à abrangência dos contratos.

### PERF-001 — [MEDIUM] Queries N+1

- **Local:** `task_routes.py:14`, `report_routes.py:53`, `report_routes.py:157`
- **Catálogo:** AP-09
- **Evidência:** `/tasks` executa até duas consultas adicionais por tarefa; o relatório consulta tarefas para cada usuário; categorias contam tarefas individualmente.
- **Impacto:** número de consultas cresce linearmente com tarefas, usuários e categorias.
- **Recomendação:** eager loading para relações e agregações agrupadas por usuário/categoria.
- **Contrato afetado:** `GET /tasks`, `/reports/summary` e `/categories`.
- **Risco de regressão:** médio; os payloads enriquecidos devem permanecer idênticos.

### QUAL-001 — [MEDIUM] Validação ausente ou inconsistente

- **Local:** `task_routes.py:85`, `task_routes.py:156`, `task_routes.py:240`, `report_routes.py:190`
- **Catálogo:** AP-10
- **Evidência:** comparação de `priority` pressupõe número; `len()` pressupõe strings; `int(priority)` e `int(user_id)` não são tratados; atualização de categoria não verifica JSON ausente.
- **Impacto:** entradas malformadas geram 500 em vez de respostas 4xx estáveis.
- **Recomendação:** schemas centralizados, validação de tipo/faixa/formato e erros tipados.
- **Contrato afetado:** criação, atualização e busca de tarefas; atualização de usuários e categorias.
- **Risco de regressão:** médio; códigos 500 atualmente observáveis devem virar 400.

### QUAL-002 — [MEDIUM] Tratamento de erros inadequado

- **Local:** `task_routes.py:62`, `user_routes.py:87`, `report_routes.py:182`, `app.py:33`
- **Catálogo:** AP-11
- **Evidência:** múltiplos `except:` capturam inclusive erros de programação; não há handler global; diagnóstico usa `print`; servidor inicia com `debug=True` em `0.0.0.0`.
- **Impacto:** falhas são ocultadas, respostas divergem e o modo de depuração aumenta risco operacional.
- **Recomendação:** exceções específicas, middleware central, logging estruturado e debug configurável por ambiente.
- **Contrato afetado:** todos os endpoints.
- **Risco de regressão:** médio; mensagens e status precisam ser comparados.

### PERF-002 — [MEDIUM] Listagens sem limite e agregações ineficientes

- **Local:** `task_routes.py:14`, `task_routes.py:273`, `report_routes.py:15`
- **Catálogo:** AP-12
- **Evidência:** listagens usam `.all()` sem paginação; `/tasks/stats` emite cinco contagens e carrega todas as tarefas; o relatório executa diversas contagens independentes.
- **Impacto:** consumo de memória e número de round-trips crescem com a base.
- **Recomendação:** paginação com limite máximo e agregações SQL condicionais.
- **Contrato afetado:** listagens, estatísticas e relatórios.
- **Risco de regressão:** alto para paginação, pois altera o formato; médio para agregações internas.

### QUAL-003 — [MEDIUM] Duplicação estrutural

- **Local:** `task_routes.py:16`, `user_routes.py:153`, `task.py:23`
- **Catálogo:** AP-13
- **Evidência:** serialização de tarefa, cálculo de atraso, validação de status/prioridade e conversão de datas são implementados repetidamente com pequenas diferenças.
- **Impacto:** endpoints podem divergir ao corrigir uma regra em apenas um local.
- **Recomendação:** extrair DTOs/schemas e políticas únicas de validação e cálculo.
- **Contrato afetado:** endpoints de tarefas, usuários e relatórios.
- **Risco de regressão:** médio devido às diferenças atuais entre payloads.

### MAINT-001 — [LOW] API legada do SQLAlchemy

- **Local:** `user_routes.py:29`, `task_routes.py:67`, `report_routes.py:105`
- **Catálogo:** AP-17
- **Evidência:** o projeto declara Flask-SQLAlchemy 3.1.1 e usa repetidamente `Model.query.get()`.
- **Impacto:** dependência de interface legada, com manutenção e migração futuras mais difíceis.
- **Recomendação:** substituir busca por chave por `db.session.get(Model, id)` e migrar consultas gradualmente para `select()`.
- **Contrato afetado:** consultas individuais e validações de referência.
- **Risco de regressão:** baixo; a semântica pode ser preservada.
- **Confirmação oficial:** Flask-SQLAlchemy 3.1 classifica a interface `Model.query` como legada; SQLAlchemy documenta `Query.get()` como legado e indica `Session.get()` como substituto. [Flask-SQLAlchemy](https://flask-sqlalchemy.palletsprojects.com/en/stable/legacy-query/), [SQLAlchemy](https://docs.sqlalchemy.org/en/20/orm/queryguide/query.html#sqlalchemy.orm.Query.get)

### MAINT-002 — [LOW] Código morto e imports sem uso

- **Local:** `helpers.py:1`, `notification_service.py:4`, `app.py:7`
- **Catálogo:** AP-15
- **Evidência:** `NotificationService` não tem consumidor; diversos helpers não são chamados; imports como `sys`, `json`, `hashlib`, `os`, `time` e os helpers importados pelo relatório não são usados.
- **Impacto:** aumenta ruído, superfície de manutenção e falsa percepção de funcionalidades existentes.
- **Recomendação:** remover código sem consumidor ou integrá-lo com testes que demonstrem seu uso.
- **Contrato afetado:** nenhum confirmado.
- **Risco de regressão:** baixo após busca de consumidores dinâmicos.

### MAINT-003 — [LOW] Complexidade acidental e magic values

- **Local:** `task.py:38`, `task_routes.py:30`, `report_routes.py:119`
- **Catálogo:** AP-14 e AP-16
- **Evidência:** status, papéis, prioridades e formatos são repetidos como literais; verificações de atraso usam condicionais profundamente aninhadas.
- **Impacto:** mudanças simples exigem alterações dispersas e aumentam a chance de inconsistência.
- **Recomendação:** constantes/enums de domínio, predicados expressivos e guard clauses.
- **Contrato afetado:** validações e estatísticas.
- **Risco de regressão:** baixo.

## Cobertura do catálogo

| ID | Anti-pattern | Resultado | Evidência/justificativa |
|---|---|---|---|
| AP-01 | Segredo hardcoded | Encontrado | `app.py:13` |
| AP-02 | Injection | Não encontrado | Filtros ORM parametrizam valores; interpolação em `LIKE` não monta SQL textual |
| AP-03 | Autenticação/autorização quebrada | Encontrado | token previsível, MD5 e rotas públicas |
| AP-04 | Exposição sensível | Encontrado | `User.to_dict()` expõe `password` |
| AP-05 | God Class/Module | Não encontrado | módulos grandes, mas separados por recurso |
| AP-06 | Regra presa ao transporte | Encontrado | regras e transações nos handlers |
| AP-07 | Estado global mutável | Não aplicável em runtime confirmado | lista mutável existe em serviço sem consumidor |
| AP-08 | Fronteira transacional quebrada | Não encontrado | escritas relacionadas usam um único commit |
| AP-09 | Query N+1 | Encontrado | tarefas, usuários e categorias |
| AP-10 | Validação inconsistente | Encontrado | conversões e tipos não tratados |
| AP-11 | Erro inadequado | Encontrado | `except:` e ausência de handler global |
| AP-12 | Acesso sem limite/agregação ineficiente | Encontrado | `.all()` e contagens repetidas |
| AP-13 | Duplicação estrutural | Encontrado | serialização e regras duplicadas |
| AP-14 | Nomes opacos/magic values | Encontrado | status, papéis e limites repetidos |
| AP-15 | Código morto | Encontrado | helpers, serviço e imports sem consumidores |
| AP-16 | Complexidade acidental | Encontrado | condicionais aninhadas |
| AP-17 | API deprecated/legada | Encontrado | `Model.query.get()` |

## APIs deprecated

- `Model.query.get()` na stack Flask-SQLAlchemy 3.1.1/SQLAlchemy 2.x: interface legada; substituto recomendado para chave primária é `db.session.get(Model, id)`.
- A versão transitiva exata do SQLAlchemy não está fixada por lockfile e não foi resolvida nesta fase somente leitura.

## Limitações

- O boot não foi executado porque importar `app.py` chama `db.create_all()` e pode criar `tasks.db`.
- O seed não foi executado porque apaga e recria os dados.
- Não há testes para confirmar payloads e erros inferidos estaticamente.
- Dependências instaladas e versão do runtime Python não foram verificadas.
- Credenciais SMTP não foram testadas.
- Durante as fases 1 e 2, não houve alteração nos arquivos do projeto.

## Prioridade sugerida

1. Remover exposição de senha e substituir autenticação previsível/MD5.
2. Externalizar configuração sensível e centralizar autenticação/autorização.
3. Extrair controllers, schemas e tratamento global de erros.
4. Eliminar N+1 e consolidar agregações.
5. Migrar APIs legadas e remover código morto.

## Gate

Fase 2 concluída. Deseja executar a Fase 3 e aplicar a refatoração? [sim/não]
