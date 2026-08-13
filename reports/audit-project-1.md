# Auditoria arquitetural — code-smells-project

## Escopo aprovado

- Revisão auditada: `main@3372948`
- Operação das fases 1 e 2: somente leitura
- Código-fonte original: 4 arquivos Python, 780 linhas
- Contratos originais: 19 endpoints HTTP
- Stack: Python (versão não fixada), Flask 3.1.1 e SQLite

## Sumário

| Severidade | Quantidade |
|---|---:|
| CRITICAL | 4 |
| HIGH | 4 |
| MEDIUM | 5 |
| LOW | 2 |
| **Total** | **15** |

## Findings aprovados

| ID | Severidade | Catálogo | Evidência original | Tratamento aprovado |
|---|---|---|---|---|
| SEC-001 | CRITICAL | AP-01 | `app.py:7-8` | Configuração externa com validação no boot |
| SEC-002 | CRITICAL | AP-02 | `app.py:59-76`; `models.py:43-60,105-168,285-300` | SQL parametrizado e endpoint SQL desativado |
| SEC-003 | CRITICAL | AP-03 | `app.py:11-30,47-60`; `models.py:105-130` | Senhas com hash, sessão e autorização por papel/recurso |
| SEC-004 | CRITICAL | AP-04 | `models.py:72-103`; `controllers.py:128-144,264-290` | DTO sem senha e health check sem segredo/configuração interna |
| ARCH-001 | HIGH | AP-05 | `models.py:4-314` | Models, repositories e services separados |
| ARCH-002 | HIGH | AP-06 | `controllers.py:24-58,188-220` | Regras e transações movidas para services |
| ARCH-003 | HIGH | AP-07 | `database.py:4-11` | Conexão SQLite no contexto de cada request |
| ARCH-004 | HIGH | AP-08 | `models.py:133-169`; `controllers.py:218-220` | Transação explícita com rollback |
| PERF-001 | MEDIUM | AP-09 | `models.py:171-233` | JOIN único com reconstrução da resposta aninhada |
| QUAL-001 | MEDIUM | AP-10 | `controllers.py:24-54,111-126,167-220,237-255` | Validação centralizada e erros 400 estáveis |
| QUAL-002 | MEDIUM | AP-11 | `controllers.py:5-292`; `app.py:68-78` | Exceções de aplicação e handlers Flask centrais |
| PERF-002 | MEDIUM | AP-12 | `models.py:4-22,72-87,203-233` | Paginação opcional com limite máximo de 100 |
| QUAL-003 | MEDIUM | AP-13 | `models.py:4-41,171-233,285-314`; `controllers.py:24-96` | Mappers de domínio e parsers compartilhados |
| QUAL-004 | LOW | AP-14 | `controllers.py:52-54,242-250`; `models.py:256-262` | Constantes nomeadas para categorias, status e descontos |
| QUAL-005 | LOW | AP-15 | `models.py:2`; `database.py:2` | Imports sem uso removidos |

## Contratos e mudanças de segurança autorizadas

Os 19 métodos e caminhos originais permanecem registrados. Foi acrescentado
`POST /logout`. Formatos de sucesso do domínio foram preservados sempre que não
continham dados sensíveis.

Mudanças deliberadas:

- rotas administrativas, listagem de usuários, relatório e mutações exigem sessão;
- acesso a recurso de usuário/pedido exige o próprio usuário ou administrador;
- respostas de usuário não incluem `senha`;
- `/health` não expõe `secret_key`, `db_path` ou debug;
- `/admin/query` retorna `410` após autenticação, sem executar SQL;
- entradas inválidas retornam `400` em vez de erros internos;
- paginação opcional usa `page` e `per_page`, mantendo o payload de sucesso;
- CORS global irrestrito foi removido.

## Validação planejada

- sintaxe de todos os módulos Python;
- suíte `python -m unittest discover -s tests -v`;
- boot real com SQLite temporário;
- smoke HTTP de `/`, `/health` e `/produtos`;
- fluxos de login, usuários, produtos, pedidos, rollback, relatório e admin;
- busca residual e `git diff --check`.

Os resultados finais de validação são registrados no resumo da execução da
Fase 3, não neste snapshot pré-refatoração.
