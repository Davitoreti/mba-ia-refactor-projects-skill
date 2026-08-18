# Análise manual

Os achados desta seção referem-se ao código anterior à refatoração de cada
projeto: `3372948` para `code-smells-project`, `bec830f` para
`ecommerce-api-legacy` e `37accd1` para `task-manager-api`. Os caminhos e linhas
abaixo foram conferidos nesses commits.

### Projeto `code-smells-project`

#### Problemas encontrados

##### CRITICAL:

1 - `SECRET_KEY` hardcoded (arquivo `app.py`, linha 7). O segredo versionado
pode ser conhecido por qualquer pessoa com acesso ao repositório e dificulta a
rotação por ambiente.

##### MEDIUM:

1 - Validação incompleta na criação de pedidos (arquivo `controllers.py`, linhas
188 a 203). O código verifica apenas presença de `usuario_id` e `itens`, sem
validar tipos e quantidades antes de chamar a persistência.

2 - Queries N+1 nas funções `get_pedidos_usuario` e `get_todos_pedidos`
(arquivo `models.py`, linhas 171 a 233). Cada pedido dispara consulta de itens e
cada item dispara outra consulta de produto, aumentando o número de queries com
o volume retornado.

##### LOW:

1 - Categorias, status e faixas de desconto aparecem como valores literais
espalhados (arquivos `controllers.py`, linhas 52 a 54 e 242 a 250, e
`models.py`, linhas 256 a 262). Isso aumenta o custo de alterar essas regras.

2 - Imports sem uso de `sqlite3` e `os` (arquivos `models.py`, linha 2, e
`database.py`, linha 2). Eles adicionam ruído e sugerem dependências que os
módulos não utilizam.

### Projeto `ecommerce-api-legacy`

#### Problemas encontrados

##### CRITICAL:

1 - Credenciais e chave de pagamento hardcoded (arquivo `utils.js`, linhas 2 a
5). Os valores sensíveis ficam versionados e não podem ser configurados por
ambiente.

##### MEDIUM:

1 - Query N+1 no relatório financeiro (arquivo `AppManager.js`, linhas 83 a
127). Para cada curso são buscadas matrículas e, para cada matrícula, usuário e
pagamento.

2 - Validação insuficiente em `POST /api/checkout` (arquivo `AppManager.js`,
linhas 28 a 36). A rota verifica apenas a presença de parte dos campos e não
valida tipos, formato de e-mail, senha ou cartão.

##### LOW:

1 - Variáveis `u`, `e`, `p`, `cid` e `cc` têm nomes opacos (arquivo
`AppManager.js`, linhas 29 a 33), o que reduz a legibilidade do checkout.

2 - Callbacks profundamente aninhados no checkout e no relatório (arquivo
`AppManager.js`, linhas 37 a 76 e 83 a 128). O encadeamento aumenta a
complexidade de leitura e tratamento de erros.

### Projeto `task-manager-api`

#### Problemas encontrados

##### CRITICAL:

1 - `SECRET_KEY` hardcoded (arquivo `app.py`, linha 13). O segredo criptográfico
fica versionado e é reutilizado em qualquer ambiente que execute o código.

##### MEDIUM:

1 - Query N+1 em `GET /tasks` (arquivo `routes/task_routes.py`, linhas 14 a 52).
Depois de carregar as tarefas, a rota consulta usuário e categoria dentro do
loop.

2 - `GET /tasks/search` converte `priority` e `user_id` sem tratar `ValueError`
(arquivo `routes/task_routes.py`, linhas 240 a 271). Valores não numéricos podem
produzir erro interno em vez de resposta `400`.

##### LOW:

1 - Validação e cálculo de atraso usam condicionais desnecessariamente
aninhadas e valores literais de status (arquivo `models/task.py`, linhas 38 a
60), aumentando o custo cognitivo.

2 - Imports `json`, `os`, `sys` e `time` não são utilizados (arquivo
`routes/task_routes.py`, linha 7), adicionando ruído ao módulo.

# Construção da Skill

## Decisões de design

A skill `refactor-arch` foi organizada como um fluxo de três fases sequenciais:

1. **Análise:** detecta stack, arquitetura, persistência, entry point, comandos de validação e contratos externos.
2. **Auditoria:** cruza o código com o catálogo de anti-patterns e gera um relatório com severidade, evidência, impacto e recomendação.
3. **Refatoração:** aplica somente os findings aprovados, reorganiza o projeto e valida boot, testes, endpoints, persistência e contratos.

As fases 1 e 2 são somente leitura. A fase 2 termina com um pedido explícito de confirmação, impedindo alterações automáticas antes da revisão humana. A fase 3 só pode começar em uma mensagem posterior com autorização do usuário.

