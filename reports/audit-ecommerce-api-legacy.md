# Auditoria arquitetural — ecommerce-api-legacy

## Escopo aprovado

- Baseline: branch `main`, revisão `bec830f`.
- Operação das fases 1 e 2: somente leitura.
- Fonte auditada: `src/app.js`, `src/AppManager.js` e `src/utils.js` (180 linhas físicas).
- Contratos: `POST /api/checkout`, `GET /api/admin/financial-report` e
  `DELETE /api/users/:id`.
- Limitações: dependências inicialmente ausentes, banco SQLite em memória e ausência
  de testes, lint e versão Node fixada.

## Findings aprovados

| ID | Severidade | Finding | Evidência no baseline |
|---|---|---|---|
| SEC-001 | CRITICAL | Autorização ausente | `src/AppManager.js:80-137` |
| SEC-002 | CRITICAL | Segredos hardcoded | `src/utils.js:1-6` |
| SEC-003 | CRITICAL | Cartão e chave em log | `src/AppManager.js:43-46` |
| SEC-004 | CRITICAL | Senhas inseguras | `src/AppManager.js:12,18,66-71`; `src/utils.js:17-22` |
| ARCH-001 | HIGH | Atomicidade e integridade quebradas | `src/AppManager.js:12-16,50-61,131-136` |
| ARCH-002 | HIGH | God Class | `src/AppManager.js:4-138` |
| ARCH-003 | HIGH | Regra de negócio no HTTP | `src/AppManager.js:28-78` |
| ARCH-004 | HIGH | Estado global mutável | `src/utils.js:9-15` |
| PERF-001 | MEDIUM | Query N+1 | `src/AppManager.js:83-127` |
| QUAL-001 | MEDIUM | Validação insuficiente | `src/AppManager.js:29-38` |
| QUAL-002 | MEDIUM | Erros ignorados | `src/AppManager.js:37-61,92-106,131-136` |
| PERF-002 | MEDIUM | Relatório sem limite | `src/AppManager.js:83-127` |
| TECH-001 | MEDIUM | Driver SQLite deprecated | `package.json:11`; lock resolvia `sqlite3@5.1.7` |
| QUAL-003 | LOW | Nomes e valores opacos | `src/AppManager.js:29-46` |
| QUAL-004 | LOW | Código morto | `src/utils.js:10,25`; `src/AppManager.js:2` |
| QUAL-005 | LOW | Callbacks aninhados | `src/AppManager.js:37-76,83-128` |

## Decisão autorizada para mudanças externas

A confirmação da Fase 3 autorizou corrigir os comportamentos inseguros identificados:

- rotas administrativas passam a exigir `Authorization: Bearer <ADMIN_API_TOKEN>`;
- configuração ausente impede o boot;
- exclusão de usuário remove matrículas e pagamentos relacionados;
- entradas inválidas retornam `400` antes de qualquer persistência.

Os métodos, caminhos e formatos de sucesso do checkout e relatório permanecem iguais.
As demais alterações devem ser comparadas com este baseline pelos testes de contrato.
