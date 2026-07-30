import pandas as pd
import os

RAW_PATH = os.path.join("data_pipeline", "data", "raw", "books_raw.csv")
CLEAN_PATH = os.path.join("data_pipeline", "data", "processed", "books_clean.csv")

RATING_MAP = {"One": 1, "Two": 2, "Three": 3, "Four": 4, "Five": 5}


def clean_price(price):
    # prices come in as "£51.77" - strip the currency symbol and convert to float
    try:
        return float(price.replace("£", "").strip())
    except (ValueError, AttributeError):
        return None  # unparsable price, handled later with median imputation


def clean_rating(rating):
    # rating comes in as a word like "Three" - map it to an int 1-5
    return RATING_MAP.get(rating, None)  # None if it's an unexpected value


def clean_availability(availability):
    # availability text looks like "In stock (22 available)" or "Out of stock"
    if availability is None:
        return None
    return "in stock" in availability.lower()


def main():
    print("=" * 50)
    print("STEP 1: Load raw data")
    print("=" * 50)
    # must match the utf-8 encoding scrape.py used to write this file,
    # otherwise the £ symbol gets garbled and price parsing fails silently
    df = pd.read_csv(RAW_PATH, encoding="utf-8")
    print(f"Loaded {len(df)} raw rows from {RAW_PATH}")

    print()
    print("=" * 50)
    print("STEP 2: Convert price -> price_gbp (float)")
    print("=" * 50)
    df["price_gbp"] = df["price"].apply(clean_price)
    bad_price_count = df["price_gbp"].isna().sum()
    print(f"Converted price column. Unparsable rows: {bad_price_count}")

    print()
    print("=" * 50)
    print("STEP 3: Convert star_rating -> rating (int 1-5)")
    print("=" * 50)
    df["rating"] = df["star_rating"].apply(clean_rating)
    bad_rating_count = df["rating"].isna().sum()
    print(f"Converted rating column. Unparsable rows: {bad_rating_count}")

    print()
    print("=" * 50)
    print("STEP 4: Convert availability -> in_stock (bool)")
    print("=" * 50)
    df["in_stock"] = df["availability"].apply(clean_availability)
    bad_stock_count = df["in_stock"].isna().sum()
    print(f"Converted in_stock column. Unparsable rows: {bad_stock_count}")

    print()
    print("=" * 50)
    print("STEP 5: Handle missing/unparsable values")
    print("=" * 50)
    # median imputation for numeric fields that failed to parse
    # chose median over mean since price/rating can be skewed by outliers,
    # and median over dropping rows since we don't want to lose scraped data
    # for a handful of bad values
    if bad_price_count > 0:
        median_price = df["price_gbp"].median()
        df["price_gbp"] = df["price_gbp"].fillna(median_price)
        print(f"Filled {bad_price_count} missing price_gbp values with median: {median_price}")
    else:
        print("No missing price_gbp values to fill")

    if bad_rating_count > 0:
        median_rating = df["rating"].median()
        df["rating"] = df["rating"].fillna(median_rating).astype(int)
        print(f"Filled {bad_rating_count} missing rating values with median: {median_rating}")
    else:
        df["rating"] = df["rating"].astype(int)
        print("No missing rating values to fill")

    # in_stock has no numeric fallback, so any unparsable row here is dropped
    # instead of guessed at, since guessing true/false could bias analytics later
    before_drop = len(df)
    df = df.dropna(subset=["in_stock"])
    dropped = before_drop - len(df)
    if dropped > 0:
        print(f"Dropped {dropped} rows with missing in_stock value")
    else:
        print("No rows dropped for missing in_stock")

    print()
    print("=" * 50)
    print("STEP 6: Finalize columns and save")
    print("=" * 50)
    df = df[["title", "price_gbp", "rating", "in_stock", "category"]]
    os.makedirs(os.path.dirname(CLEAN_PATH), exist_ok=True)
    df.to_csv(CLEAN_PATH, index=False)
    print(f"Final row count: {len(df)}")
    print(f"Saved cleaned data to {CLEAN_PATH}")


if __name__ == "__main__":
    main()