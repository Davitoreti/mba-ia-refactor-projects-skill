# Auditoria arquitetural — ecommerce-api-legacy

## Escopo

- Raiz analisada: `ecommerce-api-legacy`
- Revisão/branch: `main` em `bec830f`
- Operação: somente leitura
- Estado existente: `.codex/` não rastreado, preservado
- Exclusões: dependências ausentes, builds e banco efêmero

## Resumo do projeto

| Campo | Resultado | Evidência |
|---|---|---|
| Linguagem | JavaScript CommonJS; Node não fixado | `package.json:5-7`, `src/app.js:1-3` |
| Framework | Express 4.22.1 resolvido | `package.json:9-11`, `package-lock.json` |
| Domínio | Cursos, usuários, matrículas e pagamentos | `src/AppManager.js:12-21` |
| Arquitetura atual | Monólito concentrado em `AppManager` | `src/AppManager.js:4-138` |
| Persistência | SQLite em memória, SQL direto e callbacks | `src/AppManager.js:1-22` |
| Entry point | `src/app.js` | `package.json:5-7` |
| Código-fonte | 3 arquivos, 180 linhas físicas | `Get-ChildItem src -Filter *.js` + `Get-Content` |
| Testes | Ausentes; nenhum script de teste | `package.json:6-8` |

## Contratos inventariados

| Método | Rota | Entrada | Sucesso | Erros relevantes | Efeito |
|---|---|---|---|---|---|
| POST | `/api/checkout` | JSON: `usr`, `eml`, `pwd`, `c_id`, `card` | `200`, `{msg, enrollment_id}` | `400`, `404`, `500` em texto | Pode criar usuário, matrícula, pagamento, auditoria e cache |
| GET | `/api/admin/financial-report` | Nenhuma entrada explícita | `200`, array de cursos com receita e alunos | `500` apenas na consulta inicial; erros internos inconsistentes | Leitura de cursos, matrículas, usuários e pagamentos |
| DELETE | `/api/users/:id` | `id` no path | `200`, texto fixo | Erro do banco ignorado | Remove usuário e deixa referências órfãs |

## Sumário dos findings

| Severidade | Quantidade |
|---|---:|
| CRITICAL | 4 |
| HIGH | 4 |
| MEDIUM | 5 |
| LOW | 3 |
| **Total** | **16** |

## Findings

### SEC-001 — [CRITICAL] Autorização ausente

- **Local:** `src/app.js:5-10`, `src/AppManager.js:80-137`
- **Catálogo:** AP-03
- **Evidência:** não existe middleware de autenticação ou autorização antes do relatório administrativo e da exclusão de usuários.
- **Impacto:** qualquer cliente pode consultar dados financeiros ou excluir usuários.
- **Recomendação:** autenticação real e autorização administrativa com negação por padrão.
- **Contrato afetado:** `GET /api/admin/financial-report`, `DELETE /api/users/:id`
- **Risco de regressão:** alto; adicionará respostas `401/403` que hoje não existem.

### SEC-002 — [CRITICAL] Segredos hardcoded

- **Local:** `src/utils.js:1-6`
- **Catálogo:** AP-01
- **Evidência:** senha de banco e chave `pk_live_*` estão diretamente no código.
- **Impacto:** exposição e rotação difícil de credenciais.
- **Recomendação:** carregar variáveis de ambiente e validar configuração no boot.
- **Contrato afetado:** bootstrap e checkout
- **Risco de regressão:** médio; configuração ausente deve impedir boot.

### SEC-003 — [CRITICAL] Cartão e chave de pagamento expostos em log

- **Local:** `src/AppManager.js:43-46`
- **Catálogo:** AP-04
- **Evidência:** o número integral do cartão e a chave do gateway são interpolados em `console.log`.
- **Impacto:** vazamento de dados de pagamento e credencial em logs.
- **Recomendação:** remover a chave do log e, quando indispensável, registrar somente cartão mascarado.
- **Contrato afetado:** `POST /api/checkout`
- **Risco de regressão:** baixo; muda apenas observabilidade indevida.

### SEC-004 — [CRITICAL] Armazenamento inseguro de senhas

- **Local:** `src/AppManager.js:12,18,66-71`, `src/utils.js:17-22`
- **Catálogo:** AP-03
- **Evidência:** seed armazena `"123"` em texto puro; usuários novos usam uma transformação Base64 determinística truncada para dez caracteres.
- **Impacto:** credenciais são recuperáveis e colisões são prováveis.
- **Recomendação:** hash adaptativo com salt; nunca criar senha padrão silenciosamente.
- **Contrato afetado:** `POST /api/checkout`
- **Risco de regressão:** médio; dados existentes exigirão estratégia de migração.

### ARCH-001 — [HIGH] Atomicidade e integridade relacional quebradas

