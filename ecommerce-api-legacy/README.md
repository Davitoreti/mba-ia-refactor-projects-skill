# ecommerce-api-legacy

LMS API (com fluxo de checkout) em Node.js/Express usada como entrada do desafio `refactor-arch`.

## Como rodar

No Linux, macOS, Git Bash ou WSL:

```bash
npm install
export ADMIN_API_TOKEN="troque-este-token"
npm start
```

No PowerShell:

```powershell
npm install
$env:ADMIN_API_TOKEN = "troque-este-token"
npm start
```

A aplicação sobe em `http://localhost:3000`. O banco SQLite é em memória e já carrega seeds automaticamente no boot.

As rotas `GET /api/admin/financial-report` e `DELETE /api/users/:id` exigem esse
token no header `Authorization: Bearer <token>`.
O relatório aceita `limit` (1 a 100; padrão 100) e `offset` (padrão 0).

### Testar no PowerShell

Com a aplicação em execução, abra uma segunda janela do PowerShell e envie o
mesmo token usado para iniciar o servidor:

```powershell
Invoke-RestMethod `
  -Uri "http://localhost:3000/api/admin/financial-report" `
  -Headers @{ Authorization = "Bearer troque-este-token" }
```

As variáveis de ambiente não são compartilhadas entre janelas do PowerShell. Se
preferir usar `$env:ADMIN_API_TOKEN` na segunda janela, defina-a novamente:

```powershell
$env:ADMIN_API_TOKEN = "troque-este-token"

Invoke-RestMethod `
  -Uri "http://localhost:3000/api/admin/financial-report" `
  -Headers @{ Authorization = "Bearer $env:ADMIN_API_TOKEN" }
```

Se o token usado pelo servidor for alterado, reinicie a aplicação.

## Validação

```bash
npm run check
npm test
```

Exemplos de requisições estão em `api.http`.
