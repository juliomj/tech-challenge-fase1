import json
import logging
import time
from datetime import datetime

from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import (
    JWTManager,
    create_access_token,
    create_refresh_token,
    jwt_required,
    get_jwt_identity,
)
from flasgger import Swagger

# =====================
# APP SETUP
# =====================

app = Flask(__name__)
app.config.from_object("config")

db = SQLAlchemy(app)
jwt = JWTManager(app)
swagger = Swagger(app)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("books_api")

# =====================
# SIMPLE METRICS + LOGS
# =====================

METRICS = {"requests_total": 0, "by_route": {}, "avg_latency_ms": 0.0}
_LAT_SUM = 0.0

@app.before_request
def _start_timer():
    request._start_time = time.time()

@app.after_request
def _after_request(response):
    global _LAT_SUM
    latency_ms = (time.time() - request._start_time) * 1000.0

    METRICS["requests_total"] += 1
    key = f"{request.method} {request.path}"
    METRICS["by_route"][key] = METRICS["by_route"].get(key, 0) + 1

    _LAT_SUM += latency_ms
    METRICS["avg_latency_ms"] = round(_LAT_SUM / METRICS["requests_total"], 2)

    payload = {
        "ts": datetime.utcnow().isoformat(),
        "method": request.method,
        "path": request.path,
        "status": response.status_code,
        "latency_ms": round(latency_ms, 2),
    }
    logger.info(json.dumps(payload, ensure_ascii=False))
    return response

# =====================
# MODELS
# =====================

class User(db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)

class Book(db.Model):
    __tablename__ = "books"
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    price = db.Column(db.Float, nullable=False)
    rating = db.Column(db.String(20))
    availability = db.Column(db.String(100))
    category = db.Column(db.String(100))
    image_url = db.Column(db.String(255))

def book_to_dict(b: Book):
    return {
        "id": b.id,
        "title": b.title,
        "price": b.price,
        "rating": b.rating,
        "availability": b.availability,
        "category": b.category,
        "image_url": b.image_url,
    }

# =====================
# AUTH (DESAFIO 1)
# =====================

@app.route("/api/v1/auth/register", methods=["POST"])
def auth_register():
    """
    Registra usuário (demo).
    ---
    tags:
      - Auth
    parameters:
      - in: body
        name: body
        required: true
        schema:
          type: object
          required: [username, password]
          properties:
            username: {type: string}
            password: {type: string}
    responses:
      201: {description: User created}
      400: {description: User already exists}
    """
    data = request.get_json(force=True)
    if User.query.filter_by(username=data["username"]).first():
        return jsonify({"error": "User already exists"}), 400

    user = User(username=data["username"], password=data["password"])
    db.session.add(user)
    db.session.commit()
    return jsonify({"message": "User created"}), 201

@app.route("/api/v1/auth/login", methods=["POST"])
def auth_login():
    """
    Login -> retorna access e refresh token.
    ---
    tags:
      - Auth
    parameters:
      - in: body
        name: body
        required: true
        schema:
          type: object
          required: [username, password]
          properties:
            username: {type: string}
            password: {type: string}
    responses:
      200: {description: Tokens}
      401: {description: Invalid credentials}
    """
    data = request.get_json(force=True)
    user = User.query.filter_by(username=data.get("username")).first()
    if not user or user.password != data.get("password"):
        return jsonify({"error": "Invalid credentials"}), 401

    access_token = create_access_token(identity=str(user.id))
    refresh_token = create_refresh_token(identity=str(user.id))
    return jsonify({"access_token": access_token, "refresh_token": refresh_token}), 200

@app.route("/api/v1/auth/refresh", methods=["POST"])
@jwt_required(refresh=True)
def auth_refresh():
    """
    Refresh token -> retorna novo access token.
    ---
    tags:
      - Auth
    responses:
      200: {description: New access token}
      401: {description: Missing/invalid refresh token}
    """
    user_id = get_jwt_identity()
    new_access = create_access_token(identity=user_id)
    return jsonify({"access_token": new_access}), 200

