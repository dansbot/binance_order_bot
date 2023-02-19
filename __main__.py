import argparse
import os

from bin.argparser import parse_args
from bin.logger import setup_logger


def configure(args: argparse.Namespace):
    if args.training:
        os.environ.setdefault("WAIT_UNTIL_FILLED_POLL_TIME", "0.005")
        os.environ.setdefault("TRADING_STOP_LOSS_POLL_TIME", "0.005")
    setup_logger(
        log_level=args.log_level,
        log_file=args.log_file
    )


def main():
    import bin.sw_1 as sw_1
    sw_1.run()
    return


if __name__ == "__main__":
    configure(parse_args())
    main()
