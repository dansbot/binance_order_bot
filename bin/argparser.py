import argparse


def parse_args():
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
    return parser.parse_args()