# =====================
# CORE ENDPOINTS (OBRIGATÓRIOS)
# =====================

@app.route("/api/v1/health", methods=["GET"])
def health():
    """
    Healthcheck.
    ---
    tags:
      - Core
    responses:
      200: {description: API OK}
    """
    return jsonify({"status": "ok"}), 200

@app.route("/api/v1/books", methods=["GET"])
def get_books():
    """
    Lista todos os livros.
    ---
    tags:
      - Books
    responses:
      200: {description: List of books}
    """
    books = Book.query.order_by(Book.id.asc()).all()
    return jsonify([book_to_dict(b) for b in books]), 200

@app.route("/api/v1/books/<int:book_id>", methods=["GET"])
def get_book(book_id):
    """
    Detalhes de um livro por ID.
    ---
    tags:
      - Books
    parameters:
      - in: path
        name: book_id
        required: true
        type: integer
    responses:
      200: {description: Book}
      404: {description: Not found}
    """
    b = Book.query.get_or_404(book_id)
    return jsonify(book_to_dict(b)), 200

@app.route("/api/v1/books/search", methods=["GET"])
def search_books():
    """
    Busca por title e/ou category.
    ---
    tags:
      - Books
    parameters:
      - in: query
        name: title
        type: string
        required: false
      - in: query
        name: category
        type: string
        required: false
    responses:
      200: {description: Filtered books}
    """
    title = request.args.get("title")
    category = request.args.get("category")

    query = Book.query
    if title:
        query = query.filter(Book.title.ilike(f"%{title}%"))
    if category:
        query = query.filter(Book.category.ilike(f"%{category}%"))

    books = query.order_by(Book.id.asc()).all()
    return jsonify([book_to_dict(b) for b in books]), 200

@app.route("/api/v1/categories", methods=["GET"])
def get_categories():
    """
    Lista categorias disponíveis.
    ---
    tags:
      - Core
    responses:
      200: {description: Categories list}
    """
    rows = db.session.query(Book.category).distinct().order_by(Book.category.asc()).all()
    cats = [r[0] for r in rows if r[0]]
    return jsonify(cats), 200

# =====================
# INSIGHTS (OPCIONAIS)
# =====================

@app.route("/api/v1/stats/overview", methods=["GET"])
def stats_overview():
    """
    Estatísticas gerais: total, preço médio, distribuição de ratings.
    ---
    tags:
      - Stats
    responses:
      200: {description: Overview stats}
    """
    books = Book.query.all()
    total = len(books)
    avg_price = round(sum(b.price for b in books) / total, 2) if total else 0.0

    rating_dist = {}
    for b in books:
        r = b.rating or "Unknown"
        rating_dist[r] = rating_dist.get(r, 0) + 1

    return jsonify({
        "total_books": total,
        "avg_price": avg_price,
        "rating_distribution": rating_dist
    }), 200

@app.route("/api/v1/stats/categories", methods=["GET"])
def stats_categories():
    """
    Estatísticas por categoria.
    ---
    tags:
      - Stats
    responses:
      200: {description: Categories stats}
    """
    books = Book.query.all()
    by_cat = {}
    for b in books:
        cat = b.category or "Unknown"
        by_cat.setdefault(cat, {"total": 0, "sum_price": 0.0})
        by_cat[cat]["total"] += 1
        by_cat[cat]["sum_price"] += float(b.price)

    result = [{
        "category": c,
        "total_books": v["total"],
        "avg_price": round(v["sum_price"] / v["total"], 2)
    } for c, v in by_cat.items()]
    result.sort(key=lambda x: x["total_books"], reverse=True)

    return jsonify(result), 200

