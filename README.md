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

---

## Configuração do ambiente

1. Clone o repositório:

```bash
git clone <url-do-repositorio>
cd shopping-cart-api
```

2. Instale as dependências:

```bash
pip install -r requirements.txt
```

3. Crie um arquivo `.env` na raiz do projeto com a variável de conexão ao banco:

```env
DATABASE_URL=postgresql://usuario:senha@host/banco
```

---

## Banco de dados

Os comandos abaixo utilizam o `Makefile` para simplificar o uso do Alembic.

### Gerar uma nova migration

```bash
make migrate msg="descrição da migration"
```

> O Alembic compara os models com o estado atual do banco e gera o arquivo de migration automaticamente.

### Aplicar migrations pendentes

```bash
make upgrade
```

### Reverter a última migration

```bash
make downgrade
```

### Ver histórico de migrations

```bash
make history
```

---

## Executando o servidor

```bash
make run
```

A API estará disponível em `http://localhost:8000`.

Documentação interativa (Swagger): `http://localhost:8000/docs`

---

## Docker

Quando a configuração Docker estiver disponível, a execução será via:

```bash
docker compose up --build
```
