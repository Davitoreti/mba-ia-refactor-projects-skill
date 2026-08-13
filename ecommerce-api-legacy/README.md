# ecommerce-api-legacy

LMS API (com fluxo de checkout) em Node.js/Express usada como entrada do desafio `refactor-arch`.

## Como rodar

```bash
npm install
export ADMIN_API_TOKEN="troque-este-token"
npm start
```

A aplicação sobe em `http://localhost:3000`. O banco SQLite é em memória e já carrega seeds automaticamente no boot.

No PowerShell, configure o token com `$env:ADMIN_API_TOKEN = "troque-este-token"`.
As rotas `GET /api/admin/financial-report` e `DELETE /api/users/:id` exigem esse
token no header `Authorization: Bearer <token>`.
O relatório aceita `limit` (1 a 100; padrão 100) e `offset` (padrão 0).

## Validação

```bash
npm run check
npm test
```

Exemplos de requisições estão em `api.http`.
