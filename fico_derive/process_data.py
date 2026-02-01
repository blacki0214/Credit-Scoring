import pandas as pd

def load_datasets(data_dir="../data"):
    """Load raw Home Credit datasets."""
    app = pd.read_csv(f"{data_dir}/application_train.csv")
    bureau = pd.read_csv(f"{data_dir}/bureau.csv")
    install = pd.read_csv(f"{data_dir}/installments_payments.csv")
    try:
        credit = pd.read_csv(f"{data_dir}/credit_card_balance.csv")
    except FileNotFoundError:
        credit = None
        print("credit_card_balance.csv not found — skipping credit card features.")

    print(f"Loaded datasets: app({len(app)}), bureau({len(bureau)}), install({len(install)})")
    return app, bureau, install, credit

if __name__ == "__main__":
    app, bureau, install, credit = load_datasets()
    print(app.head())
    print("Data processing step complete.")

