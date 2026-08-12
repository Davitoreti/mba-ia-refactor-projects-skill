# Template de relatório de auditoria

Usar esta estrutura sem omitir seções. Escrever `não determinado`, `não aplicável` ou `não validado` em vez de inventar dados.

```markdown
# Auditoria arquitetural — <projeto>

## Escopo

- Raiz analisada: `<caminho>`
- Revisão/branch: `<valor ou não determinado>`
- Operação: somente leitura
- Exclusões: `<dependências, builds, dados locais>`

## Resumo do projeto

| Campo | Resultado | Evidência |
|---|---|---|
| Linguagem | <valor> | `<arquivo:linha>` |
| Framework | <valor> | `<arquivo:linha>` |
| Domínio | <valor> | `<arquivos>` |
| Arquitetura atual | <valor> | `<arquivos>` |
| Persistência | <valor> | `<arquivo:linha>` |
| Entry point | <valor> | `<arquivo:linha>` |
| Código-fonte | <N arquivos / N linhas> | `<comando>` |
| Testes | <comando ou ausente> | `<manifest/config>` |

## Contratos inventariados

| Método/tipo | Rota/interface | Entrada | Sucesso | Erros relevantes | Efeito |
|---|---|---|---|---|---|
| <GET> | </items> | <query> | <200 schema> | <400/500> | <leitura> |

## Sumário dos findings

| Severidade | Quantidade |
|---|---:|
| CRITICAL | <N> |
| HIGH | <N> |
| MEDIUM | <N> |
| LOW | <N> |
| **Total** | **<N>** |

## Findings

### <ID> — [<SEVERIDADE>] <nome>

- **Local:** `<arquivo:linha-inicial-linha-final>`
- **Catálogo:** `<AP-NN>`
- **Evidência:** <comportamento objetivo observado>
- **Impacto:** <efeito concreto>
- **Recomendação:** <correção compatível com stack>
- **Contrato afetado:** <rota/interface ou nenhum>
- **Risco de regressão:** <baixo/médio/alto e motivo>

## Cobertura do catálogo

| ID | Anti-pattern | Resultado | Evidência/justificativa |
|---|---|---|---|
| AP-01 | Segredo hardcoded | encontrado/não encontrado/não aplicável | <valor> |

## APIs deprecated

- <API, versão, arquivo/linha, fonte de confirmação e substituto>
- Ou: `Nenhuma ocorrência confirmada na versão detectada.`

## Limitações

- <dependência ausente, código dinâmico, boot não executado ou nenhuma>

## Prioridade sugerida

1. <segurança e integridade>
2. <fronteiras arquiteturais>
3. <performance e manutenção>

## Gate

Fase 2 concluída. Deseja executar a Fase 3 e aplicar a refatoração? [sim/não]
```

## Regras do relatório

- Ordenar findings por severidade e, dentro dela, por impacto.
- Usar IDs estáveis como `ARCH-001`, `SEC-001`, `PERF-001` e `QUAL-001`.
- Citar linhas do estado auditado antes da refatoração.
- Diferenciar evidência de recomendação.
- Não representar arquivo apenas proposto como código existente.
- Não declarar API deprecated sem confirmação por versão.
- Não prometer `zero anti-patterns` sem nova auditoria completa.