- **Local:** `src/AppManager.js:12-16,50-61,66-74,131-136`
- **Catálogo:** AP-08
- **Evidência:** checkout executa várias escritas sem transação; pagamento recusado pode deixar usuário criado; falha posterior deixa matrícula ou pagamento parcial. As tabelas não têm foreign keys e a exclusão deixa registros órfãos.
- **Impacto:** dados parciais, pagamentos e matrículas inconsistentes.
- **Recomendação:** constraints, transação única com rollback e política explícita de exclusão.
- **Contrato afetado:** checkout e exclusão de usuário
- **Risco de regressão:** alto; efeitos persistentes precisam ser preservados ou deliberadamente corrigidos.

### ARCH-002 — [HIGH] God Class

- **Local:** `src/AppManager.js:4-138`
- **Catálogo:** AP-05
- **Evidência:** uma classe cria banco/schema/seeds, registra rotas, valida HTTP, processa pagamentos, persiste entidades e serializa respostas.
- **Impacto:** forte acoplamento e testes isolados difíceis.
- **Recomendação:** separar routes, controllers, services e repositories/models, mantendo `app.js` como composition root.
- **Contrato afetado:** todos
- **Risco de regressão:** alto devido à concentração de responsabilidades.

### ARCH-003 — [HIGH] Regras de negócio presas ao transporte HTTP

- **Local:** `src/AppManager.js:28-78`
- **Catálogo:** AP-06
- **Evidência:** o handler decide aprovação pelo prefixo do cartão e coordena criação de usuário, matrícula, pagamento e auditoria.
- **Impacto:** checkout não pode ser testado ou reutilizado sem Express.
- **Recomendação:** extrair caso de uso e serviço de pagamento; deixar a rota mapear HTTP.
- **Contrato afetado:** `POST /api/checkout`
- **Risco de regressão:** alto.

### ARCH-004 — [HIGH] Estado global mutável

- **Local:** `src/utils.js:9-15,25`
- **Catálogo:** AP-07
- **Evidência:** `globalCache` é compartilhado por todos os requests, mutado sem limite ou ciclo de vida e exportado diretamente.
- **Impacto:** vazamento entre requests, crescimento de memória e testes dependentes de ordem.
- **Recomendação:** abstrair cache com escopo e política de expiração explícitos.
- **Contrato afetado:** efeito colateral do checkout
- **Risco de regressão:** médio.

### PERF-001 — [MEDIUM] Query N+1

- **Local:** `src/AppManager.js:83-127`
- **Catálogo:** AP-09
- **Evidência:** após buscar cursos, há uma consulta de matrículas por curso e duas consultas por matrícula.
- **Impacto:** número aproximado de queries cresce como `1 + C + 2E`.
- **Recomendação:** JOIN/agregação ou consultas em lote.
- **Contrato afetado:** relatório financeiro
- **Risco de regressão:** médio; ordem e formato precisam permanecer iguais.

### QUAL-001 — [MEDIUM] Validação insuficiente

- **Local:** `src/AppManager.js:29-38,45-48,68`
- **Catálogo:** AP-10
- **Evidência:** apenas presença parcial é verificada; senha pode ser omitida, formatos e tipos não são validados, e `cc.startsWith()` falha para valor numérico.
- **Impacto:** dados inválidos e respostas `500` imprevisíveis.
- **Recomendação:** schema centralizado com tipos, formato, tamanho e erros `400` estáveis.
- **Contrato afetado:** checkout
- **Risco de regressão:** médio.

### QUAL-002 — [MEDIUM] Erros ignorados ou inconsistentes

- **Local:** `src/AppManager.js:37-61,92-106,131-136`
- **Catálogo:** AP-11
- **Evidência:** callbacks internos do relatório, auditoria e DELETE ignoram `err`; o DELETE responde sucesso mesmo se nada for removido ou ocorrer falha.
- **Impacto:** falso sucesso, request pendurado ou exceção fora do fluxo do Express.
- **Recomendação:** erros tipados e middleware central; conferir `changes` no DELETE.
- **Contrato afetado:** todos
- **Risco de regressão:** alto; status observáveis podem mudar.

### PERF-002 — [MEDIUM] Relatório sem paginação ou limite

- **Local:** `src/AppManager.js:83-127`
- **Catálogo:** AP-12
- **Evidência:** todos os cursos e todas as matrículas são carregados e agregados em memória.
- **Impacto:** latência e consumo de memória crescem sem limite.
- **Recomendação:** paginação e agregação SQL.
- **Contrato afetado:** relatório financeiro
- **Risco de regressão:** alto se paginação alterar o formato atual.

### TECH-001 — [MEDIUM] Dependência de persistência deprecated

