# Anti-padrões

Lista derivada da estrutura real do projeto (`personal-finance-api`) e violações detectáveis em code review.

## Camadas e Responsabilidade

### 1. Regra de negócio na API (Fat Views)

- **Descrição:** Consultas complexas ao banco, `transaction.atomic` ou orquestração de regras de negócio feitas diretamente no `views.py` ou `serializers.py`.
- **Severidade:** CRÍTICA
- **Como detectar:** Loops de negócio ou múltiplas queries em uma view.
- **Correção:** Mover a lógica pesada para a camada de `services.py`.

### 2. Inversão de dependência (Services importando API)

- **Descrição:** A camada de domínio/serviço não deve saber sobre o contexto HTTP ou de serialização.
- **Severidade:** CRÍTICA
- **Como detectar:** Imports de `views.py` ou `serializers.py` dentro de `services.py` ou `models.py`.
- **Correção:** Remover import; passar apenas os dados limpos (DTOs ou primitivos) da view para o serviço.

### 3. Lógica pesada apenas nos Models

- **Descrição:** Métodos de model contendo orquestração de várias entidades, disparo de e-mails ou integrações, o que deveria estar em um serviço.
- **Severidade:** MÉDIA
- **Como detectar:** Models chamando clientes HTTP ou importando de outros domínios de forma acoplada.

## Estrutura do App

### 4. Novo módulo fora da estrutura padrão

- **Descrição:** Criar pastas ou arquivos de domínio fora do padrão estabelecido (`views.py`, `services.py`, `serializers.py`, `models.py`, `errors.py`).
- **Severidade:** MÉDIA
- **Como detectar:** Arquivos como `managers.py` ou `utils.py` com lógicas centrais exclusivas de domínio.

### 5. Funções utilitárias duplicadas

- **Descrição:** Helper genérico (ex: formatação de datas) copiado e colado em vários apps em vez de centralizado.
- **Severidade:** BAIXA
- **Como detectar:** Função idêntica em `transactions` e `users`.
- **Correção:** Mover para o app `core`.

### 6. Exceção sem classe no `errors.py`

- **Descrição:** Lançar `Exception` genérica ou usar validações puras na view em vez de mapear erros de domínio.
- **Severidade:** ALTA
- **Como detectar:** Uso de `raise Exception(...)` ou `raise ValidationError(...)` contendo regras de negócio fora de serializers/services.
- **Correção:** Mapear classes de erro no `errors.py` do app.

## API e Roteamento

### 7. ViewSet não registrado

- **Descrição:** Uma view ou ViewSet criado mas nunca exposto via router ou path.
- **Severidade:** ALTA
- **Como detectar:** Classe de view sem import correspondente em `urls.py`.

### 8. App não incluído no roteador central

- **Descrição:** O app possui rotas próprias mas faltou o `include` no arquivo raiz.
- **Severidade:** CRÍTICA (para features novas)
- **Como detectar:** Diff no `urls.py` do app mas ausente no `personal_finance_api/urls.py`.

### 9. Endpoints sem `permission_classes` claras

- **Descrição:** Falta de clareza nas permissões de uma view, deixando o endpoint aberto de forma acidental.
- **Severidade:** CRÍTICA
- **Como detectar:** ViewSet ou APIView sem `permission_classes` explícitas, dependendo apenas do default global.

### 10. Endpoints sem documentação OpenAPI (Swagger/drf-yasg)

- **Descrição:** Views ou actions personalizadas sem o decorator `@swagger_auto_schema` (já que o projeto usa `drf-yasg`).
- **Severidade:** MÉDIA
- **Como detectar:** Actions públicas não documentadas que recebem parâmetros de query/body específicos.

## Persistência e Async

### 11. Migrations manipuladas incorretamente

- **Descrição:** Alteração manual em arquivos de migration adicionando lógica de negócio indesejada.
- **Severidade:** ALTA
- **Como detectar:** Diff complexo na pasta `migrations/` sem ser uma data migration explícita.

### 12. Regra de negócio orquestrada na Task (Celery)

- **Descrição:** Tarefa assíncrona executando fluxos de negócio diretamente, em vez de delegar ao serviço.
- **Severidade:** MÉDIA
- **Como detectar:** `tasks.py` extenso e com lógicas de banco próprias.

## Testes

### 13. Mudança estrutural sem teste correspondente

- **Descrição:** Criação de novos serviços ou views sem espelhar na pasta de testes do app.
- **Severidade:** ALTA
- **Como detectar:** Novo arquivo/função em `services.py` sem um arquivo em `src/<app>/tests/`.

### 14. Factories declaradas de forma inconsistente

- **Descrição:** Uso de inicializações de model hardcoded ou `Factory` inline dispersa nos testes.
- **Severidade:** BAIXA
- **Como detectar:** Não utilização do `factory-boy` onde já é o padrão estabelecido no projeto.

## Imports e Dependências

### 15. Importações relativas profundas

- **Descrição:** Uso excessivo de `from ..` em vez de caminhos absolutos do app.
- **Severidade:** BAIXA
- **Como detectar:** Imports relativos subindo mais de um nível (`..`).

### 16. Dependência Circular entre Apps

- **Descrição:** App A (ex: `transactions`) importa do App B (`users`), e o App B importa do App A simultaneamente nas camadas de model ou service.
- **Severidade:** ALTA
- **Como detectar:** Erros de importação no momento de execução ou linting.

## Referências Cruzadas

- Nomenclatura: [naming.md](./naming.md)
- Organização em camadas: [layers.md](./layers.md)
- Checklist de desenvolvimento: [feature-workflow.md](./feature-workflow.md)

<!-- created: 2026-07-20 | modified: 2026-07-20 -->
