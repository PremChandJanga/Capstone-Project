import pandas as pd
import os

CLEAN_PATH = os.path.join("data_pipeline", "data", "processed", "books_clean.csv")
CONVERTED_PATH = os.path.join("data_pipeline", "data", "processed", "books_converted.csv")

# fixed baseline rate for this project - not a live market rate, just a
# constant defined by the assignment, so no API/lookup needed for this
GBP_TO_INR_RATE = 105.50


def main():
    print("=" * 50)
    print("STEP 1: Load cleaned data")
    print("=" * 50)
    df = pd.read_csv(CLEAN_PATH)
    print(f"Loaded {len(df)} rows from {CLEAN_PATH}")

    print()
    print("=" * 50)
    print(f"STEP 2: Convert price_gbp -> price_inr (rate = {GBP_TO_INR_RATE})")
    print("=" * 50)
    df["price_inr"] = df["price_gbp"] * GBP_TO_INR_RATE
    df["price_inr"] = df["price_inr"].round(2)
    print(f"Converted {len(df)} rows using fixed rate 1 GBP = {GBP_TO_INR_RATE} INR")
    print(df[["price_gbp", "price_inr"]].head())

    print()
    print("=" * 50)
    print("STEP 3: Save converted data")
    print("=" * 50)
    df.to_csv(CONVERTED_PATH, index=False)
    print(f"Saved to {CONVERTED_PATH}")


if __name__ == "__main__":
    main()