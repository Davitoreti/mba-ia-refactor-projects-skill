---
name: refactor-arch
description: Analisar, auditar e refatorar backends legados para uma arquitetura MVC preservando contratos externos. Usar para detectar stack e arquitetura, inventariar APIs, localizar anti-patterns e APIs deprecated, gerar relatório com severidade e evidências, ou executar refatoração arquitetural controlada em Python/Flask, Node.js/Express e stacks equivalentes.
---
# Refatoração arquitetural

Executar análise, auditoria e refatoração em três fases sequenciais. Adaptar nomes e técnicas à stack detectada. Não presumir linguagem, framework, ORM, banco ou estrutura.

## Regras obrigatórias

- Tratar diretório de trabalho como raiz do projeto-alvo.
- Preservar método, rota, parâmetros, payload, resposta, status HTTP e efeitos observáveis, salvo mudança autorizada.
- Respeitar alterações locais existentes. Não sobrescrever trabalho do usuário nem usar comandos destrutivos.
- Manter as fases 1 e 2 somente leitura. Não instalar dependências, iniciar serviços com efeitos persistentes, formatar ou criar arquivos.
- Basear todo finding em evidência verificável. Informar arquivo e linha exatos. Não inventar problemas para alcançar quantidade mínima.
- Ordenar findings por `CRITICAL`, `HIGH`, `MEDIUM` e `LOW`.
- Consolidar ocorrências com a mesma causa raiz. Não inflar contagens repetindo o mesmo problema.
- Encerrar a fase 2, pedir confirmação explícita e aguardar nova resposta. Não iniciar a fase 3 no mesmo turno.
- Parar e informar bloqueio quando referência obrigatória estiver ausente.

## Referências por fase

Resolver caminhos relativamente a este `SKILL.md` e ler cada arquivo indicado integralmente.

- Fase 1: `references/project-analysis.md`.
- Fase 2: `references/anti-pattern-catalog.md` e `references/audit-report-template.md`.
- Fase 3: `references/mvc-guidelines.md` e `references/refactoring-playbook.md`.

Não carregar referências de fases futuras antecipadamente. Não substituir regras das referências por suposições.

## Fase 1 — Análise

1. Inspecionar instruções, estado do versionamento, árvore, manifests, lockfiles, configuração, entry points, rotas, persistência e testes.
2. Ignorar dependências, caches, ambientes virtuais, cobertura, builds, artefatos gerados e dados locais.
3. Detectar com evidências:
   - linguagem e versão indicada ou `não determinada`;
   - framework e versão declarada ou resolvida;
   - dependências relevantes;
   - banco, driver e padrão de acesso a dados;
   - domínio e recursos;
   - arquitetura e fronteiras atuais;
   - entry point, arquivos-fonte e linhas analisadas;
   - comandos de instalação, boot, teste, lint e tipos.
4. Inventariar contratos externos: método, rota, parâmetros, payload, resposta, status e efeitos persistentes.
5. Registrar limitações da análise, inclusive código dinâmico, dependências ausentes ou contratos inferidos.
6. Imprimir:

```text
================================
FASE 1: ANÁLISE DO PROJETO
================================
Projeto:       <nome>
Linguagem:     <linguagem e versão ou não determinada>
Framework:     <framework e versão ou não determinada>
Dependências:  <principais dependências>
Domínio:       <descrição curta>
Arquitetura:   <estrutura atual>
Persistência:  <banco e acesso a dados>
Entry point:   <arquivo>
Código-fonte:  <arquivos analisados> | <linhas analisadas>
Contratos:     <quantidade de endpoints ou interfaces>
Validação:     <comandos disponíveis ou ausentes>
Limitações:    <lista curta ou nenhuma>
================================
```

Prosseguir diretamente para a fase 2, ainda em somente leitura.

## Fase 2 — Auditoria

1. Cruzar o código com todo o catálogo de anti-patterns.
2. Procurar APIs deprecated ou legadas. Confirmar versão em uso, condição de depreciação e substituto em fonte oficial ou documentação local antes de registrar.
3. Avaliar segurança, arquitetura, correção, performance, confiabilidade, manutenibilidade, observabilidade e qualidade.
4. Para cada finding, registrar:
   - identificador estável;
   - severidade e nome do anti-pattern;
   - arquivo e intervalo de linhas;
   - evidência objetiva;
   - impacto concreto;
   - recomendação compatível com stack;
   - contrato afetado e risco de regressão, quando aplicável.
5. Gerar o relatório na resposta usando `references/audit-report-template.md`.
6. Buscar pelo menos cinco findings e pelo menos um `CRITICAL` ou `HIGH`. Se o código não sustentar o mínimo, declarar o total real e explicar a lacuna.
7. Informar cobertura do catálogo, itens não aplicáveis e limitações.
8. Não gravar o relatório em disco.
9. Terminar exatamente com:

```text
Fase 2 concluída. Deseja executar a Fase 3 e aplicar a refatoração? [sim/não]
```

Parar. Aceitar apenas confirmação explícita em mensagem posterior. Se a resposta for negativa, encerrar sem mudanças. Se o usuário restringir escopo, aplicar a restrição na fase 3.

## Fase 3 — Refatoração

Executar somente após confirmação explícita posterior à fase 2.

1. Revalidar estado do versionamento. Interromper se mudanças novas conflitarem com arquivos necessários.
2. Determinar raiz do repositório pelo sistema de versionamento; se inexistente, usar raiz do projeto. Salvar relatório aprovado em `<repo-root>/reports/audit-<project-slug>.md`.
3. Relacionar cada alteração a findings aprovados e definir passos pequenos e reversíveis.
4. Aplicar `references/mvc-guidelines.md` sem forçar estrutura incompatível com a stack:
   - extrair configuração e segredos para ambiente com validação no boot;
   - manter Models responsáveis por entidades e persistência;
   - manter Views/Routes responsáveis pelo transporte HTTP;
   - manter Controllers responsáveis por orquestração de casos de uso;
   - separar serviços para regras que não pertencem ao transporte ou persistência;
   - centralizar tratamento e serialização de erros;
   - preservar entry point claro como composition root;
   - remover anti-patterns sem alterar contratos inventariados.
5. Aplicar transformações do playbook adequadas aos findings. Preferir dependências existentes; justificar dependência nova antes de adicioná-la.
6. Pedir autorização antes de instalar dependências ou executar comandos com efeitos externos.
7. Validar:
   - sintaxe, lint e tipos disponíveis;
   - testes existentes;
   - boot real da aplicação;
   - smoke test de cada contrato, incluindo erros relevantes;
   - persistência e transações críticas;
   - comparação de contratos antes/depois;
   - busca residual pelos findings tratados;
   - diff e arquivos inesperados.
8. Corrigir falhas e repetir validação. Não declarar sucesso parcial como completo.
9. Não afirmar `zero anti-patterns` sem nova auditoria completa.
10. Imprimir:

```text
================================
FASE 3: REFATORAÇÃO CONCLUÍDA
================================
Findings tratados: <IDs>
Estrutura criada:  <resumo MVC>
Contratos:         <preservados ou mudanças autorizadas>
Boot:              <comando e resultado>
Testes:            <comandos e resultados>
Endpoints:         <quantidade validada e resultado>
Pendências:        <lista ou nenhuma>
================================
```

## Critério de conclusão

Concluir somente quando os findings aprovados estiverem tratados, estrutura MVC estiver coerente, configuração sensível não estiver hardcoded, erros estiverem centralizados, aplicação iniciar e contratos originais responderem conforme inventário. Relatar qualquer item não validado como pendência.
