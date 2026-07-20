# Specs de tasks

Specs numeradas geradas pela skill `create-plan` e executadas pela skill `execute-plan`.

## Convenções

| Item | Regra |
| ---- | ----- |
| Pasta | `.specify/specs/` |
| Nome | `{NNN}_{slug}.md` (ex.: `001_create_company_app.md`) |
| Numeração | `001`, `002`, … — próximo = `max(NNN) + 1` |
| Referência ativa | `.specify/spec_ref.json` aponta para a spec em execução |
| Template | `.specify/templates/spec-template.md` |

## `spec_ref.json`

```json
{
  "name": "001_create_company_app",
  "path": ".specify/specs/001_create_company_app.md",
  "completedSession": "Fase 1 — Scaffold (MVP)",
  "updatedAt": "2026-06-23"
}
```

| Campo | Descrição |
| ----- | --------- |
| `name` | Nome do arquivo sem extensão |
| `path` | Caminho relativo à root do repositório |
| `completedSession` | Última fase concluída (título `## Fase N — …`), ou `null` |
| `updatedAt` | Data ISO (`YYYY-MM-DD`) |

## Skills relacionadas

| Skill | Papel |
| ----- | ----- |
| `create-plan` | Cria ou revisa estrutura da spec (não implementa código) |
| `execute-plan` | Executa fases da spec ativa e atualiza `spec_ref.json` |
| `create-backend-feature` | Guia de implementação por camada Django/DRF |
| `get-code-pattern` | Gera/atualiza `.specify/pattern/` |

## Ordem típica de fases (apps em camadas)

1. Model + migration
2. `errors.py` / `core/dto.py`
3. `repositories/` + testes
4. `services/` + testes
5. `container.py`
6. `api/` (serializers, views) + `permissions.py`
7. `urls.py` + include na raiz
8. Testes de integração / `test_routes.py`
9. Opcional: `tasks.py`, `mails.py`, `admin.py`

Detalhes em `.specify/pattern/feature-workflow.md`.

## Regras

- Todas as tarefas começam **desmarcadas** (`- [ ]`).
- Use paths reais sob `src/` e `src/tests/`.
- Não inclua segredos, credenciais ou `.env`.
- Rodapé obrigatório em cada spec: `<!-- criação: YYYY-MM-DD | modificação: YYYY-MM-DD -->`.

<!-- criação: 2026-06-23 | modificação: 2026-07-19 -->