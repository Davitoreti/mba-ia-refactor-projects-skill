# task-manager-api

API de Task Manager em Python/Flask usada como entrada do desafio `refactor-arch`. Diferente dos outros projetos, este já possui alguma separação de camadas (`models/`, `routes/`, `services/`, `utils/`), mas ainda contém problemas arquiteturais e de qualidade.

## Como rodar

```bash
pip install -r requirements.txt
$env:SECRET_KEY = "gere-um-segredo-forte-fora-do-repositorio" # PowerShell
python seed.py
python app.py
```

A aplicação sobe em `http://localhost:5000`. O `seed.py` popula o banco SQLite (`tasks.db`) com usuários, categorias e tasks de exemplo — **rode-o antes do primeiro boot**, caso contrário os endpoints vão retornar listas vazias.

O `SECRET_KEY` é obrigatório. Use `DATABASE_URL`, `TOKEN_MAX_AGE_SECONDS` e
`FLASK_DEBUG` para sobrescrever, respectivamente, banco, validade do token e modo
de depuração. Não versione valores reais.

Após o seed, autentique em `POST /login` com `joao@email.com` / `admin1234`.
Envie o token retornado como `Authorization: Bearer <token>`. Endpoints de
usuários e mutações de categorias exigem `admin`; relatórios aceitam `admin` ou
`manager`.

## Validação

```bash
python -m unittest discover -s tests -v
python -m compileall -q .
```
