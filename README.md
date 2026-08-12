# Análise manual

### Projeto `code-smells-project`

#### Problemas encontrados

##### CRITICAL:

1 - `Secret Key` exposta no código (arquivo `controllers.py`, linha 7).

##### MEDIUM:

1 - Função de login não verifica se o usuário existe antes de tentar logar (arquivo `controllers.py`, linha 167).

2 - Query N+1 na função `get_pedidos_usuario` (arquivo `models.py`, linha 171).

##### LOW:

1 - Mensagem de erro genérica ao criar pedido (arquivo `controllers.py`, linha 223).

2 - Mensagem de sucesso genérica ao logar (arquivo `controllers.py`, linha 182).

### Projeto `ecommerce-api-legacy`

#### Problemas encontrados

##### CRITICAL:

1 - Senha exposta no código (arquivo `utils.js`, linha 3).

##### MEDIUM:

1 - Query SQL N+1 no relatório financeiro (arquivo `AppManager.js`, linha 83).

2 - Rota `/api/checkout` não faz validações necessárias (arquivo `AppManager.js`, linha 28).

##### LOW:

1 - Variáveis com nomes pouco descritivos (arquivo `AppManager.js`, linhas 30, 31, 32, 33 e 34).

2 - Resposta desnecessária ao deletar usuário (arquivo `AppManager.js`, linha 138).

### Projeto `task-manager-api`

#### Problemas encontrados

##### CRITICAL:

1 - Credenciais hardcoded (arquivo `app.py`, linha 13).

##### MEDIUM:

1 - Para cada tarefa, busca usuário e categoria. Query N+1 (arquivo `routes/task_routes.py`, linha 14).

2 - Busca converte `priority` e `user_id`  sem tratar `ValueError`(arquivo `routes/task_routes.py`, linha 241).

##### LOW:

1 - Melhoria na legibilidade (arquivo `models/task.py`, linha 45).

2 - Imports não utilziados (arquivo `routes/task_routes.py`, linha 7).