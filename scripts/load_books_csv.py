import sys
import os
import argparse

sys.path.append(os.path.dirname(os.path.dirname(__file__)))

import pandas as pd
from app import app, db, Book

CSV_PATH = "data/books.csv"

def load_books(truncate: bool):
    df = pd.read_csv(CSV_PATH)

    inserted = 0
    skipped = 0

    with app.app_context():
        if truncate:
            db.session.query(Book).delete()
            db.session.commit()

        for _, row in df.iterrows():
            title = str(row["title"]).strip()
            category = str(row.get("category", "")).strip()
            price = float(row["price"])

            exists = Book.query.filter_by(
                title=title,
                category=category,
                price=price
            ).first()

            if exists:
                skipped += 1
                continue

            book = Book(
                title=title,
                price=price,
                rating=row.get("rating"),
                availability=row.get("availability"),
                category=category if category else None,
                image_url=row.get("image_url")
            )

            db.session.add(book)
            inserted += 1

        db.session.commit()

    print(f"{inserted} livros inseridos com sucesso!")
    print(f"{skipped} livros ignorados (duplicados).")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--truncate", action="store_true", help="Apaga a tabela books antes de recarregar")
    args = parser.parse_args()
    load_books(truncate=args.truncate)