O `SKILL.md` concentra regras, sequência, gates e critérios de conclusão. O conhecimento detalhado foi separado em cinco referências obrigatórias:

| Referência | Responsabilidade |
|---|---|
| `project-analysis.md` | Detectar stack, mapear arquitetura, domínio, dados, contratos e comandos de validação |
| `anti-pattern-catalog.md` | Definir sinais, confirmação, impacto, severidade e correção dos anti-patterns |
| `audit-report-template.md` | Padronizar evidências, findings, cobertura, limitações e gate da auditoria |
| `mvc-guidelines.md` | Definir responsabilidades e dependências entre entry point, routes, controllers, services e persistência |
| `refactoring-playbook.md` | Fornecer transformações concretas com exemplos de código antes/depois |

Cada fase carrega apenas as referências necessárias. Essa separação reduz contexto desnecessário e permite evoluir catálogo, template e playbook sem tornar o arquivo principal extenso.

## Anti-patterns incluídos

O catálogo possui 17 anti-patterns. A seleção cobre segurança, arquitetura, integridade, performance e manutenibilidade encontradas nos três projetos, sem limitar a análise a problemas específicos de Flask ou Express.

| ID | Anti-pattern | Motivo da inclusão |
|---|---|---|
| AP-01 | Segredo ou credencial hardcoded | Evitar vazamento, acesso indevido e rotação difícil de credenciais |
| AP-02 | Injection | Detectar entrada controlável concatenada em SQL, shell, templates ou outros sinks |
| AP-03 | Autenticação ou autorização ausente/quebrada | Proteger rotas, senhas, tokens, papéis e recursos restritos |
| AP-04 | Exposição de dados sensíveis | Impedir que senhas, hashes, cartões e segredos apareçam em respostas ou logs |
| AP-05 | God Class ou God Module | Identificar módulos com responsabilidades independentes e alto acoplamento |
| AP-06 | Regra de negócio presa ao transporte | Separar regras de domínio dos detalhes de Flask, Express e HTTP |
| AP-07 | Estado global mutável ou conexão compartilhada indevida | Evitar corridas, vazamentos entre requests e testes instáveis |
| AP-08 | Fronteira transacional quebrada | Evitar escritas parciais, dados órfãos e estado inconsistente |
| AP-09 | Query N+1 | Evitar aumento linear de consultas e degradação conforme o volume cresce |
| AP-10 | Validação ausente ou inconsistente | Evitar dados inválidos, respostas 500 e contratos imprevisíveis |
| AP-11 | Tratamento de erro inadequado | Padronizar status, rollback, logging e mensagens seguras |
| AP-12 | Acesso sem limite ou agregação ineficiente | Controlar consumo de memória, latência e carga no banco |
| AP-13 | Duplicação estrutural | Evitar divergência entre validações, serializações e regras repetidas |
| AP-14 | Nomes opacos e magic values | Melhorar legibilidade e segurança das alterações |
| AP-15 | Código morto ou dependência não usada | Reduzir ruído e superfície de manutenção |
| AP-16 | Complexidade acidental | Reduzir custo cognitivo e chance de erro em fluxos desnecessariamente complexos |
| AP-17 | API deprecated | Confirmar APIs obsoletas pela versão e documentação oficial antes de recomendar substituição |

O catálogo também define regras contra falsos positivos: tamanho isolado não caracteriza God Module, loop sem consulta não caracteriza N+1 e `WHERE 1=1` isolado não caracteriza SQL Injection. Findings com a mesma causa raiz são consolidados para não inflar a auditoria.

## Como a skill permanece agnóstica de tecnologia

A skill não presume linguagem, framework, ORM, banco ou organização de pastas.
Primeiro identifica a stack por manifests, lockfiles, imports, configuração e entry points. Quando uma informação não pode ser comprovada, registra `não
determinada` em vez de inferir sem evidência.

As regras arquiteturais usam responsabilidades, não nomes fixos. Flask pode usar blueprints e application factory; Express pode usar routers, middlewares e factories; outras stacks devem usar equivalentes idiomáticos. A separação entre
transporte, orquestração, domínio e persistência continua igual.

As recomendações também descrevem alternativas: N+1 pode ser corrigido com JOIN, eager loading, batch ou agregação; persistência pode usar ORM ou SQL
parametrizado; erros podem ser centralizados pelos mecanismos nativos de cada framework. Exemplos em Python e JavaScript demonstram o padrão, mas não tornam a sintaxe obrigatória.

Por fim, a validação é descoberta no próprio projeto. A skill procura scripts de teste, lint, tipos, boot e smoke test, preservando método, rota, payload, resposta, status HTTP e efeitos observáveis independentemente da tecnologia.

