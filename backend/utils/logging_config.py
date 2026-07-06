import logging
from logging.handlers import RotatingFileHandler

LOG_FORMAT = '%(asctime)s:%(levelname)s:%(message)s'
VALID_LOG_LEVELS = ('DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL')


def setup_logging(log_file, level='INFO'):
    level_name = (level or 'INFO').upper()
    if level_name not in VALID_LOG_LEVELS:
        level_name = 'INFO'

    root = logging.getLogger()
    root.setLevel(getattr(logging, level_name))

    for handler in list(root.handlers):
        root.removeHandler(handler)

    handler = RotatingFileHandler(
        log_file,
        maxBytes=5 * 1024 * 1024,
        backupCount=5,
        encoding='utf-8',
    )
    handler.setFormatter(logging.Formatter(LOG_FORMAT))
    root.addHandler(handler)

    console = logging.StreamHandler()
    console.setFormatter(logging.Formatter(LOG_FORMAT))
    root.addHandler(console)


def parse_log_line(line):
    parts = line.split(':', 2)
    if len(parts) < 3:
        return {'level': 'INFO', 'message': line, 'raw': line}
    return {
        'timestamp': parts[0],
        'level': parts[1],
        'message': parts[2],
        'raw': line,
    }


def filter_log_lines(lines, level=None, search=None):
    level = (level or '').upper()
    search = (search or '').strip().lower()
    filtered = []
    for line in lines:
        parsed = parse_log_line(line)
        if level and parsed['level'] != level:
            continue
        if search and search not in line.lower():
            continue
        filtered.append(parsed)
    return filtered
