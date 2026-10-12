"""Command line: ``python -m ordersync serve`` and ``python -m ordersync forward``."""

import argparse
import os
import sys

from .forwarder import forward_pending
from .server import serve
from .store import EventStore
from .webhooks import WebhookHandler


def main(argv=None):
    parser = argparse.ArgumentParser(prog="ordersync")
    parser.add_argument("--db", default="ordersync.db")
    sub = parser.add_subparsers(dest="command", required=True)
    serve_cmd = sub.add_parser("serve", help="receive webhooks")
    serve_cmd.add_argument("--port", type=int, default=8080)
    sub.add_parser("forward", help="forward stored events to the order API")
    args = parser.parse_args(argv)

    store = EventStore(args.db)
    if args.command == "serve":
        secret = os.environ.get("ORDERSYNC_WEBHOOK_SECRET")
        if not secret:
            sys.exit("ORDERSYNC_WEBHOOK_SECRET is not set")
        serve(WebhookHandler(store, secret), port=args.port)
    elif args.command == "forward":
        print(f"forwarded {forward_pending(store)} event(s)")


if __name__ == "__main__":
    main()
