# Feature Implementation Workflow

Workflow para uma nova feature no **personal-finance-api**, inspirado em boas práticas e adaptado para a arquitetura do projeto.

## Ordem recomendada

```text
1. models.py + migration
2. errors.py / exceptions.py (exceções de domínio)
3. services.py (regras de negócio)
4. serializers.py (validação e formatação de payload da API)
5. views.py (DRF views/viewsets)
6. urls.py (registro no router ou paths diretos)
7. personal_finance_api/urls.py (include, caso seja um app novo)
8. admin.py (se a entidade for administrável)
9. testes em src/<app>/tests/
```

## Checklist executável

### Model e persistência

- [ ] Adicionar/alterar model em `src/<app>/models.py`
- [ ] Gerar migration: `cd src && uv run manage.py makemigrations <app>`
- [ ] Aplicar localmente: `cd src && uv run manage.py migrate`

### Camada de negócio

- [ ] Registrar exceções customizadas no `errors.py` (ou `exceptions.py` no caso do `core`) do app.
- [ ] Implementar operações de negócio no `services.py`, mantendo-as desacopladas da camada web/HTTP.

### API

- [ ] Criar Serializer em `src/<app>/serializers.py`
- [ ] Criar View/ViewSet em `src/<app>/views.py` — manter a view "fina", delegando a lógica complexa para o `services.py`.
- [ ] Configurar `permission_classes` se aplicável ao endpoint.

### Roteamento

- [ ] Registrar rota no `src/<app>/urls.py` (`DefaultRouter` ou `path`).
- [ ] Confirmar o `include` no `src/personal_finance_api/urls.py` (obrigatório para apps novos).

### Testes

- [ ] Criar ou atualizar factories no `src/<app>/tests/` se houver novos models (usando `factory-boy`).
- [ ] Escrever testes para os services e para a API (`test_*.py`).
- [ ] Rodar os testes via `pytest`.

### Qualidade

- [ ] Rodar os hooks de linting (Ruff): `uv run ruff check src`
- [ ] Rodar a formatação (Black/Ruff): `uv run black src` (ou similar)
- [ ] Garantir que os testes locais passem antes do commit.

## Comandos do projeto

| Ação | Comando |
| ---- | ------- |
| Migrations | `cd src && uv run manage.py makemigrations` |
| Migrate | `cd src && uv run manage.py migrate` |
| Testes | `pytest` |
| Lint (local) | `uv run ruff check src` |
| Servidor local | `cd src && uv run manage.py runserver` |

## Evidências

- Estrutura baseada nos diretórios encontrados como `services.py`, `errors.py`, `serializers.py` presentes em `src/transactions/` e `src/users/`.
- Uso de `uv` refletido nas dependências descritas no `pyproject.toml` e no arquivo `uv.lock`.
- O framework de testes configurado no `pyproject.toml` é o `pytest` (junto de `pytest-django`).

<!-- created: 2026-07-20 | modified: 2026-07-20 -->
