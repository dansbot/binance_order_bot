import logging
import os

HOSTNAME = os.environ.get('HOSTNAME', os.environ.get('USERNAME'))

log = logging.getLogger()
LOG_FORMATTER = logging.Formatter(f'%(asctime)s\t{HOSTNAME}\t%(filename)s:%(lineno)d\t%(levelname)s\t%(message)s')
console_handler = logging.StreamHandler()
console_handler.setFormatter(LOG_FORMATTER)
log.addHandler(console_handler)
log.setLevel("DEBUG")


def setup_logger(**kwargs):
    if kwargs.get('log_level'):
        log.setLevel(kwargs.get('log_level'))
    if kwargs.get('log_file'):
        log_file = kwargs.get('log_file')
        os.makedirs(os.path.abspath(os.path.dirname(log_file)), exist_ok=True)
        file_handler = logging.FileHandler(log_file)
        file_handler.setFormatter(LOG_FORMATTER)
        log.addHandler(file_handler)