## Desafios encontrados

- **Separar sinal de evidência:** O catálogo exige rastreamento da entrada até o sink, consulta dentro do loop para N+1 e verificação de middleware antes de apontar rota desprotegida, reduzindo falsos positivos.
- **Confirmar APIs deprecated:** Memória ou preferência estilística não bastam. A skill exige versão em uso, condição de depreciação e substituto confirmado em fonte oficial ou documentação local.
- **Aplicar MVC sem criar estrutura artificial:** Os projetos têm níveis de organização diferentes. A solução foi definir fronteiras e direção de dependências, aceitando nomes equivalentes oferecidos por cada stack.
- **Preservar comportamento durante a refatoração:** Mover responsabilidades pode quebrar contratos silenciosamente. A skill inventaria contratos antes da mudança e compara boot, endpoints, erros e efeitos persistentes depois dela.
- **Equilibrar autonomia e segurança:** Refatoração automática pode alterar código sem revisão. As duas primeiras fases ficaram somente leitura e um gate humano obrigatório foi colocado antes de qualquer edição.
- **Manter instruções completas sem sobrecarregar o `SKILL.md`:** Heurísticas, catálogo, template, guidelines e transformações foram movidos para referências obrigatórias carregadas por fase.

# Resultados

## Resumo dos relatórios de auditoria

| Projeto | Stack | CRITICAL | HIGH | MEDIUM | LOW | Total | Relatório |
|---|---|---:|---:|---:|---:|---:|---|
| `code-smells-project` | Python, Flask e SQLite | 4 | 4 | 5 | 2 | 15 | [`audit-code-smells-project.md`](reports/audit-code-smells-project.md) |
| `ecommerce-api-legacy` | Node.js, Express e SQLite | 4 | 4 | 5 | 3 | 16 | [`audit-ecommerce-api-legacy.md`](reports/audit-ecommerce-api-legacy.md) |
| `task-manager-api` | Python, Flask, Flask-SQLAlchemy e SQLite | 3 | 1 | 5 | 3 | 12 | [`audit-task-manager-api.md`](reports/audit-task-manager-api.md) |
| **Total** |  | **11** | **9** | **15** | **8** | **43** |  |

Os findings mais graves envolveram segredos hardcoded, SQL Injection,
autenticação ou autorização quebrada, exposição de dados sensíveis, falta de
atomicidade, God Modules e regras de negócio presas ao transporte HTTP.

## Comparação antes/depois

| Projeto | Antes | Depois |
|---|---|---|
| `code-smells-project` | Quatro módulos Python concentravam HTTP, regras, SQL e conexão global; segredo ficava no código | Composition root, configuração externa, routes, controllers, services, repositories, models, autenticação, validação e erros separados; conexão por request e testes de contrato |
| `ecommerce-api-legacy` | Três arquivos-fonte; `AppManager` concentrava rotas, checkout, relatório e persistência com callbacks e estado global | Composition root e 17 módulos em routes, controllers, services, repositories, models, middleware e infrastructure; transações, autenticação e testes de contrato |
| `task-manager-api` | Separação parcial, mas routes extensas continham regras, queries e serialização; MD5, token previsível e N+1 | Application factory, routes finas, controllers, repositories e services; hash adaptativo, token assinado, autorização por papel, eager loading, erros globais e testes de contrato |

Os métodos e caminhos originais permanecem registrados. `code-smells-project`
também recebeu `POST /logout`. As mudanças externas documentadas nos relatórios
incluem autenticação obrigatória, remoção de dados sensíveis das respostas,
validação com erros `4xx`, exclusão em cascata no e-commerce e desativação da
execução arbitrária de SQL.

## Checklist de validação

Legenda: `[x]` concluído; `[ ]` pendência documental.

| Fase e critério | `code-smells-project` | `ecommerce-api-legacy` | `task-manager-api` |
|---|:---:|:---:|:---:|
| **Fase 1 — Análise** |
| Linguagem detectada corretamente | [x] | [x] | [x] |
| Framework detectado corretamente | [x] | [x] | [x] |
| Domínio da aplicação descrito corretamente | [x] | [x] | [x] |
| Número de arquivos analisados condiz com a realidade | [x] | [x] | [x] |
| **Fase 2 — Auditoria** |
| Relatório segue o template definido nos arquivos de referência | [x] | [x] | [x] |
| Cada finding tem arquivo e linhas exatos | [x] | [x] | [x] |
| Findings ordenados por severidade (CRITICAL → LOW) | [x] | [x] | [x] |
| Mínimo de 5 findings identificados | [x] | [x] | [x] |
| Detecção de APIs deprecated incluída (se aplicável) | [x] N/A | [x] `sqlite3` | [x] `Model.query.get()` |
| Skill pausa e pede confirmação antes da Fase 3 | [x] | [x] | [x] |
| **Fase 3 —  Refatoração** |
| Estrutura de diretórios segue padrão MVC | [x] | [x] | [x] |
| Configuração extraída para módulo de config (sem hardcoded) | [x] | [x] | [x] |
| Models criados para abstrair dados | [x] | [x] | [x] |
| Views/Routes separadas para roteamento | [x] | [x] | [x] |
| Controllers concentram o fluxo da aplicação | [x] | [x] | [x] |
| Error handling centralizado | [x] | [x] | [x] |
| Entry point claro | [x] | [x] | [x] |
| Aplicação inicia sem erros | [x] | [x] | [x] |
| Endpoints originais respondem corretamente | [x] | [x] | [x] |

