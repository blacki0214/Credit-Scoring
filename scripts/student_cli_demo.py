import os
import pickle
import sys
from datetime import datetime

import pandas as pd

try:
    from termcolor import colored
except ImportError:
    def colored(text, color=None, on_color=None, attrs=None):
        return text


BASE_DIR = os.path.join(os.path.dirname(__file__), "..")
ARTIFACT_DIR = os.path.join(BASE_DIR, "output", "alternative_model")
MODEL_PATH = os.path.join(ARTIFACT_DIR, "best_model_xgboost.pkl")
FEATURE_COLS_PATH = os.path.join(ARTIFACT_DIR, "feature_cols.pkl")
X_TRAIN_PATH = os.path.join(ARTIFACT_DIR, "X_train.csv")
DETAIL_REPORT_PATH = os.path.join(ARTIFACT_DIR, "model_comparison_detailed.csv")
DEFAULT_THRESHOLD = 0.5

FEATURE_ENUMS = {
    "program_level": {0: "college", 1: "university"},
    "living_status": {0: "family", 1: "dorm", 2: "rent"},
    "major_income_potential": {0: "low", 1: "medium", 2: "high"},
}


def print_header() -> None:
    print("=" * 80)
    print("🏦 CREDIT SCORING SYSTEM - XGBoost Model Demo")
    print("=" * 80)
    print(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")


def load_pickle(path: str):
    with open(path, "rb") as file:
        return pickle.load(file)


def load_threshold() -> float:
    if not os.path.exists(DETAIL_REPORT_PATH):
        return DEFAULT_THRESHOLD

    try:
        detailed_df = pd.read_csv(DETAIL_REPORT_PATH)
        row = detailed_df[detailed_df["model"] == "normal_xgboost"]
        if row.empty:
            return DEFAULT_THRESHOLD
        return float(row.iloc[0]["best_threshold_f1"])
    except Exception:
        return DEFAULT_THRESHOLD


def load_feature_stats(feature_cols):
    stats = {}
    if not os.path.exists(X_TRAIN_PATH):
        for feature in feature_cols:
            stats[feature] = {
                "min": None,
                "max": None,
                "default": 0.0,
                "is_binary": False,
            }
        return stats

    try:
        x_train = pd.read_csv(X_TRAIN_PATH, usecols=feature_cols)
    except Exception:
        for feature in feature_cols:
            stats[feature] = {
                "min": None,
                "max": None,
                "default": 0.0,
                "is_binary": False,
            }
        return stats

    for feature in feature_cols:
        series = pd.to_numeric(x_train[feature], errors="coerce").dropna()

        if series.empty:
            stats[feature] = {
                "min": None,
                "max": None,
                "default": 0.0,
                "is_binary": False,
            }
            continue

        unique_values = set(series.unique().tolist())
        is_binary = unique_values.issubset({0, 1})

        default_value = float(series.median())
        if is_binary:
            default_value = int(round(series.mode().iloc[0])) if not series.mode().empty else 0

        stats[feature] = {
            "min": float(series.min()),
            "max": float(series.max()),
            "default": default_value,
            "is_binary": is_binary,
        }

    return stats


def build_feature_config(feature_cols, feature_stats):
    config = []
    for feature in feature_cols:
        info = feature_stats.get(feature, {})
        label = feature.replace("_", " ").replace("-", " ").title()
        low = info.get("min")
        high = info.get("max")
        default = info.get("default", 0.0)
        is_binary = bool(info.get("is_binary", False))
        choices = FEATURE_ENUMS.get(feature)

        if choices:
            sorted_options = ", ".join([f"{key}={value}" for key, value in choices.items()])
            question = f"Select {label}."
            description = f"Encoded categorical feature. Options: {sorted_options}."
            cast = int
            default = int(round(default)) if default is not None else min(choices.keys())
            low = min(choices.keys())
            high = max(choices.keys())
            is_binary = False
        elif is_binary:
            question = f"Is {label} true?"
            description = f"Binary feature. Enter 1 for YES, 0 for NO. Typical range in training data: 0 to 1."
            cast = int
        else:
            question = f"Enter value for {label}."
            if low is None or high is None:
                description = "Numeric feature. No training range available."
            else:
                description = f"Numeric feature. Typical training range: {low:.4f} to {high:.4f}."
            cast = float

        config.append(
            {
                "field": feature,
                "label": label,
                "question": question,
                "description": description,
                "range": (low, high),
                "default": default,
                "cast": cast,
                "is_binary": is_binary,
                "choices": choices,
            }
        )

    return config


def ask_value(cfg: dict):
    cast = cfg.get("cast", float)
    low, high = cfg.get("range", (None, None))
    default = cfg.get("default")
    is_binary = cfg.get("is_binary", False)
    choices = cfg.get("choices")

    print("\n" + "─" * 60)
    print(f"{cfg['label']}")
    print(f"❓ {cfg['question']}")

    prompt = "Enter"
    if choices:
        option_text = ", ".join([f"{key}={value}" for key, value in choices.items()])
        prompt += f" option ({option_text})"
    elif is_binary:
        prompt += " (1=YES, 0=NO)"
    elif low is not None and high is not None:
        prompt += f" value (range: {low:.4f} to {high:.4f})"
    else:
        prompt += " value"

    if default is not None:
        prompt += f" [default: {default}]"

    prompt += "\n💡 Type '?' for more info, or press Enter for default: "

    while True:
        try:
            raw = input(prompt).strip()
        except (KeyboardInterrupt, EOFError):
            print("\nExiting...")
            sys.exit(0)

        if raw == "?":
            print("\nHelp:")
            print(f"   {cfg['description']}")
            continue

        if raw == "":
            if default is None:
                print("❌ This field is required. Please enter a value or type '?' for help.")
                continue
            value = default
        else:
            try:
                value = cast(raw.replace(",", "").replace("$", ""))
            except ValueError:
                print("❌ Invalid input. Please enter a valid number.")
                continue

        if low is not None and value < low:
            print(f"❌ Value too low. Minimum is {low:.4f}.")
            continue
        if high is not None and value > high:
            print(f"❌ Value too high. Maximum is {high:.4f}.")
            continue
        if choices and int(value) not in choices:
            valid_options = ", ".join([str(key) for key in choices.keys()])
            print(f"❌ Invalid option. Choose one of: {valid_options}")
            continue

        if choices:
            display_value = f"{int(value)} ({choices[int(value)]})"
        elif is_binary:
            display_value = "YES" if int(value) == 1 else "NO"
        else:
            display_value = value
        print(f"✅ Confirmed: {display_value}")
        return value


def collect_values(feature_config):
    print("\n" + "=" * 80)
    print("CUSTOMER INFORMATION FORM")
    print("=" * 80)
    print("\nTips:")
    print("  • Press Enter to use default values")
    print("  • Type '?' at any question to see explanation")
    print("  • Each prompt shows training-data range")
    print("\nLet's start!\n")

    values = {}
    for cfg in feature_config:
        values[cfg["field"]] = ask_value(cfg)

    print("\n" + "=" * 80)
    print("All information collected!")
    print("=" * 80)
    return values


def predict_and_print(model, sample, threshold, feature_cols, values):
    probability = float(model.predict_proba(sample)[0][1])
    is_risky = probability >= threshold

    if probability < 0.3:
        risk_level = "VERY LOW"
        risk_emoji = "🟢"
    elif probability < 0.5:
        risk_level = "LOW"
        risk_emoji = "🟡"
    elif probability < 0.7:
        risk_level = "MEDIUM"
        risk_emoji = "🟠"
    elif probability < threshold:
        risk_level = "HIGH"
        risk_emoji = "🔴"
    else:
        risk_level = "CRITICAL"
        risk_emoji = "🚨"

    print("\n" + "=" * 80)
    print("🎯 PREDICTION RESULTS")
    print("=" * 80)
    print(f"\n{risk_emoji} Default Probability: {probability:.1%}")
    print(f"{risk_emoji} Risk Level: {risk_level}")
    print(f"🎚️  Decision Threshold: {threshold:.1%}")

    print("\n" + "─" * 80)
    print("📋 FINAL DECISION")
    print("─" * 80)

    if is_risky:
        print("\n❌ REJECT APPLICATION")
        print("\n⚠️  Reasons:")
        print(f"   • Default probability ({probability:.1%}) exceeds threshold ({threshold:.1%})")
        print(f"   • Risk level: {risk_level}")
    else:
        print("\n✅ APPROVE APPLICATION")
        print("\n🎉 This customer shows low default risk.")

    print("\n" + "=" * 80)
    print("📊 MODEL INFORMATION")
    print("=" * 80)
    print("Model: XGBoost Classifier (best_model_xgboost.pkl)")
    print(f"Features used: {len(feature_cols)}")
    print(f"Threshold: {threshold:.6f}")
    print("=" * 80 + "\n")

    if hasattr(model, "feature_importances_"):
        print("TOP 10 FACTORS INFLUENCING THIS DECISION:")
        print("─" * 60)
        importance_df = pd.DataFrame(
            {
                "feature": feature_cols,
                "importance": model.feature_importances_,
            }
        ).sort_values("importance", ascending=False)

        for index, row in enumerate(importance_df.head(10).itertuples(index=False), start=1):
            feature = row.feature
            imp = row.importance
            value = values.get(feature, 0.0)
            print(f"{index}. {feature}")
            print(f"   Importance: {imp:.4f} | Your value: {value:.4f}")


def main():
    print_header()

    if not os.path.exists(MODEL_PATH):
        print(colored(f"Error: missing model file: {MODEL_PATH}", "red"))
        sys.exit(1)
    if not os.path.exists(FEATURE_COLS_PATH):
        print(colored(f"Error: missing feature list: {FEATURE_COLS_PATH}", "red"))
        sys.exit(1)

    model = load_pickle(MODEL_PATH)
    feature_cols = load_pickle(FEATURE_COLS_PATH)
    threshold = load_threshold()

    feature_stats = load_feature_stats(feature_cols)
    feature_config = build_feature_config(feature_cols, feature_stats)

    values = collect_values(feature_config)
    sample = pd.DataFrame([values], columns=feature_cols).fillna(0.0)

    predict_and_print(model, sample, threshold, feature_cols, values)


if __name__ == "__main__":
    main()
