# Catálogo de anti-patterns

Aplicar severidade pelo impacto real. Níveis seguem padrão do desafio; contexto pode elevar ou reduzir severidade com justificativa.

## Sumário

1. Segurança crítica
2. Arquitetura de alta severidade
3. Performance e qualidade média
4. Manutenibilidade baixa
5. APIs deprecated
6. Regras de consolidação

## Segurança crítica

### AP-01 — Segredo ou credencial hardcoded — CRITICAL

- **Sinais:** chaves, senhas, tokens ou credenciais SMTP/DB no código, seed público ou resposta HTTP.
- **Confirmar:** valor utilizável e sensível, não placeholder claramente documentado.
- **Impacto:** acesso indevido, vazamento e rotação difícil.
- **Correção:** variável de ambiente, secret manager e validação no boot; remover exposição em logs e respostas.

### AP-02 — Injection — CRITICAL

- **Sinais:** concatenação/interpolação de entrada em SQL, shell, template, expressão ou query administrativa.
- **Confirmar:** rastrear dado controlável até sink; `WHERE 1=1` isolado não caracteriza injection.
- **Impacto:** leitura, alteração ou execução não autorizada.
- **Correção:** parâmetros, APIs estruturadas, allowlist e menor privilégio.

### AP-03 — Autenticação ou autorização ausente/quebrada — CRITICAL

- **Sinais:** rota administrativa pública, token previsível, senha em texto puro, hash fraco, papel não verificado.
- **Confirmar:** procurar middleware global e proteção específica antes de registrar.
- **Impacto:** acesso ou operação indevida.
- **Correção:** autenticação real, hash adaptativo, autorização por recurso/papel e negação por padrão.

### AP-04 — Exposição de dados sensíveis — CRITICAL

- **Sinais:** senha, hash, cartão ou segredo em JSON, log, exceção ou health check.
- **Confirmar:** distinguir metadado inofensivo de dado reutilizável ou regulado.
- **Impacto:** comprometimento de contas e privacidade.
- **Correção:** DTO seguro, mascaramento, logging mínimo e mensagens sanitizadas.

## Arquitetura de alta severidade

### AP-05 — God Class ou God Module — HIGH

- **Sinais:** módulo concentra bootstrap, rotas, banco, regras, integrações e serialização; muitas razões independentes para mudança.
- **Confirmar:** tamanho sozinho não basta; demonstrar responsabilidades e acoplamentos distintos.
- **Impacto:** testes difíceis, regressão ampla e baixa coesão.
- **Correção:** separar por responsabilidade e domínio, mantendo composition root fino.

### AP-06 — Regra de negócio presa ao transporte — HIGH

- **Sinais:** handler HTTP calcula preço, decide status, envia notificações ou controla transação.
- **Confirmar:** validação puramente HTTP e mapeamento de resposta pertencem à rota.
- **Impacto:** casos de uso não reutilizáveis e testes dependentes do framework.
- **Correção:** mover orquestração para controller/use case e regras para serviço ou domínio.

### AP-07 — Estado global mutável ou conexão compartilhada indevida — HIGH

- **Sinais:** cache global, singleton mutável, conexão única entre requests, lista de eventos em memória.
- **Confirmar:** avaliar concorrência, ciclo de vida e isolamento oferecido pelo framework.
- **Impacto:** corrida, vazamento entre requests e testes instáveis.
- **Correção:** dependência injetada com escopo explícito, pool ou storage apropriado.

### AP-08 — Fronteira transacional quebrada — HIGH

- **Sinais:** operação faz múltiplas escritas relacionadas sem transação ou confirma parcialmente antes de terminar.
- **Confirmar:** verificar comportamento real do driver/ORM e compensações existentes.
- **Impacto:** dados órfãos ou estado inconsistente.
- **Correção:** transação única no caso de uso, rollback e constraints de integridade.

## Performance e qualidade média

### AP-09 — Query N+1 — MEDIUM

