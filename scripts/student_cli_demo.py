import argparse
import json
import os
import pickle
import sys

import pandas as pd

try:
    from termcolor import colored
except ImportError:
    def colored(text, color=None, on_color=None, attrs=None):
        return text


MODEL_PATH = os.path.join(
    os.path.dirname(__file__), '..', 'output', 'alternative_model', 'best_model_xgboost.pkl'
)
FEATURE_COLS_PATH = os.path.join(
    os.path.dirname(__file__), '..', 'output', 'alternative_model', 'feature_cols.pkl'
)
THRESHOLD = 0.417958


def parse_args():
    parser = argparse.ArgumentParser(
        description='Student Loan Risk Prediction CLI (normal XGBoost, no hardcoded feature engineering)'
    )
    parser.add_argument('--input-file', type=str, help='JSON file path: {"feature": value, ...}')
    parser.add_argument('--json', type=str, help='Inline JSON payload string')
    parser.add_argument('--stdin-json', action='store_true', help='Read JSON payload from stdin')
    parser.add_argument('--interactive', action='store_true', help='Prompt for each model feature value')
    parser.add_argument('--print-template', action='store_true', help='Print JSON template and exit')
    return parser.parse_args()


def load_artifacts():
    if not (os.path.exists(MODEL_PATH) and os.path.exists(FEATURE_COLS_PATH)):
        print(colored('Error: model artifacts not found.', 'red'))
        sys.exit(1)

    with open(MODEL_PATH, 'rb') as model_file:
        model = pickle.load(model_file)
    with open(FEATURE_COLS_PATH, 'rb') as feature_file:
        feature_cols = pickle.load(feature_file)

    return model, feature_cols


def read_payload_from_file(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        return json.load(file)


def read_payload_from_stdin():
    content = sys.stdin.read().strip()
    if not content:
        raise ValueError('stdin is empty')
    return json.loads(content)


def read_payload_interactive(feature_cols):
    print(colored('Interactive mode: provide values for each feature.', 'green'))
    print(colored('Press ENTER for 0.\n', 'yellow'))
    payload = {}

    for feature_name in feature_cols:
        while True:
            try:
                raw = input(f'{feature_name} [default: 0]: ').strip()
            except (KeyboardInterrupt, EOFError):
                print('\nExiting...')
                sys.exit(0)

            if raw == '':
                payload[feature_name] = 0.0
                break

            try:
                payload[feature_name] = float(raw)
                break
            except ValueError:
                print(colored('  -> Please enter a valid number.', 'yellow'))

    return payload


def get_payload(args, feature_cols):
    if args.print_template:
        print(json.dumps({feature: 0 for feature in feature_cols}, indent=2))
        sys.exit(0)

    selected = [bool(args.input_file), bool(args.json), bool(args.stdin_json), bool(args.interactive)]
    if sum(selected) == 0:
        return read_payload_interactive(feature_cols)
    if sum(selected) > 1:
        raise ValueError('Use exactly one input mode at a time')

    if args.input_file:
        return read_payload_from_file(args.input_file)
    if args.json:
        return json.loads(args.json)
    if args.stdin_json:
        return read_payload_from_stdin()
    return read_payload_interactive(feature_cols)


def build_input_frame(payload, feature_cols):
    if not isinstance(payload, dict):
        raise ValueError('Payload must be a JSON object')

    missing = [feature for feature in feature_cols if feature not in payload]
    if missing:
        preview = missing[:10]
        suffix = ' ...' if len(missing) > 10 else ''
        raise ValueError(f'Missing required features ({len(missing)}): {preview}{suffix}')

    row = {feature: payload[feature] for feature in feature_cols}
    return pd.DataFrame([row])[feature_cols]


def main():
    print(colored('=======================================', 'cyan'))
    print(colored('   Student Loan Risk Prediction CLI    ', 'cyan', attrs=['bold']))
    print(colored('=======================================\n', 'cyan'))

    args = parse_args()
    model, feature_cols = load_artifacts()

    try:
        payload = get_payload(args, feature_cols)
        input_frame = build_input_frame(payload, feature_cols)
    except Exception as error:
        print(colored(f'Input error: {error}', 'red'))
        sys.exit(1)

    print(colored('Analyzing profile...\n', 'cyan'))
    probability = model.predict_proba(input_frame)[0][1]

    print(colored('=======================================', 'cyan'))
    print('Prediction Results:')
    if probability >= THRESHOLD:
        print(colored('Risk Status: HIGH RISK (Likely Default)', 'red', attrs=['bold']))
    else:
        print(colored('Risk Status: LOW RISK (Approved)', 'green', attrs=['bold']))
    print(f'Default Probability: {probability * 100:.1f}%')
    print(colored('=======================================\n', 'cyan'))


if __name__ == '__main__':
    main()
