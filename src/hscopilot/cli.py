from __future__ import annotations

import argparse
import json
from dataclasses import asdict

from .perception.logconfig import write_log_config
from .perception.doctor import discover
from .perception.live import watch_decisions
from .perception.power import parse_power_log
from .replay.evaluate import evaluate
from .render.board import render_board
from .debug_ui import DebugState, serve_debug_ui
from .launcher import launch


def main() -> None:
    parser = argparse.ArgumentParser(prog="hscopilot")
    sub = parser.add_subparsers(dest="command", required=True)
    p_snapshot = sub.add_parser("snapshot"); p_snapshot.add_argument("power_log")
    p_eval = sub.add_parser("replay-evaluate"); p_eval.add_argument("corpus")
    p_config = sub.add_parser("write-log-config"); p_config.add_argument("path"); p_config.add_argument("--dry-run", action="store_true")
    sub.add_parser("doctor")
    p_board = sub.add_parser("board"); p_board.add_argument("power_log"); p_board.add_argument("index", type=int)
    p_watch = sub.add_parser("watch"); p_watch.add_argument("logs_dir"); p_watch.add_argument("--poll-seconds", type=float, default=0.25)
    p_debug = sub.add_parser("debug-ui"); p_debug.add_argument("--power-log"); p_debug.add_argument("--index", type=int, default=0); p_debug.add_argument("--screenshot"); p_debug.add_argument("--host", default="127.0.0.1"); p_debug.add_argument("--port", type=int, default=8765); p_debug.add_argument("--fixture-dir")
    p_launch = sub.add_parser("launch"); p_launch.add_argument("--execute", action="store_true"); p_launch.add_argument("--play-x", type=int); p_launch.add_argument("--play-y", type=int); p_launch.add_argument("--timeout", type=float, default=30.0)
    args = parser.parse_args()
    if args.command == "doctor":
        print(json.dumps(discover(), indent=2, sort_keys=True))
    elif args.command == "snapshot":
        print(json.dumps([game.to_dict() for game in parse_power_log(args.power_log)], indent=2))
    elif args.command == "board":
        print(render_board(parse_power_log(args.power_log)[0], args.index))
    elif args.command == "watch":
        for point in watch_decisions(args.logs_dir, poll_seconds=args.poll_seconds):
            print(json.dumps(point.to_dict(), sort_keys=True), flush=True)
    elif args.command == "debug-ui":
        state = DebugState()
        if args.power_log:
            game = parse_power_log(args.power_log)[0]
            state.update(game.decision_points[args.index], screenshot=args.screenshot)
        elif args.screenshot:
            state.update(screenshot=args.screenshot)
        server = serve_debug_ui(state, host=args.host, port=args.port, fixture_dir=args.fixture_dir)
        print(f"debug UI: http://{args.host}:{server.server_port}", flush=True)
        try:
            server.serve_forever()
        except KeyboardInterrupt:
            server.shutdown()
    elif args.command == "launch":
        print(json.dumps(asdict(launch(dry_run=not args.execute, play_x=args.play_x, play_y=args.play_y, timeout=args.timeout)), indent=2, default=str))
    elif args.command == "replay-evaluate":
        print(json.dumps(evaluate(args.corpus), indent=2))
    else:
        print(write_log_config(args.path, dry_run=args.dry_run))
