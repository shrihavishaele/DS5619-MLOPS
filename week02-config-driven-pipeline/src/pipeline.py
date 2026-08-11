"""
The "after" version — YOUR file to complete.

Fill in the three functions marked with # TODO. Everything else (CLI wiring,
imports) is already done for you. Do not hardcode any path, format string, or
threshold value anywhere in this file — if you find yourself typing a literal
number or file path outside of a default/example, it belongs in the config
file instead.

Run with:
    python src/pipeline.py --config config/pipeline.yaml
"""
import argparse
import csv
import json

import yaml

REQUIRED_KEYS = ["input_path", "input_format", "high_value_threshold", "output_path"]


def load_config(path):
    """Load a YAML config file and validate required keys are present.

    Must raise ValueError naming the specific missing key if REQUIRED_KEYS
    are not all present. Do not let this fail with a bare KeyError later.
    """
    # TODO: implement
    with open(path, 'r') as file:
        config = yaml.safe_load(file)
    
    for key in REQUIRED_KEYS:
        if key not in config:
            raise ValueError(f"missing key {key}")
    return config

def load_transactions(path, fmt):
    """Load transactions from `path`, using `fmt` ("csv" or "json") to decide
    how to parse it — not by sniffing the file extension.

    Must return a list of dicts. Every dict must have at least "amount"
    (str or float) and "is_fraud" (str "True"/"False" or bool).
    Raise ValueError for any fmt other than "csv" or "json".
    """
    # TODO: implement
    if fmt not in ["csv", "json"]:
        raise ValueError(f"unsupported format: {fmt}, should be csv or json")
    
    with open(path, 'r') as file:
        if fmt == "csv":
            reader = csv.DictReader(file)
            return list(reader)
        elif fmt == "json":
            return json.load(file)


def run_pipeline(config):
    """Load data per `config`, compute the same summary fields as
    pipeline_hardcoded.py (n_transactions, total_amount, fraud_rate,
    n_high_value, high_value_threshold), and write them as JSON to
    config["output_path"]. Return the report dict as well.
    """
    # TODO: implement
    transactions = load_transactions(config["input_path"], config["input_format"])
    
    n_transactions = len(transactions)
    total_amount = 0.0
    n_fraud = 0
    n_high_value = 0
    
    threshold = float(config["high_value_threshold"])
    
    for txn in transactions:
        amount = float(txn["amount"])
        is_fraud_val = txn["is_fraud"]
        if isinstance(is_fraud_val, str):
            is_fraud = is_fraud_val.strip().lower() == "true"
        else:
            is_fraud = bool(is_fraud_val)
            
        total_amount += amount
        
        if is_fraud:
            n_fraud += 1
            
        if amount >= threshold:
            n_high_value += 1
            
    fraud_rate = (n_fraud / n_transactions) if n_transactions > 0 else 0.0
    
    report = {
        "n_transactions": n_transactions,
        "total_amount": total_amount,
        "fraud_rate": fraud_rate,
        "n_high_value": n_high_value,
        "high_value_threshold": threshold
    }
    
    with open(config["output_path"], 'w') as out_file:
        json.dump(report, out_file, indent=4)
        
    return report



def main():
    parser = argparse.ArgumentParser(description="Config-driven fraud transaction summary pipeline")
    parser.add_argument("--config", required=True, help="Path to a YAML config file")
    args = parser.parse_args()

    config = load_config(args.config)
    report = run_pipeline(config)
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
