# Guidelines de arquitetura MVC

Aplicar MVC como separação de responsabilidades para backend. Preservar convenções da stack e evitar estrutura cerimonial sem benefício.

## Dependências desejadas

```text
Entry point/composition root
  cria dependências e registra rotas

Routes/Views
  traduz HTTP para chamada de controller

Controllers
  orquestram casos de uso e mapeiam resultado

Services/domain
  executam regras e integrações

Models/repositories
  representam dados e persistência
```

Dependências apontam para dentro. Models e serviços de domínio não importam Flask, Express, request ou response.

## Entry point

Responsável por criar aplicação, carregar e validar configuração, montar dependências, registrar middlewares/rotas e iniciar servidor explicitamente.

Não colocar regra de negócio, SQL ou seed destrutivo no import.

## Views/Routes

Responsáveis por declarar método/caminho, extrair entrada, chamar validação, invocar controller e serializar resposta.

Não calcular preço, controlar transação, acessar SQL diretamente ou executar integração externa.

## Controllers

Responsáveis por coordenar caso de uso, chamar services/repositories, decidir fluxo e retornar resultado independente do framework quando viável.

Não concentrar detalhes SQL, credenciais, cliente SMTP ou formatação repetida.

## Services e domínio

Usar para cálculo, políticas, checkout, estoque, notificações, autenticação, relatórios e coordenação transacional.

Evitar serviço genérico que apenas encaminha chamadas sem adicionar regra ou fronteira testável.

## Models e repositories

Models representam entidades, invariantes e mapeamento persistente. Repositories encapsulam consultas quando reduzirem acoplamento ou melhorarem testes.

- Usar queries parametrizadas ou ORM.
- Declarar relações e constraints relevantes.
- Evitar serializar segredos.
- Evitar regra dependente de HTTP.
- Manter transação no nível do caso de uso.

## Configuração

- Ler segredo e configuração variável do ambiente.
- Validar obrigatórios no boot.
- Usar defaults somente para valores seguros.
- Nunca devolver segredo em endpoint ou log.
- Separar ambientes quando necessário.

## Erros

- Definir erros de domínio/aplicação estáveis.
- Mapear erros para HTTP em middleware central.
- Preservar status e formato existentes, salvo correção autorizada.
- Fazer rollback antes de responder erro transacional.
- Registrar contexto sem expor dado sensível.

## Contratos

Antes da mudança, registrar método, rota, entrada, resposta, status e efeitos. Depois, comparar todos campos.

Mudança de segurança pode alterar comportamento inseguro. Documentar contrato anterior, risco corrigido, novo comportamento e autorização quando houver quebra externa.

## Adaptação por stack

- Flask: blueprints como Routes; application factory como composition root; handlers para erros.
- Express: routers como Views/Routes; middleware para validação/erros; factories recebem dependências.
- Outras stacks: usar equivalentes idiomáticos, mantendo responsabilidades e direção de dependência.

Não exigir nomes `models`, `views` e `controllers` quando stack usa termos equivalentes e separação está clara.

## Critérios arquiteturais

- Entry point fino.
- Transporte sem regra pesada.
- Persistência sem HTTP.
- Configuração sensível externa.
- Erros centralizados.
- Dependências explícitas.
- Transações alinhadas ao caso de uso.
- Contratos preservados.