Os três relatórios salvos registram escopo, findings, severidade, evidência e tratamento.

## Logs das aplicações após a refatoração

Validação executada em 17/08/2026. Portas temporárias `5101`, `5102` e `5103` evitaram conflito com servidores locais existentes.

```text
code-smells-project
$ python -m unittest discover -s tests -v
Ran 8 tests in 2.358s
OK

ecommerce-api-legacy
$ npm run check
node --check src/app.js && node --check src/create-application.js
$ node test/contracts.test.js
tests 6 | pass 6 | fail 0

task-manager-api
$ python -m unittest discover -s tests -v
Ran 5 tests in 1.457s
OK
$ python -m compileall -q .
exit code 0
```

Boot real e smoke HTTP:

```text
code-smells-project | Running on http://127.0.0.1:5101
code-smells-project | GET /health | HTTP 200

ecommerce-api-legacy | LMS rodando na porta 5102
ecommerce-api-legacy | GET /api/admin/financial-report | HTTP 200

task-manager-api | Running on http://127.0.0.1:5103
task-manager-api | GET /health | HTTP 200
task-manager-api | POST /login + GET /tasks | HTTP 200
```

Processos temporários foram encerrados após o smoke test. Logs textuais foram usados como evidência reproduzível no lugar de screenshots.

# Como Executar

## Pré-requisitos

- Python 3 e `pip` para `code-smells-project` e `task-manager-api`.
- Node.js e `npm` para `ecommerce-api-legacy`.
- PowerShell para executar os comandos abaixo.

## Instalar dependências

### Projetos Python/Flask

Execute dentro de `code-smells-project` e repita dentro de `task-manager-api`:

```powershell
pip install -r requirements.txt
```

### Projeto Node.js/Express

```powershell
cd ecommerce-api-legacy
npm install
```

## Validar a refatoração

Execute cada bloco no diretório indicado.

### `code-smells-project`

```powershell
cd code-smells-project
$env:SECRET_KEY = "gere-um-segredo-forte"
python app.py
```

A aplicação sobe em `http://localhost:5000`. As variáveis opcionais são
`DATABASE_PATH`, `APP_ENV` e `FLASK_DEBUG`. As rotas administrativas e de
escrita exigem autenticação em `POST /login`.

### `ecommerce-api-legacy`

```powershell
cd ecommerce-api-legacy
npm install
npm run check
npm test
$env:ADMIN_API_TOKEN = "troque-este-token"
npm start
```

Com a aplicação rodando, abra outra janela e use o mesmo token:

```powershell
Invoke-RestMethod `
  -Uri "http://localhost:3000/api/admin/financial-report" `
  -Headers @{ Authorization = "Bearer troque-este-token" }
```

Resultado esperado: verificação sintática sem erro, seis testes aprovados e
relatório com HTTP `200`.

### `task-manager-api`

```powershell
cd task-manager-api
$env:SECRET_KEY = "gere-um-segredo-forte-fora-do-repositorio"
pip install -r requirements.txt
python seed.py
python -m unittest discover -s tests -v
python -m compileall -q .
python app.py
```

A aplicação sobe em `http://localhost:5000`. O `seed.py` popula `tasks.db` com
usuários, categorias e tarefas de exemplo e deve ser executado antes do primeiro
boot. O login documentado é `joao@email.com` / `admin1234`.

## Critério de sucesso

Refatoração validada quando:

- testes e verificações de sintaxe passam;
- aplicação inicia sem exceção;
- endpoints públicos retornam `200`;
- endpoints protegidos aceitam credencial válida e rejeitam credencial inválida;
- formatos, status e efeitos dos contratos inventariados permanecem iguais, salvo
  mudanças de segurança autorizadas;
- `git diff --check` não encontra erro e `git status --short` mostra apenas
  arquivos esperados.