@app.route("/api/v1/books/top-rated", methods=["GET"])
def top_rated():
    """
    Lista livros com melhor avaliação (Five).
    ---
    tags:
      - Books
    parameters:
      - in: query
        name: limit
        type: integer
        required: false
        default: 10
    responses:
      200: {description: Top rated books}
    """
    limit = request.args.get("limit", default=10, type=int)
    books = Book.query.filter(Book.rating == "Five").order_by(Book.price.asc()).limit(limit).all()
    return jsonify([book_to_dict(b) for b in books]), 200

@app.route("/api/v1/books/price-range", methods=["GET"])
def price_range():
    """
    Filtra livros por faixa de preço.
    ---
    tags:
      - Books
    parameters:
      - in: query
        name: min
        type: number
        required: false
      - in: query
        name: max
        type: number
        required: false
    responses:
      200: {description: Books in price range}
    """
    min_p = request.args.get("min", type=float)
    max_p = request.args.get("max", type=float)

    query = Book.query
    if min_p is not None:
        query = query.filter(Book.price >= min_p)
    if max_p is not None:
        query = query.filter(Book.price <= max_p)

    books = query.order_by(Book.price.asc()).all()
    return jsonify([book_to_dict(b) for b in books]), 200

# =====================
# ML-READY (DESAFIO 2)
# =====================

RATING_MAP = {"One": 1, "Two": 2, "Three": 3, "Four": 4, "Five": 5}
CATEGORY_MAP = {}

def encode_category(c):
    if not c:
        return 0
    if c not in CATEGORY_MAP:
        CATEGORY_MAP[c] = len(CATEGORY_MAP) + 1
    return CATEGORY_MAP[c]

def encode_availability(a):
    if not a:
        return 0
    return 1 if "In stock" in a else 0

def encode_rating(r):
    return RATING_MAP.get(r, 0)

@app.route("/api/v1/ml/features", methods=["GET"])
def ml_features():
    """
    Features formatadas para ML.
    ---
    tags:
      - ML
    responses:
      200: {description: Features list}
    """
    books = Book.query.all()
    return jsonify([{
        "book_id": b.id,
        "price": b.price,
        "category_encoded": encode_category(b.category),
        "availability_encoded": encode_availability(b.availability),
        "rating_encoded": encode_rating(b.rating)
    } for b in books]), 200

@app.route("/api/v1/ml/training-data", methods=["GET"])
def ml_training_data():
    """
    Dataset para treinamento.
    ---
    tags:
      - ML
    responses:
      200: {description: Training data}
    """
    books = Book.query.all()
    return jsonify([{
        "id": b.id,
        "title": b.title,
        "price": b.price,
        "category": b.category,
        "category_encoded": encode_category(b.category),
        "availability": b.availability,
        "availability_encoded": encode_availability(b.availability),
        "rating": b.rating,
        "rating_encoded": encode_rating(b.rating)
    } for b in books]), 200

@app.route("/api/v1/ml/predictions", methods=["POST"])
@jwt_required()
def ml_predictions():
    """
    Recebe predições (simulando consumo de um modelo).
    Protegido por JWT (exemplo).
    ---
    tags:
      - ML
    responses:
      200: {description: Prediction received}
      401: {description: Missing/invalid token}
    """
    data = request.get_json(force=True)
    return jsonify({"message": "Prediction received", "data": data}), 200

# =====================
# MONITORAMENTO (DESAFIO 3)
# =====================

@app.route("/api/v1/metrics", methods=["GET"])
def metrics():
    """
    Métricas simples.
    ---
    tags:
      - Monitoring
    responses:
      200: {description: Metrics}
    """
    return jsonify(METRICS), 200

# =====================
# ADMIN PROTECTED (DESAFIO 1)
# =====================

@app.route("/api/v1/scraping/trigger", methods=["POST"])
@jwt_required()
def scraping_trigger():
    """
    Endpoint admin protegido por JWT.
    ---
    tags:
      - Admin
    responses:
      200: {description: Trigger accepted}
      401: {description: Missing/invalid token}
    """
    user_id = get_jwt_identity()
    return jsonify({"message": "Scraping trigger received", "triggered_by_user_id": user_id}), 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
