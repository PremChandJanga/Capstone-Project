import pandas as pd
import sqlite3
import os

DB_PATH = os.path.join("data_pipeline", "db", "books.db")


def run_query(conn, title, query):
    print("=" * 60)
    print(title)
    print("=" * 60)
    print("SQL:")
    print(query.strip())
    print()
    result = pd.read_sql(query, conn)
    print("Output:")
    print(result)
    print()
    return result


def main():
    conn = sqlite3.connect(DB_PATH)

    # Query 1: SELECT / WHERE - books that are in stock and priced above 2000 INR
    q1 = """
        SELECT title, price_inr, in_stock
        FROM books
        WHERE in_stock = 1 AND price_inr > 2000
    """
    run_query(conn, "Query 1: SELECT / WHERE - in-stock books over 2000 INR", q1)

    # Query 2: ORDER BY / LIMIT - top 10 most expensive books overall
    q2 = """
        SELECT title, price_inr
        FROM books
        ORDER BY price_inr DESC
        LIMIT 10
    """
    run_query(conn, "Query 2: ORDER BY / LIMIT - top 10 most expensive books", q2)

    # Query 3: DISTINCT - list all category names present in the data
    q3 = """
        SELECT DISTINCT category_name
        FROM categories
    """
    run_query(conn, "Query 3: DISTINCT - all category names", q3)

    # Query 4: WHERE with BETWEEN - books rated between 3 and 5 stars
    q4 = """
        SELECT title, rating
        FROM books
        WHERE rating BETWEEN 3 AND 5
        ORDER BY rating DESC
    """
    run_query(conn, "Query 4: WHERE BETWEEN - books rated 3 to 5 stars", q4)

    # Query 5: JOIN - top 10 highest-rated books per category, using JOIN + ORDER BY + LIMIT
    # this single query also satisfies the JOIN requirement
    q5 = """
        SELECT categories.category_name, books.title, books.rating, books.price_inr
        FROM books
        JOIN categories ON books.category_id = categories.category_id
        WHERE categories.category_name = 'Romance'
        ORDER BY books.rating DESC, books.book_id ASC
        LIMIT 10
    """
    join_result_sql = run_query(conn, "Query 5: JOIN - top 10 highest-rated Romance books", q5)

    print("=" * 60)
    print("Comparing pd.read_sql (above) vs pd.merge (in-memory)")
    print("=" * 60)
    # read both full tables into memory, then reproduce the join with pandas
    # instead of SQL, to prove both approaches give the same result
    books_df = pd.read_sql("SELECT * FROM books", conn)
    categories_df = pd.read_sql("SELECT * FROM categories", conn)

    merged_df = pd.merge(books_df, categories_df, on="category_id")
    join_result_pandas = (
        merged_df[merged_df["category_name"] == "Romance"]
        .sort_values(["rating", "book_id"], ascending=[False, True])
        .head(10)[["category_name", "title", "rating", "price_inr"]]
    )

    print("pd.merge output:")
    print(join_result_pandas.reset_index(drop=True))

    print()
    print("Do SQL JOIN and pd.merge outputs match?",
          join_result_sql.reset_index(drop=True)[["title", "rating", "price_inr"]].equals(
              join_result_pandas.reset_index(drop=True)[["title", "rating", "price_inr"]]
          ))

    print()
    print("=" * 60)
    print("Task check: at least 2 queries read back via pd.read_sql")
    print("=" * 60)
    # every query above (q1-q5) was already read into a DataFrame using
    # pd.read_sql inside run_query() - confirming two of them explicitly here
    df_query1 = pd.read_sql(q1, conn)
    df_query4 = pd.read_sql(q4, conn)
    print(f"Query 1 read via pd.read_sql -> DataFrame with shape {df_query1.shape}")
    print(f"Query 4 read via pd.read_sql -> DataFrame with shape {df_query4.shape}")
    print("(All 5 queries above were also read this way inside run_query().)")

    conn.close()


if __name__ == "__main__":
    main()