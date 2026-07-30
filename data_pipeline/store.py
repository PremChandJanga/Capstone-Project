import pandas as pd
import sqlite3
import os

CONVERTED_PATH = os.path.join("data_pipeline", "data", "processed", "books_converted.csv")
DB_PATH = os.path.join("data_pipeline", "db", "books.db")


def main():
    print("=" * 50)
    print("STEP 1: Load converted data")
    print("=" * 50)
    df = pd.read_csv(CONVERTED_PATH)
    print(f"Loaded {len(df)} rows from {CONVERTED_PATH}")

    print()
    print("=" * 50)
    print("STEP 2: Connect to SQLite database")
    print("=" * 50)
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    print(f"Connected to {DB_PATH}")

    print()
    print("=" * 50)
    print("STEP 3: Create normalized schema (categories + books)")
    print("=" * 50)
    # drop tables first so this script can be re-run cleanly without duplicate data
    cursor.execute("DROP TABLE IF EXISTS books")
    cursor.execute("DROP TABLE IF EXISTS categories")

    cursor.execute("""
        CREATE TABLE categories (
            category_id INTEGER PRIMARY KEY,
            category_name TEXT UNIQUE
        )
    """)

    cursor.execute("""
        CREATE TABLE books (
            book_id INTEGER PRIMARY KEY,
            title TEXT,
            price_gbp REAL,
            price_inr REAL,
            rating INTEGER,
            in_stock INTEGER,
            category_id INTEGER REFERENCES categories(category_id)
        )
    """)
    print("Created tables: categories, books (linked by category_id)")

    print()
    print("=" * 50)
    print("STEP 4: Insert categories")
    print("=" * 50)
    # one row per unique category found in the data - this is the whole point
    # of normalizing: category name is stored once here, not repeated in every book row
    unique_categories = df["category"].unique()
    category_id_map = {}

    for i, name in enumerate(unique_categories, start=1):
        cursor.execute(
            "INSERT INTO categories (category_id, category_name) VALUES (?, ?)",
            (i, name)
        )
        category_id_map[name] = i

    print(f"Inserted {len(unique_categories)} categories: {list(unique_categories)}")

    print()
    print("=" * 50)
    print("STEP 5: Insert books")
    print("=" * 50)
    for i, row in df.iterrows():
        cursor.execute("""
            INSERT INTO books (book_id, title, price_gbp, price_inr, rating, in_stock, category_id)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            i + 1,
            row["title"],
            row["price_gbp"],
            row["price_inr"],
            int(row["rating"]),
            int(bool(row["in_stock"])),
            category_id_map[row["category"]]
        ))

    print(f"Inserted {len(df)} books")

    print()
    print("=" * 50)
    print("STEP 6: Create per-category views (for easy visualization only)")
    print("=" * 50)
    # views are NOT separate physical tables - they're saved queries that
    # always reflect the current books table, so the schema stays normalized
    # while still giving an easy way to look at one category at a time
    for name in unique_categories:
        view_name = "view_" + name.lower().replace(" ", "_")
        cursor.execute(f"DROP VIEW IF EXISTS {view_name}")
        cursor.execute(f"""
            CREATE VIEW {view_name} AS
            SELECT books.book_id, books.title, books.price_gbp, books.price_inr,
                   books.rating, books.in_stock
            FROM books
            JOIN categories ON books.category_id = categories.category_id
            WHERE categories.category_name = '{name}'
        """)
        print(f"Created view: {view_name}")

    print()
    print("=" * 50)
    print("STEP 7: Commit and close")
    print("=" * 50)
    conn.commit()
    conn.close()
    print(f"Database saved to {DB_PATH}")


if __name__ == "__main__":
    main()