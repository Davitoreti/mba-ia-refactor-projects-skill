# code-smells-project

API de E-commerce em Python/Flask usada como entrada do desafio `refactor-arch`.

## Como rodar

```bash
pip install -r requirements.txt
set SECRET_KEY=gere-um-segredo-forte
python app.py
```

No PowerShell, use `$env:SECRET_KEY = "gere-um-segredo-forte"`. As variáveis
opcionais são `DATABASE_PATH`, `APP_ENV` e `FLASK_DEBUG`.

A aplicação sobe em `http://localhost:5000`. O banco SQLite (`loja.db`) é criado automaticamente no primeiro boot, já com produtos e usuários de exemplo.

As rotas administrativas e de escrita exigem login em `POST /login`. O usuário
administrativo inicial é `admin@loja.com`; a senha inicial permanece `admin123`
apenas para compatibilidade com o seed legado e deve ser alterada em ambientes
reais. O endpoint legado `POST /admin/query` permanece registrado, porém retorna
`410` depois da autenticação porque execução arbitrária de SQL foi desativada.
