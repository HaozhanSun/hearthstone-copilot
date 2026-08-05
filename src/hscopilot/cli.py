from __future__ import annotations

import argparse
import json

from .perception.logconfig import write_log_config
from .perception.power import parse_power_log
from .replay.evaluate import evaluate


def main() -> None:
    parser = argparse.ArgumentParser(prog="hscopilot")
    sub = parser.add_subparsers(dest="command", required=True)
    p_snapshot = sub.add_parser("snapshot"); p_snapshot.add_argument("power_log")
    p_eval = sub.add_parser("replay-evaluate"); p_eval.add_argument("corpus")
    p_config = sub.add_parser("write-log-config"); p_config.add_argument("path")
    args = parser.parse_args()
    if args.command == "snapshot":
        print(parse_power_log(args.power_log).to_json())
    elif args.command == "replay-evaluate":
        print(json.dumps(evaluate(args.corpus), indent=2))
    else:
        print(write_log_config(args.path))
