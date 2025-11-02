import pandas as pd

def load_and_clean_data(path="data/online_retail_cleaned_dataset.csv"):
    """
    Load and clean the retail dataset.
    - Removes missing descriptions
    - Deduplicates products
    - Cleans and normalizes text
    """
    df = pd.read_csv(path)
    print(f"📦 Loaded dataset with {len(df)} rows")

    # Drop rows without description
    df.dropna(subset=["Description"], inplace=True)

    # Remove duplicates
    df.drop_duplicates(subset=["StockCode", "Description"], inplace=True)

    # Clean description text
    df["Description"] = df["Description"].str.strip().str.lower()

    print(f"✅ Cleaned dataset: {len(df)} rows remaining")
    return df

if __name__ == "__main__":
    df = load_and_clean_data()
    print(df.head())
