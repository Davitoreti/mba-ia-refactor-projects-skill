# Auditoria arquitetural — task-manager-api

## Escopo

- Raiz analisada: `task-manager-api/`
- Revisão/branch: `main` — `37accd1`
- Operação da auditoria: somente leitura
- Código-fonte: 15 arquivos Python, 1.158 linhas antes da refatoração
- Contratos: 19 rotas e 22 combinações método/rota
- Limitações: comportamento original inferido estaticamente; o boot original criava o schema durante o import e não havia testes.

## Stack

- Python, versão não fixada pelo projeto
- Flask 3.0.0
- Flask-SQLAlchemy 3.1.1
- SQLite
- Flask-CORS, Marshmallow, Requests e python-dotenv

## Sumário dos findings aprovados

| Severidade | Quantidade |
|---|---:|
| CRITICAL | 3 |
| HIGH | 1 |
| MEDIUM | 5 |
| LOW | 3 |
| **Total** | **12** |

## Findings

### SEC-001 — [CRITICAL] Autenticação e autorização quebradas

- **Catálogo:** AP-03
- **Evidência original:** `models/user.py:27-32`, `routes/user_routes.py:42-78`, `routes/user_routes.py:185-210`.
- **Problema:** MD5 sem salt, token previsível e operações públicas capazes de atribuir papel administrativo.
- **Correção aprovada:** hash adaptativo, token assinado com expiração e autorização por papel.
- **Risco contratual:** alto; endpoints protegidos passam a exigir `Authorization: Bearer <token>`.

### SEC-002 — [CRITICAL] Exposição de hash de senha

- **Catálogo:** AP-04
- **Evidência original:** `models/user.py:16-25`, consumido por consulta, criação, atualização e login.
- **Correção aprovada:** serializer público sem `password`.
- **Risco contratual:** médio; o campo inseguro foi removido das respostas.

### SEC-003 — [CRITICAL] Segredo criptográfico hardcoded

- **Catálogo:** AP-01
- **Evidência original:** `app.py:11-13`.
- **Correção aprovada:** `SECRET_KEY` obrigatória via ambiente e validação no boot.

### ARCH-001 — [HIGH] Regras presas ao transporte HTTP

- **Catálogo:** AP-06
- **Evidência original:** `routes/task_routes.py:11-299`, `routes/user_routes.py:10-211`, `routes/report_routes.py:12-223`.
- **Correção aprovada:** rotas finas, controllers, services e repositories.

### PERF-001 — [MEDIUM] Queries N+1

- **Catálogo:** AP-09
- **Evidência original:** `routes/task_routes.py:14-52`, `routes/report_routes.py:53-68`, `routes/report_routes.py:157-165`.
- **Correção aprovada:** eager loading e agregações agrupadas.

### QUAL-001 — [MEDIUM] Validação ausente ou inconsistente

- **Catálogo:** AP-10
- **Evidência original:** `routes/task_routes.py:85-144`, `routes/task_routes.py:156-213`, `routes/task_routes.py:240-265`.
- **Correção aprovada:** validadores centralizados e respostas 400 estáveis.

### QUAL-002 — [MEDIUM] Tratamento inadequado de erros

- **Catálogo:** AP-11
- **Evidência original:** `except:` genéricos nas três rotas e `debug=True` em `app.py:34`.
- **Correção aprovada:** erros de aplicação, handlers globais, rollback e logging do Flask.

### PERF-002 — [MEDIUM] Acesso sem limite e agregações ineficientes

- **Catálogo:** AP-12
- **Evidência original:** `.all()` sem paginação e diversas contagens independentes em estatísticas/relatórios.
- **Correção aprovada:** paginação opcional limitada a 100 e agregações condicionais.

### QUAL-003 — [MEDIUM] Duplicação estrutural

- **Catálogo:** AP-13
- **Evidência original:** serialização, cálculo de atraso e validação repetidos nos handlers.
- **Correção aprovada:** entidades, controllers e validadores compartilhados.

### MAINT-001 — [LOW] API legada do SQLAlchemy

- **Catálogo:** AP-17
- **Evidência original:** usos de `Model.query.get()` nas três rotas.
- **Correção aprovada:** `db.session.get()` e consultas `select()`.
- **Fonte:** documentação oficial do Flask-SQLAlchemy 3.1 e SQLAlchemy 2.x.

### MAINT-002 — [LOW] Código morto e imports sem uso

- **Catálogo:** AP-15
- **Evidência original:** `services/notification_service.py`, `utils/helpers.py` e imports sem consumidores.
- **Correção aprovada:** remoção dos módulos mortos e imports associados.

### MAINT-003 — [LOW] Complexidade acidental e magic values

- **Catálogo:** AP-14 e AP-16
- **Evidência original:** status, papéis, limites e condicionais de atraso repetidos.
- **Correção aprovada:** constantes, predicados e guard clauses.

## Mudanças contratuais de segurança autorizadas

1. Todas as rotas de dados passam a exigir token; operações de usuários e mutações de categorias exigem `admin`, e relatórios aceitam `admin` ou `manager`.
2. `password` deixa de existir nos payloads públicos.
3. Senha mínima passa de quatro para oito caracteres.
4. Tokens previsíveis são substituídos por tokens assinados com validade padrão de uma hora.
5. Busca inválida passa a responder 400 em vez de 500.

## Prioridade executada

1. Segurança e configuração.
2. Fronteiras MVC e tratamento de erros.
3. Performance, validação e redução de duplicação.
4. API legada, código morto e testes de contrato.
