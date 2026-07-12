import logging
import re
from logging.handlers import RotatingFileHandler

LOG_FORMAT = '%(asctime)s:%(levelname)s:%(message)s'
VALID_LOG_LEVELS = ('DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL')

# asctime itself contains colons, so anchor the split on a known level name.
_LOG_LINE_PATTERN = re.compile(
    r'^(?P<timestamp>.*?):(?P<level>' + '|'.join(VALID_LOG_LEVELS) + r'):(?P<message>.*)$'
)


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
    match = _LOG_LINE_PATTERN.match(line)
    if not match:
        return {'level': 'INFO', 'message': line, 'raw': line}
    return {
        'timestamp': match.group('timestamp'),
        'level': match.group('level'),
        'message': match.group('message'),
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
