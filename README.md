<<<<<<< HEAD
# tech-challenge-fase1
=======
# 📚 Tech Challenge — API Pública de Livros

Este projeto faz parte do **Tech Challenge – Fase 1** da Pós Tech.  
O objetivo é construir uma **infraestrutura completa de dados** para um sistema de recomendação de livros, contemplando **extração, processamento, armazenamento e disponibilização via API pública**, com foco em **Machine Learning**.

---

## 🎯 Objetivo do Projeto

Criar um pipeline de dados que:

1. Extraia dados do site https://books.toscrape.com  
2. Armazene os dados localmente (CSV + SQLite)  
3. Disponibilize os dados via API REST pública  
4. Seja escalável e reutilizável para cientistas de dados e modelos de ML  

---

## 🏗️ Arquitetura do Projeto (Pipeline)

```
Web Scraping
↓
CSV (data/books.csv)
↓
SQLite + Alembic (migrations)
↓
API Flask + Swagger + JWT
↓
Consumo:
• Cientistas de Dados
• Modelos de Machine Learning
• Dashboard (Streamlit)
```

---

## 🧰 Tecnologias Utilizadas

- **Scraping:** BeautifulSoup + Requests  
- **Persistência:** SQLite + SQLAlchemy + Alembic  
- **API:** Flask + JWT + Swagger (Flasgger)  
- **ML Ready:** Endpoints de features e training data  
- **Monitoramento:** Logs estruturados  
- **Visualização:** Streamlit  

---

## 📂 Estrutura do Repositório

```
.
├── app.py
├── config.py
├── requirements.txt
├── alembic.ini
├── migrations/
│   ├── env.py
│   └── versions/
├── scripts/
│   ├── scrape_books.py
│   └── load_books_csv.py
├── data/
│   └── books.csv
└── dashboard/
    └── streamlit_app.py
```

---

## ⚙️ Instalação e Configuração (Windows)

### 1️⃣ Criar ambiente virtual

```bash
python -m venv venv
```

### 2️⃣ Ativar o ambiente virtual

```bash
venv\Scripts\activate
```

✅ Se der certo, o PowerShell vai ficar assim:

```
(venv) PS C:\...
```

### 3️⃣ Instalar dependências

```bash
pip install -r requirements.txt
```

⚠️ **Se aparecer erro dizendo que não achou o requirements.txt**, você criou ele no lugar errado.  
O arquivo **requirements.txt precisa ficar na raiz do projeto**, no mesmo nível do `app.py`.

---

## ▶️ Como Executar o Projeto (Passo a Passo)

### 1️⃣ Rodar o Web Scraping (gera o CSV)

```bash
python scripts\scrape_books.py
```

📄 Arquivo gerado:

```
data/books.csv
```

✅ O site possui **1000 livros** (50 páginas x 20 livros).  
O CSV deve ter **1000 linhas**.

---

### 2️⃣ Criar tabelas no banco (SQLite)

```bash
python app.py
```

⚠️ O Flask vai iniciar e travar o terminal (isso é normal).  
Para parar e continuar os próximos passos, aperte:

```
CTRL + C
```

---

### 3️⃣ Popular o banco com o CSV

```bash
python scripts\load_books_csv.py
```

✅ Saída esperada (exemplo):

```
999 livros inseridos com sucesso!
1 livros ignorados (duplicados).
```

---

### 4️⃣ Rodar a API

```bash
python app.py
```

✅ A API ficará disponível em:

- API: http://127.0.0.1:5000  
- Swagger: http://127.0.0.1:5000/apidocs  

---

## ✅ Endpoints Obrigatórios (Core)

### GET /api/v1/books
Lista todos os livros disponíveis.

Exemplo (cURL):
```bash
curl http://127.0.0.1:5000/api/v1/books
```

Exemplo de resposta:
```json
[
  {
    "id": 1,
    "title": "A Light in the Attic",
    "price": 51.77,
    "rating": "Three",
    "availability": "In stock",
    "category": "Poetry",
    "image_url": "https://books.toscrape.com/media/cache/xx.jpg"
  }
]
```

---

### GET /api/v1/books/{id}
Retorna um livro específico pelo ID.

Exemplo:
```bash
curl http://127.0.0.1:5000/api/v1/books/1
```

Resposta:
```json
{
  "id": 1,
  "title": "A Light in the Attic",
  "price": 51.77,
  "rating": "Three",
  "availability": "In stock",
  "category": "Poetry",
  "image_url": "https://books.toscrape.com/media/cache/xx.jpg"
}
```

---

### GET /api/v1/books/search?title=&category=
Busca por título e/ou categoria.

Exemplo:
```bash
curl "http://127.0.0.1:5000/api/v1/books/search?title=light&category=Poetry"
```

---

### GET /api/v1/categories
Lista todas as categorias disponíveis.

Exemplo:
```bash
curl http://127.0.0.1:5000/api/v1/categories
```

Resposta:
```json
[
  "Poetry",
  "Mystery",
  "Travel"
]
```

---

### GET /api/v1/health
Status da API.

Exemplo:
```bash
curl http://127.0.0.1:5000/api/v1/health
```

Resposta:
```json
{
  "status": "ok"
}
```

---

## ⭐ Endpoints Opcionais (Insights)

### GET /api/v1/stats/overview
Estatísticas gerais da coleção (total, preço médio, distribuição de ratings)

### GET /api/v1/stats/categories
Estatísticas por categoria

### GET /api/v1/books/top-rated
Lista livros com melhor avaliação

### GET /api/v1/books/price-range?min=&max=
Filtra por faixa de preço

---

## 🔐 Desafio 1 — Autenticação JWT (Bônus)

### POST /api/v1/auth/login
Obtém token JWT.

Exemplo:
```bash
curl -X POST http://127.0.0.1:5000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d "{\"username\":\"admin\",\"password\":\"123\"}"
```

Resposta:
```json
{
  "access_token": "SEU_TOKEN_AQUI"
}
```

### POST /api/v1/auth/refresh
Renova token JWT.

---

## 🤖 Desafio 2 — Pipeline ML-Ready (Bônus)

### GET /api/v1/ml/features
Retorna features limpas para ML.

### GET /api/v1/ml/training-data
Retorna dataset pronto para treino.

### POST /api/v1/ml/predictions
Endpoint para receber predições feitas pelo modelo.

---

## 📊 Desafio 3 — Dashboard (Streamlit)

Rodar o dashboard:

```bash
streamlit run dashboard\streamlit_app.py
```

✅ O Streamlit vai abrir um link no navegador.  
Se aparecer a pergunta sobre rede pública/privada, escolha **Public** para compartilhar com avaliador.

---

## 🚀 Deploy Público

Cole aqui o link do deploy:

```
COLE_AQUI_O_LINK_DO_RENDER
```

---

## 🎥 Vídeo de Apresentação

Cole aqui o link do vídeo:

```
COLE_AQUI_O_LINK_DO_VIDEO
```
>>>>>>> c7a9978 (Initial commit - Tech Challenge API de livros)