- **Local:** `package.json:11`, `package-lock.json:2021-2022`
- **Catálogo:** AP-17
- **Evidência:** o projeto resolve `sqlite3@5.1.7`; o repositório oficial declara `node-sqlite3` deprecated e sem manutenção. [Repositório oficial do node-sqlite3](https://github.com/TryGhost/node-sqlite3)
- **Impacto:** ausência de manutenção e risco futuro de compatibilidade/segurança.
- **Recomendação:** primeiro fixar uma versão do Node; para Node compatível, avaliar `node:sqlite`, disponível desde Node 22.5 e atualmente em estágio release candidate. [Documentação oficial do Node.js](https://nodejs.org/download/release/latest-v24.x/docs/api/sqlite.html)
- **Contrato afetado:** persistência de todos os endpoints
- **Risco de regressão:** alto; APIs assíncronas atuais e síncronas do substituto têm semânticas distintas.

### QUAL-003 — [LOW] Nomes opacos e valores mágicos

- **Local:** `src/AppManager.js:29-46`
- **Catálogo:** AP-14
- **Evidência:** variáveis como `u`, `e`, `p`, `cid`, `cc` e prefixo `"4"` ocultam conceitos do domínio.
- **Impacto:** leitura e alteração inseguras.
- **Recomendação:** nomes de domínio e política explícita de autorização do pagamento.
- **Contrato afetado:** checkout
- **Risco de regressão:** baixo.

### QUAL-004 — [LOW] Código morto

- **Local:** `src/utils.js:10,25`, `src/AppManager.js:2`
- **Catálogo:** AP-15
- **Evidência:** `totalRevenue` é exportado e importado, mas nunca lido ou atualizado.
- **Impacto:** ruído e intenção arquitetural enganosa.
- **Recomendação:** remover ou implementar por meio de uma agregação coerente.
- **Contrato afetado:** nenhum
- **Risco de regressão:** baixo.

### QUAL-005 — [LOW] Complexidade acidental por callbacks aninhados

- **Local:** `src/AppManager.js:37-76,83-128`
- **Catálogo:** AP-16
- **Evidência:** checkout e relatório possuem múltiplos níveis de callbacks, contadores manuais e respostas emitidas em ramos internos.
- **Impacto:** difícil assegurar resposta única, propagação de erros e conclusão das operações.
- **Recomendação:** adapters Promise/async e funções coesas, preservando a ordem observável.
- **Contrato afetado:** checkout e relatório
- **Risco de regressão:** médio.

## Cobertura do catálogo

| ID | Resultado | Justificativa |
|---|---|---|
| AP-01 | Encontrado | SEC-002 |
| AP-02 | Não encontrado | Todas as entradas SQL observadas usam placeholders |
| AP-03 | Encontrado | SEC-001 e SEC-004 |
| AP-04 | Encontrado | SEC-003 |
| AP-05 | Encontrado | ARCH-002 |
| AP-06 | Encontrado | ARCH-003 |
| AP-07 | Encontrado | ARCH-004 |
| AP-08 | Encontrado | ARCH-001 |
| AP-09 | Encontrado | PERF-001 |
| AP-10 | Encontrado | QUAL-001 |
| AP-11 | Encontrado | QUAL-002 |
| AP-12 | Encontrado | PERF-002 |
| AP-13 | Não encontrado | Não há repetição estrutural suficiente |
| AP-14 | Encontrado | QUAL-003 |
| AP-15 | Encontrado | QUAL-004 |
| AP-16 | Encontrado | QUAL-005 |
| AP-17 | Encontrado | TECH-001 |

## APIs deprecated

- Confirmada: dependência `sqlite3@5.1.7`/`node-sqlite3`, cujo projeto oficial está marcado como deprecated e sem manutenção.
- Não foi confirmada depreciação das APIs Express usadas. Express 4.x continua suportado e `express()`, `express.json()`, rotas e `app.listen()` permanecem documentados. [Suporte do Express](https://expressjs.com/en/support/), [API oficial 4.x](https://expressjs.com/en/4x/api/)

## Limitações

- Dependências não estavam instaladas; boot e smoke tests não foram executados.
- Não há suíte de testes para confirmar detalhes não explícitos dos contratos.
- A versão do Node.js não está fixada em `package.json`, `.nvmrc` ou equivalente.
- O banco em memória é populado no boot; executá-lo produziria efeitos locais.
- A análise de callbacks é estática.

## Prioridade sugerida

1. Remover logs sensíveis e externalizar/rotacionar segredos.
2. Proteger relatório e exclusão com autenticação/autorização.
3. Corrigir senhas, transações, constraints e propagação de erros.
4. Separar MVC/casos de uso preservando os contratos inventariados.
5. Eliminar N+1 e planejar migração de `node-sqlite3`.

## Gate

Fase 2 concluída. Deseja executar a Fase 3 e aplicar a refatoração? [sim/não]
