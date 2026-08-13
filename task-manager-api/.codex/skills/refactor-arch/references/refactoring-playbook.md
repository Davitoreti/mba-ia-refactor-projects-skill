# Playbook de refatoração

Escolher somente transformações ligadas aos findings aprovados. Exemplos ilustram padrão; adaptar sintaxe e nomes à stack.

## Sumário

1. Extrair configuração
2. Parametrizar SQL
3. Separar rota e controller
4. Dividir God Module
5. Eliminar N+1
6. Centralizar validação
7. Centralizar erros
8. Criar fronteira transacional
9. Proteger autenticação e autorização
10. Remover estado global
11. Migrar API deprecated

## 1. Extrair configuração e segredos

**Antes**

```python
app.config["SECRET_KEY"] = "secret-123"
```

**Depois**

```python
import os

secret_key = os.environ.get("SECRET_KEY")
if not secret_key:
    raise RuntimeError("SECRET_KEY is required")
app.config["SECRET_KEY"] = secret_key
```

Validar no boot. Não incluir segredo real em exemplo, teste, log ou resposta.

## 2. Parametrizar SQL

**Antes**

```python
cursor.execute("SELECT * FROM users WHERE email = '" + email + "'")
```

**Depois**

```python
cursor.execute("SELECT * FROM users WHERE email = ?", (email,))
```

Aplicar a todo dado variável. Para nome de tabela/coluna, usar allowlist; parâmetros não substituem identificadores.

## 3. Separar rota e controller

**Antes**

```javascript
app.post('/checkout', async (req, res) => {
  // valida, cobra, matricula e responde
});
```

**Depois**

```javascript
router.post('/checkout', validate(checkoutSchema), checkoutController.create);

async function create(req, res, next) {
  try {
    const result = await checkoutService.execute(req.validatedBody);
    return res.status(200).json(result);
  } catch (error) {
    return next(error);
  }
}
```

Manter detalhes HTTP na rota/controller e regras no serviço.

## 4. Dividir God Module por responsabilidade

**Antes**

```text
AppManager
  initDb
  setupRoutes
  checkout
  report
  deleteUser
```

**Depois**

```text
app.js
routes/checkout-routes.js
controllers/checkout-controller.js
services/checkout-service.js
repositories/enrollment-repository.js
```

Extrair incrementalmente. Capturar contratos; depois mover um fluxo por vez.

## 5. Eliminar N+1

**Antes**

```python
tasks = Task.query.all()
for task in tasks:
    task.user = User.query.get(task.user_id)
```

**Depois**

```python
from sqlalchemy import select
from sqlalchemy.orm import joinedload

tasks = db.session.execute(
    select(Task).options(joinedload(Task.user))
).scalars().all()
```

Alternativas: JOIN explícito, eager loading, batch por IDs ou agregação. Validar número de queries e formato da resposta.

## 6. Centralizar validação

**Antes**

```python
if not title:
    return {"error": "required"}, 400
if len(title) > 200:
    return {"error": "too long"}, 400
```

**Depois**

```python
def parse_task_input(data):
    return {
        "title": require_string(data, "title", min_length=3, max_length=200)
    }
```

Usar biblioteca já presente quando adequada. Preservar mensagens e status se fizerem parte do contrato.

## 7. Centralizar tratamento de erros

**Antes**

```python
try:
    service.execute()
except Exception as error:
    return jsonify({"error": str(error)}), 500
```

**Depois**

```python
@app.errorhandler(NotFoundError)
def handle_not_found(error):
    return jsonify({"error": error.public_message}), 404

@app.errorhandler(Exception)
def handle_unexpected(error):
    logger.exception("unexpected error")
    return jsonify({"error": "Erro interno"}), 500
```

Não esconder rollback. Não devolver stack trace, segredo ou SQL.

## 8. Criar fronteira transacional

**Antes**

```javascript
await enrollments.insert(data);
await payments.insert(payment);
await audit.insert(log);
```

**Depois**

```javascript
await database.transaction(async (transaction) => {
  const enrollment = await enrollments.insert(data, transaction);
  await payments.insert(buildPayment(enrollment), transaction);
  await audit.insert(buildAudit(enrollment), transaction);
});
```

Definir efeitos atômicos. Para integração externa, considerar idempotência, outbox ou compensação.

## 9. Proteger autenticação e autorização

**Antes**

```python
return {"token": "fake-token-" + str(user.id)}
```

**Depois**

```python
token = token_service.issue(subject=user.id, role=user.role)
return {"token": token}
```

Aplicar middleware de autenticação/autorização nas rotas protegidas. Usar hash adaptativo confiável. Mudança de contrato exige registro e autorização quando consumidores forem afetados.

## 10. Remover estado global mutável

**Antes**

```javascript
const cache = {};
module.exports = { cache };
```

**Depois**

```javascript
function createApplication({ cache, database }) {
  const service = new CheckoutService({ cache, database });
  return buildHttpApp({ service });
}
```

Definir ciclo de vida e concorrência. Em teste, injetar implementação isolada.

## 11. Migrar API deprecated

**Antes**

```python
user = User.query.get(user_id)
```

**Depois**

```python
user = db.session.get(User, user_id)
```

Confirmar depreciação na versão detectada e fonte oficial. Executar testes de semântica, não apenas substituir texto.

## Sequência segura

1. Capturar contratos e comportamento atual.
2. Executar testes existentes ou caracterização.
3. Corrigir segurança e integridade com risco explícito.
4. Extrair configuração e error handling.
5. Separar um fluxo vertical por vez.
6. Otimizar persistência preservando resultado.
7. Reexecutar boot, testes e contratos após cada etapa.
8. Auditar findings residuais e revisar diff final.
