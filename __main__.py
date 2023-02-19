import argparse
import os
from logger import setup_logger


def configure(args: argparse.Namespace):
    if args.training:
        os.environ.setdefault("WAIT_UNTIL_FILLED_POLL_TIME", "0.005")
        os.environ.setdefault("TRADING_STOP_LOSS_POLL_TIME", "0.005")
    setup_logger(
        log_level=args.log_level,
        log_file=args.log_file
    )


def main():
    import sw_1
    sw_1.func_1()
    sw_1.func_2()


if __name__ == "__main__":
    # Create an ArgumentParser object
    parser = argparse.ArgumentParser(description='Order Bot.')

    # Add arguments
    parser.add_argument(
        '-trn',
        '--training',
        action="store_true",
        help='Provide for training runs',
    )

    parser.add_argument(
        '-ll',
        '--log_level',
        type=str.upper,
        choices=['CRITICAL', 'FATAL', 'ERROR', 'WARN', 'WARNING', 'INFO', 'DEBUG', 'NOTSET'],
        default="INFO",
        help='Set the logging level. Default = "INFO"',
    )

    parser.add_argument(
        '-lf',
        '--log_file',
        default='logs/log_file.log',
        help='File to store log file.',
    )

    # Parse the arguments
    args = parser.parse_args()
    configure(args)
    main()
