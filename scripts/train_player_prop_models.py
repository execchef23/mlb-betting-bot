import pandas as pd
from xgboost import XGBClassifier
import joblib
import os

ENGINEERED_PATH = "data/engineered"

def train_hits_model():
    path = f"{ENGINEERED_PATH}/player_hits_features_2024.csv"
    if not os.path.exists(path):
        print(f"❌ Hits training data not found: {path}")
        return

    df = pd.read_csv(path).dropna()
    features = ["rolling_avg_hits_5", "rolling_avg_hits_10", "rolling_hits_sum_5"]
    target = "hit"

    if target not in df.columns:
        print("❌ 'hit' column not found in hits data.")
        return

    X = df[features]
    y = df[target]

    model = XGBClassifier(
        n_estimators=100,
        max_depth=3,
        learning_rate=0.1,
        use_label_encoder=False,
        eval_metric="logloss"
    )
    model.fit(X, y)

    joblib.dump(model, "models/player_hits_model.pkl")
    print("✅ Saved player_hits_model.pkl")


def train_strikeouts_model():
    path = f"{ENGINEERED_PATH}/player_strikeout_features_2024.csv"
    if not os.path.exists(path):
        print(f"❌ Strikeouts training data not found: {path}")
        return

    df = pd.read_csv(path).dropna()

    # ✅ DEBUG OUTPUT
    print("📊 Columns in dataset:", df.columns.tolist())
    print("\n🔍 First 5 rows:")
    print(df.head())

    # ✅ STOP here — don’t train
    return


if __name__ == "__main__":
    os.makedirs("models", exist_ok=True)
    train_hits_model()
    train_strikeouts_model()