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
    df = pd.read_csv(RAW_PATH)

    # convert price string -> float column price_gbp
    df["price_gbp"] = df["price"].apply(clean_price)

    # convert rating word -> int column rating
    df["rating"] = df["star_rating"].apply(clean_rating)

    # convert availability text -> boolean column in_stock
    df["in_stock"] = df["availability"].apply(clean_availability)

    # count how many rows failed to parse before fixing them, just for the log
    bad_price_count = df["price_gbp"].isna().sum()
    bad_rating_count = df["rating"].isna().sum()
    print(f"Rows with unparsable price: {bad_price_count}")
    print(f"Rows with unparsable rating: {bad_rating_count}")

    # median imputation for numeric fields that failed to parse
    # chose median over mean since price/rating can be skewed by outliers,
    # and median over dropping rows since we don't want to lose scraped data
    # for a handful of bad values
    if bad_price_count > 0:
        median_price = df["price_gbp"].median()
        df["price_gbp"] = df["price_gbp"].fillna(median_price)

    if bad_rating_count > 0:
        median_rating = df["rating"].median()
        df["rating"] = df["rating"].fillna(median_rating).astype(int)
    else:
        df["rating"] = df["rating"].astype(int)

    # in_stock has no numeric fallback, so any unparsable row here is dropped
    # instead of guessed at, since guessing true/false could bias analytics later
    before_drop = len(df)
    df = df.dropna(subset=["in_stock"])
    dropped = before_drop - len(df)
    if dropped > 0:
        print(f"Dropped {dropped} rows with missing availability")

    # keep only the columns we need going forward
    df = df[["title", "price_gbp", "rating", "in_stock", "category"]]

    os.makedirs(os.path.dirname(CLEAN_PATH), exist_ok=True)
    df.to_csv(CLEAN_PATH, index=False)

    print(f"Cleaned {len(df)} rows")
    print(f"Saved to {CLEAN_PATH}")


if __name__ == "__main__":
    main()