- **Sinais:** consulta de coleção seguida por consulta dentro de loop para cada item.
- **Confirmar:** contar padrão de consultas; loop sem consulta não é N+1.
- **Impacto:** latência e carga crescem com volume.
- **Correção:** JOIN, eager loading, batch query ou agregação.

### AP-10 — Validação ausente ou inconsistente — MEDIUM

- **Sinais:** presença sem tipo, faixa ou formato; conversão que lança erro; regras divergentes entre create/update.
- **Confirmar:** procurar schema, middleware ou validação anterior no fluxo.
- **Impacto:** erro 500, dados inválidos e contrato imprevisível.
- **Correção:** schema centralizado e erro 4xx estável.

### AP-11 — Tratamento de erro inadequado — MEDIUM

- **Sinais:** `except:` genérico, erro interno devolvido ao cliente, callback ignora erro, respostas inconsistentes.
- **Confirmar:** mapear handlers globais antes de registrar.
- **Impacto:** diagnóstico ruim, vazamento e status incorreto.
- **Correção:** exceções tipadas, rollback, logging estruturado e middleware central.

### AP-12 — Acesso sem limite ou agregação ineficiente — MEDIUM

- **Sinais:** listagem completa sem paginação, várias contagens independentes, carga de todos registros para contar.
- **Confirmar:** considerar tamanho esperado e uso administrativo restrito.
- **Impacto:** memória, latência e indisponibilidade sob crescimento.
- **Correção:** paginação, agregação SQL e limites explícitos.

### AP-13 — Duplicação estrutural — MEDIUM

- **Sinais:** serialização, validação, cálculo ou mapeamento de erros repetido em múltiplos endpoints.
- **Confirmar:** evitar abstrair coincidência pequena sem chance real de divergência.
- **Impacto:** correções inconsistentes e manutenção repetida.
- **Correção:** extrair schema, mapper, política ou serviço coeso.

## Manutenibilidade baixa

### AP-14 — Nomes opacos e magic values — LOW

- **Sinais:** variáveis sem significado, listas/status repetidos, limites e mensagens soltos.
- **Impacto:** leitura difícil e alteração insegura.
- **Correção:** nomes de domínio, enums, constantes e funções expressivas.

### AP-15 — Código morto ou dependência não usada — LOW

- **Sinais:** imports, helpers, configuração, variável ou pacote sem consumidores.
- **Confirmar:** procurar uso dinâmico, registro por reflexão e side effects de importação.
- **Impacto:** ruído, superfície de manutenção e dependência desnecessária.
- **Correção:** remover ou integrar com teste que demonstre uso.

### AP-16 — Complexidade acidental — LOW

- **Sinais:** condicionais aninhadas, booleanos verbosos, montagem manual repetitiva, comentários compensando código confuso.
- **Impacto:** maior custo cognitivo e chance de erro.
- **Correção:** guard clauses, funções pequenas e APIs idiomáticas.

## APIs deprecated ou legadas

### AP-17 — API deprecated — severidade por impacto

- **Sinais:** warning, documentação oficial, changelog, anotação do compilador ou API listada como legacy na versão usada.
- **Confirmar:** versão declarada/resolvida, uso real, fonte oficial e equivalente recomendado.
- **Não registrar:** apenas por memória, preferência estilística ou existência de API mais nova.
- **Classificar:** `LOW` para migração simples sem risco atual; `MEDIUM` quando remoção próxima, warning operacional ou manutenção relevante; elevar somente com impacto concreto.
- **Correção:** migrar preservando semântica e adicionar teste de regressão.

## Regras de consolidação

- Usar um finding por causa raiz e agrupar ocorrências relacionadas.
- Separar findings quando correção, impacto ou contrato forem independentes.
- Não contar mesma linha como injection, validação e erro sem explicar causas distintas.
- Informar falso positivo descartado quando sinal forte não se confirmar.
- Não rebaixar falha de segurança para criar distribuição artificial.
