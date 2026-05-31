# shopping-cart-api

## Integrantes

- Lucas Gabriel Volpato Martins Bezerra
- Ana Laura Martins
- Luisa de Matos

## Tema do projeto

Carrinho de compras.

## Backend

O backend do projeto será desenvolvido em Python, utilizando FastAPI com SQLAlchemy, Alembic e banco de dados PostgreSQL (NeonDB).

---

## Pré-requisitos

- Python 3.11+
- pip
- Docker e Docker Compose (para execução em container)

---

## Configuração do ambiente

1. Clone o repositório:

```bash
git clone <url-do-repositorio>
cd shopping-cart-api
```

2. Crie um arquivo `.env` na raiz do projeto com a variável de conexão ao banco:

```env
DATABASE_URL=postgresql://usuario:senha@host/banco
```

> O arquivo `.env` nunca deve ser commitado. Ele já está no `.gitignore`.

---

## Executando com Docker (recomendado)

O container já aplica as migrations automaticamente ao iniciar.

### Subir o ambiente

```bash
make docker-up
```

### Subir reconstruindo a imagem

```bash
make docker-build && make docker-up
```

### Parar o ambiente

```bash
make docker-down
```

### Ver logs do backend

```bash
make docker-logs
```

### Abrir terminal dentro do container

```bash
make docker-shell
```

---

## Executando localmente (sem Docker)

1. Instale as dependências:

```bash
pip install -r requirements.txt
```

2. Aplique as migrations:

```bash
make upgrade
```

3. Suba o servidor:

```bash
make run
```

---

## Banco de dados (Alembic)

| Comando | O que faz |
|---|---|
| `make migrate msg="descrição"` | Gera nova migration com autogenerate |
| `make upgrade` | Aplica todas as migrations pendentes |
| `make downgrade` | Reverte a última migration |
| `make history` | Lista o histórico de migrations |

---

## Testes

Os testes de integração rodam contra a branch **staging** do NeonDB.

### Configuração

Adicione ao `.env` a URL da branch staging:

```env
STAGING_DATABASE_URL=postgresql://...branch-staging...
```

O `conftest.py` usa a seguinte ordem de prioridade para o banco de testes:

```
STAGING_DATABASE_URL → TEST_DATABASE_URL → DATABASE_URL
```

### Rodando os testes

```bash
make test           # todos os testes com output verboso
make test-cov       # com relatório de cobertura por módulo
```

> As tabelas nunca são dropadas após os testes. O banco staging é persistente —
> apenas os dados inseridos durante os testes são removidos ao final de cada um.

---

## Endpoints

A API estará disponível em `http://localhost:8000`.

Documentação interativa (Swagger): `http://localhost:8000/docs`

| Prefixo | Recurso |
|---|---|
| `/users` | Usuários |
| `/categories` | Categorias |
| `/products` | Produtos |
| `/cart` | Carrinho |
| `/orders` | Pedidos e checkout |
| `/payments` | Pagamentos |
